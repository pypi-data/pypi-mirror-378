from typing import Literal, cast

V1VehicleExportTransmission = Literal["", "auto", "cvt", "dct", "manual", "other", "semi_auto", "unknown"]

V1_VEHICLE_EXPORT_TRANSMISSION_VALUES: set[V1VehicleExportTransmission] = {
    "",
    "auto",
    "cvt",
    "dct",
    "manual",
    "other",
    "semi_auto",
    "unknown",
}


def check_v1_vehicle_export_transmission(value: str) -> V1VehicleExportTransmission:
    if value in V1_VEHICLE_EXPORT_TRANSMISSION_VALUES:
        return cast(V1VehicleExportTransmission, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {V1_VEHICLE_EXPORT_TRANSMISSION_VALUES!r}")
