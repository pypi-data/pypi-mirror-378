from typing import Literal, cast

VehiclesApiV1VehiclesListFuelTypesItem = Literal[
    "cng", "diesel", "electric", "gasoline", "hybrid", "hydrogen", "lpg", "other", "plug_hybrid", "unknown"
]

VEHICLES_API_V1_VEHICLES_LIST_FUEL_TYPES_ITEM_VALUES: set[VehiclesApiV1VehiclesListFuelTypesItem] = {
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


def check_vehicles_api_v1_vehicles_list_fuel_types_item(value: str) -> VehiclesApiV1VehiclesListFuelTypesItem:
    if value in VEHICLES_API_V1_VEHICLES_LIST_FUEL_TYPES_ITEM_VALUES:
        return cast(VehiclesApiV1VehiclesListFuelTypesItem, value)
    raise TypeError(
        f"Unexpected value {value!r}. Expected one of {VEHICLES_API_V1_VEHICLES_LIST_FUEL_TYPES_ITEM_VALUES!r}"
    )
