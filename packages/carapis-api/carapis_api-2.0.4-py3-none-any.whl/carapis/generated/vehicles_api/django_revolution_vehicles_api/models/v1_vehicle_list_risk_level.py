from typing import Literal, cast

V1VehicleListRiskLevel = Literal["", "high", "low", "medium", "very_high", "very_low"]

V1_VEHICLE_LIST_RISK_LEVEL_VALUES: set[V1VehicleListRiskLevel] = {
    "",
    "high",
    "low",
    "medium",
    "very_high",
    "very_low",
}


def check_v1_vehicle_list_risk_level(value: str) -> V1VehicleListRiskLevel:
    if value in V1_VEHICLE_LIST_RISK_LEVEL_VALUES:
        return cast(V1VehicleListRiskLevel, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {V1_VEHICLE_LIST_RISK_LEVEL_VALUES!r}")
