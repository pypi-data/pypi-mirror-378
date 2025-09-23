from typing import Literal, cast

V1VehicleListColor = Literal[
    "",
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

V1_VEHICLE_LIST_COLOR_VALUES: set[V1VehicleListColor] = {
    "",
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


def check_v1_vehicle_list_color(value: str) -> V1VehicleListColor:
    if value in V1_VEHICLE_LIST_COLOR_VALUES:
        return cast(V1VehicleListColor, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {V1_VEHICLE_LIST_COLOR_VALUES!r}")
