from typing import Literal, cast

VehiclesApiV1VehiclesListColorsItem = Literal[
    "beige",
    "black",
    "blue",
    "brown",
    "gold",
    "gray",
    "green",
    "orange",
    "other",
    "pink",
    "purple",
    "red",
    "silver",
    "unknown",
    "white",
    "yellow",
]

VEHICLES_API_V1_VEHICLES_LIST_COLORS_ITEM_VALUES: set[VehiclesApiV1VehiclesListColorsItem] = {
    "beige",
    "black",
    "blue",
    "brown",
    "gold",
    "gray",
    "green",
    "orange",
    "other",
    "pink",
    "purple",
    "red",
    "silver",
    "unknown",
    "white",
    "yellow",
}


def check_vehicles_api_v1_vehicles_list_colors_item(value: str) -> VehiclesApiV1VehiclesListColorsItem:
    if value in VEHICLES_API_V1_VEHICLES_LIST_COLORS_ITEM_VALUES:
        return cast(VehiclesApiV1VehiclesListColorsItem, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {VEHICLES_API_V1_VEHICLES_LIST_COLORS_ITEM_VALUES!r}")
