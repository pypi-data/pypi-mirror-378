from typing import Literal, cast

VehiclesApiV1VehiclesListRiskLevel = Literal["high", "low", "medium", "very_high", "very_low"]

VEHICLES_API_V1_VEHICLES_LIST_RISK_LEVEL_VALUES: set[VehiclesApiV1VehiclesListRiskLevel] = {
    "high",
    "low",
    "medium",
    "very_high",
    "very_low",
}


def check_vehicles_api_v1_vehicles_list_risk_level(value: str) -> VehiclesApiV1VehiclesListRiskLevel:
    if value in VEHICLES_API_V1_VEHICLES_LIST_RISK_LEVEL_VALUES:
        return cast(VehiclesApiV1VehiclesListRiskLevel, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {VEHICLES_API_V1_VEHICLES_LIST_RISK_LEVEL_VALUES!r}")
