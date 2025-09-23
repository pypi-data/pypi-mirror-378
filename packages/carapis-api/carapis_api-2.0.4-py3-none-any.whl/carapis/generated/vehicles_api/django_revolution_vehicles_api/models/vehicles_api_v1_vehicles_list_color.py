from typing import Literal, cast

VehiclesApiV1VehiclesListColor = Literal[
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

VEHICLES_API_V1_VEHICLES_LIST_COLOR_VALUES: set[VehiclesApiV1VehiclesListColor] = {
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


def check_vehicles_api_v1_vehicles_list_color(value: str) -> VehiclesApiV1VehiclesListColor:
    if value in VEHICLES_API_V1_VEHICLES_LIST_COLOR_VALUES:
        return cast(VehiclesApiV1VehiclesListColor, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {VEHICLES_API_V1_VEHICLES_LIST_COLOR_VALUES!r}")
