from typing import Literal, cast

V1VehicleExportInvestmentGrade = Literal["", "A", "A+", "A-", "B", "B+", "B-", "C", "C+", "C-", "D", "F"]

V1_VEHICLE_EXPORT_INVESTMENT_GRADE_VALUES: set[V1VehicleExportInvestmentGrade] = {
    "",
    "A",
    "A+",
    "A-",
    "B",
    "B+",
    "B-",
    "C",
    "C+",
    "C-",
    "D",
    "F",
}


def check_v1_vehicle_export_investment_grade(value: str) -> V1VehicleExportInvestmentGrade:
    if value in V1_VEHICLE_EXPORT_INVESTMENT_GRADE_VALUES:
        return cast(V1VehicleExportInvestmentGrade, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {V1_VEHICLE_EXPORT_INVESTMENT_GRADE_VALUES!r}")
