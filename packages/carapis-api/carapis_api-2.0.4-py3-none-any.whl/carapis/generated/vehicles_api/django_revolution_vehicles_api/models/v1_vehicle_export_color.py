from typing import Literal, cast

V1VehicleExportColor = Literal[
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

V1_VEHICLE_EXPORT_COLOR_VALUES: set[V1VehicleExportColor] = {
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


def check_v1_vehicle_export_color(value: str) -> V1VehicleExportColor:
    if value in V1_VEHICLE_EXPORT_COLOR_VALUES:
        return cast(V1VehicleExportColor, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {V1_VEHICLE_EXPORT_COLOR_VALUES!r}")
