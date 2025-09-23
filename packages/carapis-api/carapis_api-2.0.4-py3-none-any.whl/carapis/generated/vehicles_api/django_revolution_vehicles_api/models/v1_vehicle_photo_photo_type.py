from typing import Literal, cast

V1VehiclePhotoPhotoType = Literal[
    "damage", "dashboard", "document", "engine", "exterior", "interior", "other", "trunk", "wheel"
]

V1_VEHICLE_PHOTO_PHOTO_TYPE_VALUES: set[V1VehiclePhotoPhotoType] = {
    "damage",
    "dashboard",
    "document",
    "engine",
    "exterior",
    "interior",
    "other",
    "trunk",
    "wheel",
}


def check_v1_vehicle_photo_photo_type(value: str) -> V1VehiclePhotoPhotoType:
    if value in V1_VEHICLE_PHOTO_PHOTO_TYPE_VALUES:
        return cast(V1VehiclePhotoPhotoType, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {V1_VEHICLE_PHOTO_PHOTO_TYPE_VALUES!r}")
