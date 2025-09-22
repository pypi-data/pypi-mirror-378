from typing import Literal, cast

V1VehicleListFuelType = Literal[
    "", "cng", "diesel", "electric", "gasoline", "hybrid", "hydrogen", "lpg", "other", "plug_hybrid", "unknown"
]

V1_VEHICLE_LIST_FUEL_TYPE_VALUES: set[V1VehicleListFuelType] = {
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


def check_v1_vehicle_list_fuel_type(value: str) -> V1VehicleListFuelType:
    if value in V1_VEHICLE_LIST_FUEL_TYPE_VALUES:
        return cast(V1VehicleListFuelType, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {V1_VEHICLE_LIST_FUEL_TYPE_VALUES!r}")
