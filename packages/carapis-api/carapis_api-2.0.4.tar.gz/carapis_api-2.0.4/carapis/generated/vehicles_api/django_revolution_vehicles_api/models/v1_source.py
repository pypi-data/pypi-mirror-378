from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.v1_source_default_currency import check_v1_source_default_currency
from ..models.v1_source_default_currency import V1SourceDefaultCurrency
from ..types import UNSET, Unset
from dateutil.parser import isoparse
from typing import cast
from typing import cast, Union
from typing import Union
import datetime


T = TypeVar("T", bound="V1Source")


@_attrs_define
class V1Source:
    """Source information serializer

    Attributes:
        id (int):
        code (str): Unique identifier for the parser source (e.g., 'encar', 'che168')
        name (str): Human-readable name (e.g., 'Encar Korea', 'Che168 China')
        country (str): Country where this source operates
        flag_emoji (str):
        total_vehicles (int): Total number of vehicles from this source
        active_vehicles (int): Number of currently active vehicles
        last_parsed_at (Union[None, datetime.datetime]):
        created_at (datetime.datetime):
        updated_at (datetime.datetime):
        website_url (Union[Unset, str]): Main website URL of the source
        currency (Union[Unset, V1SourceDefaultCurrency]): * `KRW` - ₩ Korean Won
            * `USD` - $ US Dollar
            * `JPY` - ¥ Japanese Yen
            * `EUR` - € Euro
            * `CNY` - ¥ Chinese Yuan
            * `RUB` - ₽ Russian Ruble
            * `other` - Other
        timezone (Union[Unset, str]):
    """

    id: int
    code: str
    name: str
    country: str
    flag_emoji: str
    total_vehicles: int
    active_vehicles: int
    last_parsed_at: Union[None, datetime.datetime]
    created_at: datetime.datetime
    updated_at: datetime.datetime
    website_url: Union[Unset, str] = UNSET
    currency: Union[Unset, V1SourceDefaultCurrency] = UNSET
    timezone: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        code = self.code

        name = self.name

        country = self.country

        flag_emoji = self.flag_emoji

        total_vehicles = self.total_vehicles

        active_vehicles = self.active_vehicles

        last_parsed_at: Union[None, str]
        if isinstance(self.last_parsed_at, datetime.datetime):
            last_parsed_at = self.last_parsed_at.isoformat()
        else:
            last_parsed_at = self.last_parsed_at

        created_at = self.created_at.isoformat()

        updated_at = self.updated_at.isoformat()

        website_url = self.website_url

        currency: Union[Unset, str] = UNSET
        if not isinstance(self.currency, Unset):
            currency = self.currency

        timezone = self.timezone

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "code": code,
                "name": name,
                "country": country,
                "flag_emoji": flag_emoji,
                "total_vehicles": total_vehicles,
                "active_vehicles": active_vehicles,
                "last_parsed_at": last_parsed_at,
                "created_at": created_at,
                "updated_at": updated_at,
            }
        )
        if website_url is not UNSET:
            field_dict["website_url"] = website_url
        if currency is not UNSET:
            field_dict["currency"] = currency
        if timezone is not UNSET:
            field_dict["timezone"] = timezone

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        code = d.pop("code")

        name = d.pop("name")

        country = d.pop("country")

        flag_emoji = d.pop("flag_emoji")

        total_vehicles = d.pop("total_vehicles")

        active_vehicles = d.pop("active_vehicles")

        def _parse_last_parsed_at(data: object) -> Union[None, datetime.datetime]:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                last_parsed_at_type_0 = isoparse(data)

                return last_parsed_at_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, datetime.datetime], data)

        last_parsed_at = _parse_last_parsed_at(d.pop("last_parsed_at"))

        created_at = isoparse(d.pop("created_at"))

        updated_at = isoparse(d.pop("updated_at"))

        website_url = d.pop("website_url", UNSET)

        _currency = d.pop("currency", UNSET)
        currency: Union[Unset, V1SourceDefaultCurrency]
        if isinstance(_currency, Unset):
            currency = UNSET
        else:
            currency = check_v1_source_default_currency(_currency)

        timezone = d.pop("timezone", UNSET)

        v1_source = cls(
            id=id,
            code=code,
            name=name,
            country=country,
            flag_emoji=flag_emoji,
            total_vehicles=total_vehicles,
            active_vehicles=active_vehicles,
            last_parsed_at=last_parsed_at,
            created_at=created_at,
            updated_at=updated_at,
            website_url=website_url,
            currency=currency,
            timezone=timezone,
        )

        v1_source.additional_properties = d
        return v1_source

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
