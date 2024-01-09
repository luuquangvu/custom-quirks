"""Tuya PIR motion sensor."""

import zigpy.types as t
from zhaquirks import PowerConfigurationCluster
from zhaquirks.const import (
    DEVICE_TYPE,
    ENDPOINTS,
    INPUT_CLUSTERS,
    MODELS_INFO,
    OUTPUT_CLUSTERS,
    PROFILE_ID,
)
from zhaquirks.tuya import TuyaLocalCluster
from zigpy.profiles import zha
from zigpy.quirks import CustomDevice
from zigpy.zcl.clusters.general import (
    Basic,
    Identify,
    OnOff,
    Ota,
    PowerConfiguration,
    Time,
)
from zigpy.zcl.clusters.lightlink import LightLink
from zigpy.zcl.clusters.security import IasZone


class SensitivityLevel(t.enum8):
    """Sensitivity level enum."""

    LOW = 0x00
    MEDIUM = 0x01
    HIGH = 0x02


class OnTimeValues(t.enum8):
    """Sensitivity level enum."""

    SEC_30 = 0x00
    SEC_60 = 0x01
    SEC_120 = 0x02


class PirSensor(IasZone):
    """IasZone with extra attributes."""

    attributes = IasZone.attributes.copy()
    # Wrap `current_zone_sensitivity_level` posible values
    attributes.update({0x0013: ("current_zone_sensitivity_level", SensitivityLevel)})
    attributes.update({0xf001: ("on_time", OnTimeValues)})


class TuyaBatteryConfiguration(PowerConfigurationCluster, TuyaLocalCluster):
    """PowerConfiguration cluster for device"""

    BATTERY_SIZES = 0x0031
    BATTERY_QUANTITY = 0x0033

    _CONSTANT_ATTRIBUTES = {
        BATTERY_SIZES: 4,  # AAA
        BATTERY_QUANTITY: 3,
    }


class PirMotion(CustomDevice):
    """Tuya PIR motion sensor."""

    signature = {
        MODELS_INFO: [("_TZ3000_otvn3lne", "TS0202")],
        # endpoints=1 profile=260 device_type=0x0402
        # in_clusters=[0x0000, 0x0001, 0x0003, 0x0500],
        # out_clusters=[0x0006, 0x000a, 0x0019, 0x1000]
        ENDPOINTS: {
            1: {
                PROFILE_ID: zha.PROFILE_ID,
                DEVICE_TYPE: zha.DeviceType.IAS_ZONE,
                INPUT_CLUSTERS: [
                    Basic.cluster_id,
                    Identify.cluster_id,
                    PowerConfiguration.cluster_id,
                    IasZone.cluster_id,
                ],
                OUTPUT_CLUSTERS: [
                    OnOff.cluster_id,
                    Time.cluster_id,
                    Ota.cluster_id,
                    LightLink.cluster_id,
                ],
            }
        },
    }

    replacement = {
        ENDPOINTS: {
            1: {
                PROFILE_ID: zha.PROFILE_ID,
                DEVICE_TYPE: zha.DeviceType.IAS_ZONE,
                INPUT_CLUSTERS: [
                    Basic.cluster_id,
                    Identify.cluster_id,
                    TuyaBatteryConfiguration,
                    PirSensor,
                ],
                OUTPUT_CLUSTERS: [
                    OnOff.cluster_id,
                    Time.cluster_id,
                    Ota.cluster_id,
                    LightLink.cluster_id,
                ],
            }
        }
    }
