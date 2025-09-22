from typing import Literal, cast

VehiclesApiV1VehiclesListInvestmentGradesItem = Literal["A", "A+", "A-", "B", "B+", "B-", "C", "C+", "C-", "D", "F"]

VEHICLES_API_V1_VEHICLES_LIST_INVESTMENT_GRADES_ITEM_VALUES: set[VehiclesApiV1VehiclesListInvestmentGradesItem] = {
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


def check_vehicles_api_v1_vehicles_list_investment_grades_item(
    value: str,
) -> VehiclesApiV1VehiclesListInvestmentGradesItem:
    if value in VEHICLES_API_V1_VEHICLES_LIST_INVESTMENT_GRADES_ITEM_VALUES:
        return cast(VehiclesApiV1VehiclesListInvestmentGradesItem, value)
    raise TypeError(
        f"Unexpected value {value!r}. Expected one of {VEHICLES_API_V1_VEHICLES_LIST_INVESTMENT_GRADES_ITEM_VALUES!r}"
    )
