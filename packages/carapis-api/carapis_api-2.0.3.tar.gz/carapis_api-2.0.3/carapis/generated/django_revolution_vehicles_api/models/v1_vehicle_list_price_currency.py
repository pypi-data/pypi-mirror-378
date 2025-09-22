from typing import Literal, cast

V1VehicleListPriceCurrency = Literal["CNY", "EUR", "JPY", "KRW", "other", "RUB", "USD"]

V1_VEHICLE_LIST_PRICE_CURRENCY_VALUES: set[V1VehicleListPriceCurrency] = {
    "CNY",
    "EUR",
    "JPY",
    "KRW",
    "other",
    "RUB",
    "USD",
}


def check_v1_vehicle_list_price_currency(value: str) -> V1VehicleListPriceCurrency:
    if value in V1_VEHICLE_LIST_PRICE_CURRENCY_VALUES:
        return cast(V1VehicleListPriceCurrency, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {V1_VEHICLE_LIST_PRICE_CURRENCY_VALUES!r}")
