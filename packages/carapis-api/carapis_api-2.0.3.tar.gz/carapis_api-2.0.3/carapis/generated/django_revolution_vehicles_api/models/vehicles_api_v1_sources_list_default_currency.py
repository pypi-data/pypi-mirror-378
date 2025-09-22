from typing import Literal, cast

VehiclesApiV1SourcesListDefaultCurrency = Literal["CNY", "EUR", "JPY", "KRW", "other", "RUB", "USD"]

VEHICLES_API_V1_SOURCES_LIST_DEFAULT_CURRENCY_VALUES: set[VehiclesApiV1SourcesListDefaultCurrency] = {
    "CNY",
    "EUR",
    "JPY",
    "KRW",
    "other",
    "RUB",
    "USD",
}


def check_vehicles_api_v1_sources_list_default_currency(value: str) -> VehiclesApiV1SourcesListDefaultCurrency:
    if value in VEHICLES_API_V1_SOURCES_LIST_DEFAULT_CURRENCY_VALUES:
        return cast(VehiclesApiV1SourcesListDefaultCurrency, value)
    raise TypeError(
        f"Unexpected value {value!r}. Expected one of {VEHICLES_API_V1_SOURCES_LIST_DEFAULT_CURRENCY_VALUES!r}"
    )
