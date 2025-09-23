from typing import Literal, cast

V1VehicleExportPriceCurrency = Literal["CNY", "EUR", "JPY", "KRW", "other", "RUB", "USD"]

V1_VEHICLE_EXPORT_PRICE_CURRENCY_VALUES: set[V1VehicleExportPriceCurrency] = {
    "CNY",
    "EUR",
    "JPY",
    "KRW",
    "other",
    "RUB",
    "USD",
}


def check_v1_vehicle_export_price_currency(value: str) -> V1VehicleExportPriceCurrency:
    if value in V1_VEHICLE_EXPORT_PRICE_CURRENCY_VALUES:
        return cast(V1VehicleExportPriceCurrency, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {V1_VEHICLE_EXPORT_PRICE_CURRENCY_VALUES!r}")
