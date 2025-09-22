from typing import Literal, cast

VehiclesApiV1VehiclesListTransmissionsItem = Literal["auto", "cvt", "dct", "manual", "other", "semi_auto", "unknown"]

VEHICLES_API_V1_VEHICLES_LIST_TRANSMISSIONS_ITEM_VALUES: set[VehiclesApiV1VehiclesListTransmissionsItem] = {
    "auto",
    "cvt",
    "dct",
    "manual",
    "other",
    "semi_auto",
    "unknown",
}


def check_vehicles_api_v1_vehicles_list_transmissions_item(value: str) -> VehiclesApiV1VehiclesListTransmissionsItem:
    if value in VEHICLES_API_V1_VEHICLES_LIST_TRANSMISSIONS_ITEM_VALUES:
        return cast(VehiclesApiV1VehiclesListTransmissionsItem, value)
    raise TypeError(
        f"Unexpected value {value!r}. Expected one of {VEHICLES_API_V1_VEHICLES_LIST_TRANSMISSIONS_ITEM_VALUES!r}"
    )
