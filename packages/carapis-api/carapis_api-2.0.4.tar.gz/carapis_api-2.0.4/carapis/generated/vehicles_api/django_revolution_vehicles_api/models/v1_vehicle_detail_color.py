from typing import Literal, cast

V1VehicleDetailColor = Literal[
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

V1_VEHICLE_DETAIL_COLOR_VALUES: set[V1VehicleDetailColor] = {
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


def check_v1_vehicle_detail_color(value: str) -> V1VehicleDetailColor:
    if value in V1_VEHICLE_DETAIL_COLOR_VALUES:
        return cast(V1VehicleDetailColor, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {V1_VEHICLE_DETAIL_COLOR_VALUES!r}")
