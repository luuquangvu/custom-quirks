"""Zemismart Power Meter."""
import zigpy.types as t
from zhaquirks import LocalDataCluster
from zhaquirks.const import (
    DEVICE_TYPE,
    ENDPOINTS,
    INPUT_CLUSTERS,
    MODELS_INFO,
    OUTPUT_CLUSTERS,
    PROFILE_ID,
)
from zhaquirks.tuya import TuyaManufClusterAttributes
from zigpy.profiles import zha
from zigpy.quirks import CustomDevice
from zigpy.zcl.clusters.general import Basic, Groups, Ota, Scenes, Time
from zigpy.zcl.clusters.homeautomation import ElectricalMeasurement
from zigpy.zcl.clusters.smartenergy import Metering

"""Zemismart Power Meter Attributes"""
ZEMISMART_TOTAL_ENERGY_ATTR = 0x0201
ZEMISMART_TOTAL_REVERSE_ENERGY_ATTR = 0x0202
ZEMISMART_VCP_ATTR = 0x0006
ZEMISMART_VCP_P2_ATTR = ZEMISMART_VCP_ATTR + 1
ZEMISMART_VCP_P3_ATTR = ZEMISMART_VCP_ATTR + 2


class ZemismartManufCluster(TuyaManufClusterAttributes):
    """Manufacturer Specific Cluster of the Zemismart SPM series Power Meter devices."""

    attributes = {
        ZEMISMART_TOTAL_ENERGY_ATTR: ("energy", t.uint32_t, True),
        ZEMISMART_TOTAL_REVERSE_ENERGY_ATTR: ("reverse_energy", t.uint32_t, True),
        ZEMISMART_VCP_ATTR: ("vcp_raw", t.data64, True),
        ZEMISMART_VCP_P2_ATTR: ("vcp_p2_raw", t.data64, True),
        ZEMISMART_VCP_P3_ATTR: ("vcp_p3_raw", t.data64, True),
    }

    def _update_attribute(self, attrid, value):
        super()._update_attribute(attrid, value)
        if attrid == ZEMISMART_TOTAL_ENERGY_ATTR:
            self.endpoint.smartenergy_metering.energy_deliver_reported(value)
        elif attrid == ZEMISMART_TOTAL_REVERSE_ENERGY_ATTR:
            self.endpoint.smartenergy_metering.energy_receive_reported(value)
        elif attrid == ZEMISMART_VCP_ATTR:
            self.endpoint.electrical_measurement.vcp_reported(value, 0)
        elif attrid == ZEMISMART_VCP_P2_ATTR:
            self.endpoint.electrical_measurement.vcp_reported(value, 1)
        elif attrid == ZEMISMART_VCP_P3_ATTR:
            self.endpoint.electrical_measurement.vcp_reported(value, 2)


class ZemismartElectricalMeasurement(LocalDataCluster, Metering):
    """Custom class for total energy measurement."""

    CURRENT_DELIVERED_ID = 0x0000
    CURRENT_RECEIVED_ID = 0x0001
    POWER_WATT = 0x0000

    """Setting unit of measurement."""
    _CONSTANT_ATTRIBUTES = {
        0x0300: POWER_WATT,
        Metering.AttributeDefs.unit_of_measure.id: 0,  # kWh
        Metering.AttributeDefs.divisor.id: 100,
    }

    def energy_deliver_reported(self, value):
        """Summation Energy Deliver reported."""
        self._update_attribute(self.CURRENT_DELIVERED_ID, value)

    def energy_receive_reported(self, value):
        """Summation Energy Receive reported."""
        self._update_attribute(self.CURRENT_RECEIVED_ID, value)


