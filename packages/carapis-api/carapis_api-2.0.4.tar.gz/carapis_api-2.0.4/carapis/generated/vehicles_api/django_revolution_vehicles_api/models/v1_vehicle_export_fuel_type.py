from typing import Literal, cast

V1VehicleExportFuelType = Literal[
    "", "cng", "diesel", "electric", "gasoline", "hybrid", "hydrogen", "lpg", "other", "plug_hybrid", "unknown"
]

V1_VEHICLE_EXPORT_FUEL_TYPE_VALUES: set[V1VehicleExportFuelType] = {
    "",
    "cng",
    "diesel",
    "electric",
    "gasoline",
    "hybrid",
    "hydrogen",
    "lpg",
    "other",
    "plug_hybrid",
    "unknown",
}


def check_v1_vehicle_export_fuel_type(value: str) -> V1VehicleExportFuelType:
    if value in V1_VEHICLE_EXPORT_FUEL_TYPE_VALUES:
        return cast(V1VehicleExportFuelType, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {V1_VEHICLE_EXPORT_FUEL_TYPE_VALUES!r}")
