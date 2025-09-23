from typing import Literal, cast

V1VehicleListTransmission = Literal["", "auto", "cvt", "dct", "manual", "other", "semi_auto", "unknown"]

V1_VEHICLE_LIST_TRANSMISSION_VALUES: set[V1VehicleListTransmission] = {
    "",
    "auto",
    "cvt",
    "dct",
    "manual",
    "other",
    "semi_auto",
    "unknown",
}


def check_v1_vehicle_list_transmission(value: str) -> V1VehicleListTransmission:
    if value in V1_VEHICLE_LIST_TRANSMISSION_VALUES:
        return cast(V1VehicleListTransmission, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {V1_VEHICLE_LIST_TRANSMISSION_VALUES!r}")
