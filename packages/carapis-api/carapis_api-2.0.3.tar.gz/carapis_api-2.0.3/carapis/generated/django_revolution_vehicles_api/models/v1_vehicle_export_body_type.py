from typing import Literal, cast

V1VehicleExportBodyType = Literal[
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

V1_VEHICLE_EXPORT_BODY_TYPE_VALUES: set[V1VehicleExportBodyType] = {
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


def check_v1_vehicle_export_body_type(value: str) -> V1VehicleExportBodyType:
    if value in V1_VEHICLE_EXPORT_BODY_TYPE_VALUES:
        return cast(V1VehicleExportBodyType, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {V1_VEHICLE_EXPORT_BODY_TYPE_VALUES!r}")
