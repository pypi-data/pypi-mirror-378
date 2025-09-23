from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.v1_vehicle_model_primary_body_type import check_v1_vehicle_model_primary_body_type
from ..models.v1_vehicle_model_primary_body_type import V1VehicleModelPrimaryBodyType
from ..types import UNSET, Unset
from dateutil.parser import isoparse
from typing import cast
from typing import Union
import datetime


T = TypeVar("T", bound="V1VehicleModel")


@_attrs_define
class V1VehicleModel:
    """Vehicle model information serializer

    Attributes:
        id (int):
        code (str):
        name (str):
        slug (str):
        brand (int):
        brand_name (str):
        brand_country (str):
        total_vehicles (int):
        vehicle_count (int):
        created_at (datetime.datetime):
        updated_at (datetime.datetime):
        body_type (Union[Unset, V1VehicleModelPrimaryBodyType]): * `sedan` - 🚗 Sedan
            * `hatchback` - 🚙 Hatchback
            * `coupe` - 🏎️ Coupe
            * `convertible` - 🏎️ Convertible
            * `suv` - 🚐 SUV
            * `wagon` - 🚛 Wagon
            * `pickup` - 🛻 Pickup
            * `van` - 🚐 Van
            * `minivan` - 🚌 Minivan
            * `crossover` - 🚙 Crossover
            * `truck` - 🚚 Truck
            * `bus` - 🚌 Bus
            * `other` - ❓ Other
            * `unknown` - ❓ Unknown
        segment (Union[Unset, str]): e.g., Compact, Mid-size, Luxury
    """

    id: int
    code: str
    name: str
    slug: str
    brand: int
    brand_name: str
    brand_country: str
    total_vehicles: int
    vehicle_count: int
    created_at: datetime.datetime
    updated_at: datetime.datetime
    body_type: Union[Unset, V1VehicleModelPrimaryBodyType] = UNSET
    segment: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        code = self.code

        name = self.name

        slug = self.slug

        brand = self.brand

        brand_name = self.brand_name

        brand_country = self.brand_country

        total_vehicles = self.total_vehicles

        vehicle_count = self.vehicle_count

        created_at = self.created_at.isoformat()

        updated_at = self.updated_at.isoformat()

        body_type: Union[Unset, str] = UNSET
        if not isinstance(self.body_type, Unset):
            body_type = self.body_type

        segment = self.segment

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "code": code,
                "name": name,
                "slug": slug,
                "brand": brand,
                "brand_name": brand_name,
                "brand_country": brand_country,
                "total_vehicles": total_vehicles,
                "vehicle_count": vehicle_count,
                "created_at": created_at,
                "updated_at": updated_at,
            }
        )
        if body_type is not UNSET:
            field_dict["body_type"] = body_type
        if segment is not UNSET:
            field_dict["segment"] = segment

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        code = d.pop("code")

        name = d.pop("name")

        slug = d.pop("slug")

        brand = d.pop("brand")

        brand_name = d.pop("brand_name")

        brand_country = d.pop("brand_country")

        total_vehicles = d.pop("total_vehicles")

        vehicle_count = d.pop("vehicle_count")

        created_at = isoparse(d.pop("created_at"))

        updated_at = isoparse(d.pop("updated_at"))

        _body_type = d.pop("body_type", UNSET)
        body_type: Union[Unset, V1VehicleModelPrimaryBodyType]
        if isinstance(_body_type, Unset):
            body_type = UNSET
        else:
            body_type = check_v1_vehicle_model_primary_body_type(_body_type)

        segment = d.pop("segment", UNSET)

        v1_vehicle_model = cls(
            id=id,
            code=code,
            name=name,
            slug=slug,
            brand=brand,
            brand_name=brand_name,
            brand_country=brand_country,
            total_vehicles=total_vehicles,
            vehicle_count=vehicle_count,
            created_at=created_at,
            updated_at=updated_at,
            body_type=body_type,
            segment=segment,
        )

        v1_vehicle_model.additional_properties = d
        return v1_vehicle_model

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
