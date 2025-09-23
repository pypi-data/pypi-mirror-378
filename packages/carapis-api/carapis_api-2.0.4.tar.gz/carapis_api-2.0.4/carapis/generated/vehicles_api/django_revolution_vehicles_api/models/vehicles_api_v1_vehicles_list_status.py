from typing import Literal, cast

VehiclesApiV1VehiclesListStatus = Literal["active", "inactive", "reserved", "sold"]

VEHICLES_API_V1_VEHICLES_LIST_STATUS_VALUES: set[VehiclesApiV1VehiclesListStatus] = {
    "active",
    "inactive",
    "reserved",
    "sold",
}


def check_vehicles_api_v1_vehicles_list_status(value: str) -> VehiclesApiV1VehiclesListStatus:
    if value in VEHICLES_API_V1_VEHICLES_LIST_STATUS_VALUES:
        return cast(VehiclesApiV1VehiclesListStatus, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {VEHICLES_API_V1_VEHICLES_LIST_STATUS_VALUES!r}")
