"""Tuya PIR motion sensor."""

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
    Groups,
    Scenes,
    LevelControl
)
from zigpy.zcl.clusters.lightlink import LightLink
from zigpy.zcl.clusters.security import IasZone


class TuyaBatteryConfiguration(PowerConfigurationCluster, TuyaLocalCluster):
    """PowerConfiguration cluster for device"""

    BATTERY_SIZES = 0x0031
    BATTERY_QUANTITY = 0x0033

    _CONSTANT_ATTRIBUTES = {
        BATTERY_SIZES: 4,  # AAA
        BATTERY_QUANTITY: 2,
    }


class DoorSensor(CustomDevice):
    """Tuya PIR motion sensor."""

    signature = {
        MODELS_INFO: [("_TZ3000_2mbfxlzr", "TS0203")],
        # endpoints=1 profile=260 device_type=0x0402
        # in_clusters=[0x0000, 0x0001, 0x0003, 0x0500],
        # out_clusters=[0x0003, 0x0004, 0x0005, 0x0006, 0x0008, 0x000a, 0x0019, 0x1000]
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
                    Identify.cluster_id,
                    Groups.cluster_id,
                    Scenes.cluster_id,
                    OnOff.cluster_id,
                    LevelControl.cluster_id,
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
                    IasZone.cluster_id,
                ],
                OUTPUT_CLUSTERS: [
                    Identify.cluster_id,
                    Groups.cluster_id,
                    Scenes.cluster_id,
                    OnOff.cluster_id,
                    LevelControl.cluster_id,
                    Time.cluster_id,
                    Ota.cluster_id,
                    LightLink.cluster_id,
                ],
            }
        }
    }
