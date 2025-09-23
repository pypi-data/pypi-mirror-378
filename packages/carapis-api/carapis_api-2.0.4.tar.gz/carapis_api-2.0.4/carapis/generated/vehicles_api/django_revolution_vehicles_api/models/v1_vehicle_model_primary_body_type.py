from typing import Literal, cast

V1VehicleModelPrimaryBodyType = Literal[
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

V1_VEHICLE_MODEL_PRIMARY_BODY_TYPE_VALUES: set[V1VehicleModelPrimaryBodyType] = {
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


def check_v1_vehicle_model_primary_body_type(value: str) -> V1VehicleModelPrimaryBodyType:
    if value in V1_VEHICLE_MODEL_PRIMARY_BODY_TYPE_VALUES:
        return cast(V1VehicleModelPrimaryBodyType, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {V1_VEHICLE_MODEL_PRIMARY_BODY_TYPE_VALUES!r}")
