from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from dateutil.parser import isoparse
from typing import cast
from typing import Union
import datetime


T = TypeVar("T", bound="V1Brand")


@_attrs_define
class V1Brand:
    """Brand information serializer

    Attributes:
        id (int):
        code (str):
        name (str):
        slug (str):
        total_models (int):
        total_vehicles (int):
        vehicle_count (int):
        created_at (datetime.datetime):
        updated_at (datetime.datetime):
        country_origin (Union[Unset, str]):
        logo_url (Union[Unset, str]):
    """

    id: int
    code: str
    name: str
    slug: str
    total_models: int
    total_vehicles: int
    vehicle_count: int
    created_at: datetime.datetime
    updated_at: datetime.datetime
    country_origin: Union[Unset, str] = UNSET
    logo_url: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        code = self.code

        name = self.name

        slug = self.slug

        total_models = self.total_models

        total_vehicles = self.total_vehicles

        vehicle_count = self.vehicle_count

        created_at = self.created_at.isoformat()

        updated_at = self.updated_at.isoformat()

        country_origin = self.country_origin

        logo_url = self.logo_url

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "code": code,
                "name": name,
                "slug": slug,
                "total_models": total_models,
                "total_vehicles": total_vehicles,
                "vehicle_count": vehicle_count,
                "created_at": created_at,
                "updated_at": updated_at,
            }
        )
        if country_origin is not UNSET:
            field_dict["country_origin"] = country_origin
        if logo_url is not UNSET:
            field_dict["logo_url"] = logo_url

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        code = d.pop("code")

        name = d.pop("name")

        slug = d.pop("slug")

        total_models = d.pop("total_models")

        total_vehicles = d.pop("total_vehicles")

        vehicle_count = d.pop("vehicle_count")

        created_at = isoparse(d.pop("created_at"))

        updated_at = isoparse(d.pop("updated_at"))

        country_origin = d.pop("country_origin", UNSET)

        logo_url = d.pop("logo_url", UNSET)

        v1_brand = cls(
            id=id,
            code=code,
            name=name,
            slug=slug,
            total_models=total_models,
            total_vehicles=total_vehicles,
            vehicle_count=vehicle_count,
            created_at=created_at,
            updated_at=updated_at,
            country_origin=country_origin,
            logo_url=logo_url,
        )

        v1_brand.additional_properties = d
        return v1_brand

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
