from typing import Literal, cast

V1VehicleDetailBodyType = Literal[
    "",
    "bus",
    "convertible",
    "coupe",
    "crossover",
    "hatchback",
    "minivan",
    "other",
    "pickup",
    "sedan",
    "suv",
    "truck",
    "unknown",
    "van",
    "wagon",
]

V1_VEHICLE_DETAIL_BODY_TYPE_VALUES: set[V1VehicleDetailBodyType] = {
    "",
    "bus",
    "convertible",
    "coupe",
    "crossover",
    "hatchback",
    "minivan",
    "other",
    "pickup",
    "sedan",
    "suv",
    "truck",
    "unknown",
    "van",
    "wagon",
}


def check_v1_vehicle_detail_body_type(value: str) -> V1VehicleDetailBodyType:
    if value in V1_VEHICLE_DETAIL_BODY_TYPE_VALUES:
        return cast(V1VehicleDetailBodyType, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {V1_VEHICLE_DETAIL_BODY_TYPE_VALUES!r}")
