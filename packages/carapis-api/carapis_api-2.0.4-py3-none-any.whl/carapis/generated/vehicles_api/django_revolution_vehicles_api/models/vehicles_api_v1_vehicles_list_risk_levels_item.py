from typing import Literal, cast

VehiclesApiV1VehiclesListRiskLevelsItem = Literal["high", "low", "medium", "very_high", "very_low"]

VEHICLES_API_V1_VEHICLES_LIST_RISK_LEVELS_ITEM_VALUES: set[VehiclesApiV1VehiclesListRiskLevelsItem] = {
    "high",
    "low",
    "medium",
    "very_high",
    "very_low",
}


def check_vehicles_api_v1_vehicles_list_risk_levels_item(value: str) -> VehiclesApiV1VehiclesListRiskLevelsItem:
    if value in VEHICLES_API_V1_VEHICLES_LIST_RISK_LEVELS_ITEM_VALUES:
        return cast(VehiclesApiV1VehiclesListRiskLevelsItem, value)
    raise TypeError(
        f"Unexpected value {value!r}. Expected one of {VEHICLES_API_V1_VEHICLES_LIST_RISK_LEVELS_ITEM_VALUES!r}"
    )
