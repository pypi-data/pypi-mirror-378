from typing import Literal, cast

V1VehicleDetailRiskLevel = Literal["", "high", "low", "medium", "very_high", "very_low"]

V1_VEHICLE_DETAIL_RISK_LEVEL_VALUES: set[V1VehicleDetailRiskLevel] = {
    "",
    "high",
    "low",
    "medium",
    "very_high",
    "very_low",
}


def check_v1_vehicle_detail_risk_level(value: str) -> V1VehicleDetailRiskLevel:
    if value in V1_VEHICLE_DETAIL_RISK_LEVEL_VALUES:
        return cast(V1VehicleDetailRiskLevel, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {V1_VEHICLE_DETAIL_RISK_LEVEL_VALUES!r}")
