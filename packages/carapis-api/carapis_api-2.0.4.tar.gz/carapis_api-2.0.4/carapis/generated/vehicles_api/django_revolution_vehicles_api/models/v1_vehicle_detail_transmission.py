from typing import Literal, cast

V1VehicleDetailTransmission = Literal["", "auto", "cvt", "dct", "manual", "other", "semi_auto", "unknown"]

V1_VEHICLE_DETAIL_TRANSMISSION_VALUES: set[V1VehicleDetailTransmission] = {
    "",
    "auto",
    "cvt",
    "dct",
    "manual",
    "other",
    "semi_auto",
    "unknown",
}


def check_v1_vehicle_detail_transmission(value: str) -> V1VehicleDetailTransmission:
    if value in V1_VEHICLE_DETAIL_TRANSMISSION_VALUES:
        return cast(V1VehicleDetailTransmission, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {V1_VEHICLE_DETAIL_TRANSMISSION_VALUES!r}")
