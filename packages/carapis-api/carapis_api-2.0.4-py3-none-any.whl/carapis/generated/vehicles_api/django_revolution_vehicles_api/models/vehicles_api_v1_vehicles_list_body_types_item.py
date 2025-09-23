from typing import Literal, cast

VehiclesApiV1VehiclesListBodyTypesItem = Literal[
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

VEHICLES_API_V1_VEHICLES_LIST_BODY_TYPES_ITEM_VALUES: set[VehiclesApiV1VehiclesListBodyTypesItem] = {
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


def check_vehicles_api_v1_vehicles_list_body_types_item(value: str) -> VehiclesApiV1VehiclesListBodyTypesItem:
    if value in VEHICLES_API_V1_VEHICLES_LIST_BODY_TYPES_ITEM_VALUES:
        return cast(VehiclesApiV1VehiclesListBodyTypesItem, value)
    raise TypeError(
        f"Unexpected value {value!r}. Expected one of {VEHICLES_API_V1_VEHICLES_LIST_BODY_TYPES_ITEM_VALUES!r}"
    )
