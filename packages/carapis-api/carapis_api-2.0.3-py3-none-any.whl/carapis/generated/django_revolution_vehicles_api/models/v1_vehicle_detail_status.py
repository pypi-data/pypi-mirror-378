from typing import Literal, cast

V1VehicleDetailStatus = Literal["active", "inactive", "reserved", "sold"]

V1_VEHICLE_DETAIL_STATUS_VALUES: set[V1VehicleDetailStatus] = {
    "active",
    "inactive",
    "reserved",
    "sold",
}


def check_v1_vehicle_detail_status(value: str) -> V1VehicleDetailStatus:
    if value in V1_VEHICLE_DETAIL_STATUS_VALUES:
        return cast(V1VehicleDetailStatus, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {V1_VEHICLE_DETAIL_STATUS_VALUES!r}")
