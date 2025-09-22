from typing import Literal, cast

V1SourceDefaultCurrency = Literal["CNY", "EUR", "JPY", "KRW", "other", "RUB", "USD"]

V1_SOURCE_DEFAULT_CURRENCY_VALUES: set[V1SourceDefaultCurrency] = {
    "CNY",
    "EUR",
    "JPY",
    "KRW",
    "other",
    "RUB",
    "USD",
}


def check_v1_source_default_currency(value: str) -> V1SourceDefaultCurrency:
    if value in V1_SOURCE_DEFAULT_CURRENCY_VALUES:
        return cast(V1SourceDefaultCurrency, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {V1_SOURCE_DEFAULT_CURRENCY_VALUES!r}")