class ZemismartPowerMeasurement(LocalDataCluster, ElectricalMeasurement):
    """Custom class for power, voltage and current measurement."""

    """Setting unit of measurement."""
    _CONSTANT_ATTRIBUTES = {
        ElectricalMeasurement.AttributeDefs.ac_voltage_multiplier.id: 1,
        ElectricalMeasurement.AttributeDefs.ac_voltage_divisor.id: 10,
        ElectricalMeasurement.AttributeDefs.ac_current_multiplier.id: 1,
        ElectricalMeasurement.AttributeDefs.ac_current_divisor.id: 1000,
    }

    phase_attributes = [
        {  # Phase 1 (X)
            "voltage": ElectricalMeasurement.AttributeDefs.rms_voltage.id,
            "current": ElectricalMeasurement.AttributeDefs.rms_current.id,
            "power": ElectricalMeasurement.AttributeDefs.active_power.id,
        },
        {  # Phase 2 (Y)
            "voltage": ElectricalMeasurement.AttributeDefs.rms_voltage_ph_b.id,
            "current": ElectricalMeasurement.AttributeDefs.rms_current_ph_b.id,
            "power": ElectricalMeasurement.AttributeDefs.active_power_ph_b.id,
        },
        {  # Phase 3 (Z)
            "voltage": ElectricalMeasurement.AttributeDefs.rms_voltage_ph_c.id,
            "current": ElectricalMeasurement.AttributeDefs.rms_current_ph_c.id,
            "power": ElectricalMeasurement.AttributeDefs.active_power_ph_c.id,
        },
    ]

    # Voltage, current, power is delivered in one value
    def vcp_reported(self, value, phase=0):
        if phase < 0 or phase > 2:
            phase = 0

        voltage = int.from_bytes(value[6:8], byteorder="little")
        current = int.from_bytes(value[3:6], byteorder="little")
        power = int.from_bytes(value[0:3], byteorder="little")

        self._update_attribute(self.phase_attributes[phase]["voltage"], voltage)
        self._update_attribute(self.phase_attributes[phase]["current"], current)
        self._update_attribute(self.phase_attributes[phase]["power"], power)


class TuyaZemismartPowerMeter(CustomDevice):
    """Zemismart power meter device."""

    signature = {
        # "node_descriptor": "NodeDescriptor(logical_type=<LogicalType.Router: 1>, complex_descriptor_available=0,
        # user_descriptor_available=0, reserved=0, aps_flags=0, frequency_band=<FrequencyBand.Freq2400MHz: 8>,
        # mac_capability_flags=<MACCapabilityFlags.FullFunctionDevice|MainsPowered|RxOnWhenIdle|AllocateAddress: 142>,
        # manufacturer_code=4098, maximum_buffer_size=82, maximum_incoming_transfer_size=82, server_mask=11264,
        # maximum_outgoing_transfer_size=82, descriptor_capability_field=<DescriptorCapability.NONE: 0>,
        # *allocate_address=True, *is_alternate_pan_coordinator=False, *is_coordinator=False, *is_end_device=False,
        # *is_full_function_device=True, *is_mains_powered=True, *is_receiver_on_when_idle=True, *is_router=True,
        # *is_security_capable=False)",
        # device_version=1
        # input_clusters=[0x0000, 0x0004, 0x0005, 0xef00]
        # output_clusters=[0x000a, 0x0019]
        MODELS_INFO: [
            ("_TZE200_bcusnqt8", "TS0601"),  # SPM01
            ("_TZE204_ves1ycwx", "TS0601"),  # SPM02
            ("_TZE200_ves1ycwx", "TS0601"),  # SPM02
        ],
        ENDPOINTS: {
            # <SimpleDescriptor endpoint=1 profile=260 device_type=51
            # device_version=1
            # input_clusters=[0, 4, 5, 61184]
            # output_clusters=[10, 25]>
            1: {
                PROFILE_ID: zha.PROFILE_ID,
                DEVICE_TYPE: zha.DeviceType.SMART_PLUG,
                INPUT_CLUSTERS: [
                    Basic.cluster_id,
                    Groups.cluster_id,
                    Scenes.cluster_id,
                    TuyaManufClusterAttributes.cluster_id,
                ],
                OUTPUT_CLUSTERS: [Time.cluster_id, Ota.cluster_id],
            }
        },
    }

    replacement = {
        ENDPOINTS: {
            1: {
                PROFILE_ID: zha.PROFILE_ID,
                DEVICE_TYPE: zha.DeviceType.SMART_PLUG,
                INPUT_CLUSTERS: [
                    Basic.cluster_id,
                    Groups.cluster_id,
                    Scenes.cluster_id,
                    ZemismartManufCluster,
                    ZemismartElectricalMeasurement,
                    ZemismartPowerMeasurement,
                ],
                OUTPUT_CLUSTERS: [Time.cluster_id, Ota.cluster_id],
            }
        }
    }
