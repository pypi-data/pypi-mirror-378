from typing import Literal, cast

V1VehicleListBodyType = Literal[
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

V1_VEHICLE_LIST_BODY_TYPE_VALUES: set[V1VehicleListBodyType] = {
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


def check_v1_vehicle_list_body_type(value: str) -> V1VehicleListBodyType:
    if value in V1_VEHICLE_LIST_BODY_TYPE_VALUES:
        return cast(V1VehicleListBodyType, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {V1_VEHICLE_LIST_BODY_TYPE_VALUES!r}")
