from typing import Literal, cast

VehiclesApiV1VehiclesListBodyType = Literal[
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

VEHICLES_API_V1_VEHICLES_LIST_BODY_TYPE_VALUES: set[VehiclesApiV1VehiclesListBodyType] = {
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


def check_vehicles_api_v1_vehicles_list_body_type(value: str) -> VehiclesApiV1VehiclesListBodyType:
    if value in VEHICLES_API_V1_VEHICLES_LIST_BODY_TYPE_VALUES:
        return cast(VehiclesApiV1VehiclesListBodyType, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {VEHICLES_API_V1_VEHICLES_LIST_BODY_TYPE_VALUES!r}")
