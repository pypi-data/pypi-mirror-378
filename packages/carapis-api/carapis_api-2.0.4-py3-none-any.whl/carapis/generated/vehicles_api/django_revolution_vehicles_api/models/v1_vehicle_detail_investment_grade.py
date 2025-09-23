from typing import Literal, cast

V1VehicleDetailInvestmentGrade = Literal["", "A", "A+", "A-", "B", "B+", "B-", "C", "C+", "C-", "D", "F"]

V1_VEHICLE_DETAIL_INVESTMENT_GRADE_VALUES: set[V1VehicleDetailInvestmentGrade] = {
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


def check_v1_vehicle_detail_investment_grade(value: str) -> V1VehicleDetailInvestmentGrade:
    if value in V1_VEHICLE_DETAIL_INVESTMENT_GRADE_VALUES:
        return cast(V1VehicleDetailInvestmentGrade, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {V1_VEHICLE_DETAIL_INVESTMENT_GRADE_VALUES!r}")
