from typing import Literal, cast

V1VehicleDetailFuelType = Literal[
    "", "cng", "diesel", "electric", "gasoline", "hybrid", "hydrogen", "lpg", "other", "plug_hybrid", "unknown"
]

V1_VEHICLE_DETAIL_FUEL_TYPE_VALUES: set[V1VehicleDetailFuelType] = {
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


def check_v1_vehicle_detail_fuel_type(value: str) -> V1VehicleDetailFuelType:
    if value in V1_VEHICLE_DETAIL_FUEL_TYPE_VALUES:
        return cast(V1VehicleDetailFuelType, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {V1_VEHICLE_DETAIL_FUEL_TYPE_VALUES!r}")
