from typing import Literal, cast

VehiclesApiV1VehiclesListTransmission = Literal["auto", "cvt", "dct", "manual", "other", "semi_auto", "unknown"]

VEHICLES_API_V1_VEHICLES_LIST_TRANSMISSION_VALUES: set[VehiclesApiV1VehiclesListTransmission] = {
    "auto",
    "cvt",
    "dct",
    "manual",
    "other",
    "semi_auto",
    "unknown",
}


def check_vehicles_api_v1_vehicles_list_transmission(value: str) -> VehiclesApiV1VehiclesListTransmission:
    if value in VEHICLES_API_V1_VEHICLES_LIST_TRANSMISSION_VALUES:
        return cast(VehiclesApiV1VehiclesListTransmission, value)
    raise TypeError(
        f"Unexpected value {value!r}. Expected one of {VEHICLES_API_V1_VEHICLES_LIST_TRANSMISSION_VALUES!r}"
    )
