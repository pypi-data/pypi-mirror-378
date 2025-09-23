from typing import Literal, cast

V1VehicleListInvestmentGrade = Literal["", "A", "A+", "A-", "B", "B+", "B-", "C", "C+", "C-", "D", "F"]

V1_VEHICLE_LIST_INVESTMENT_GRADE_VALUES: set[V1VehicleListInvestmentGrade] = {
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


def check_v1_vehicle_list_investment_grade(value: str) -> V1VehicleListInvestmentGrade:
    if value in V1_VEHICLE_LIST_INVESTMENT_GRADE_VALUES:
        return cast(V1VehicleListInvestmentGrade, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {V1_VEHICLE_LIST_INVESTMENT_GRADE_VALUES!r}")
