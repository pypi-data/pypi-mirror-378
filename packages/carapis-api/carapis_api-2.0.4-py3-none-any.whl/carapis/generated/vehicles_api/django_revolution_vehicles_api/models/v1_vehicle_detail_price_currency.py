from typing import Literal, cast

V1VehicleDetailPriceCurrency = Literal["CNY", "EUR", "JPY", "KRW", "other", "RUB", "USD"]

V1_VEHICLE_DETAIL_PRICE_CURRENCY_VALUES: set[V1VehicleDetailPriceCurrency] = {
    "CNY",
    "EUR",
    "JPY",
    "KRW",
    "other",
    "RUB",
    "USD",
}


def check_v1_vehicle_detail_price_currency(value: str) -> V1VehicleDetailPriceCurrency:
    if value in V1_VEHICLE_DETAIL_PRICE_CURRENCY_VALUES:
        return cast(V1VehicleDetailPriceCurrency, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {V1_VEHICLE_DETAIL_PRICE_CURRENCY_VALUES!r}")
