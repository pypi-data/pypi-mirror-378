from typing import Literal, cast

V1VehicleExportStatus = Literal["active", "inactive", "reserved", "sold"]

V1_VEHICLE_EXPORT_STATUS_VALUES: set[V1VehicleExportStatus] = {
    "active",
    "inactive",
    "reserved",
    "sold",
}


def check_v1_vehicle_export_status(value: str) -> V1VehicleExportStatus:
    if value in V1_VEHICLE_EXPORT_STATUS_VALUES:
        return cast(V1VehicleExportStatus, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {V1_VEHICLE_EXPORT_STATUS_VALUES!r}")
