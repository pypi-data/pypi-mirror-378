from typing import Literal, cast

V1VehicleExportRiskLevel = Literal["", "high", "low", "medium", "very_high", "very_low"]

V1_VEHICLE_EXPORT_RISK_LEVEL_VALUES: set[V1VehicleExportRiskLevel] = {
    "",
    "high",
    "low",
    "medium",
    "very_high",
    "very_low",
}


def check_v1_vehicle_export_risk_level(value: str) -> V1VehicleExportRiskLevel:
    if value in V1_VEHICLE_EXPORT_RISK_LEVEL_VALUES:
        return cast(V1VehicleExportRiskLevel, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {V1_VEHICLE_EXPORT_RISK_LEVEL_VALUES!r}")
