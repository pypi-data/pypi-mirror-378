from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.v1_vehicle_photo_photo_type import check_v1_vehicle_photo_photo_type
from ..models.v1_vehicle_photo_photo_type import V1VehiclePhotoPhotoType
from ..types import UNSET, Unset
from typing import cast
from typing import cast, Union
from typing import Union
from uuid import UUID


T = TypeVar("T", bound="V1VehiclePhoto")


@_attrs_define
class V1VehiclePhoto:
    """Lightweight photo serializer for API responses with image proxy support

    Attributes:
        uuid (UUID): UUID for image proxy URLs
        url (Union[None, str]): Get proxied photo URL
        thumbnail_url (Union[None, str]): Get proxied thumbnail URL
        photo_type (Union[Unset, V1VehiclePhotoPhotoType]): * `exterior` - 🚗 Exterior
            * `interior` - 🪑 Interior
            * `engine` - 🔧 Engine
            * `trunk` - 📦 Trunk
            * `wheel` - ⚙️ Wheel
            * `dashboard` - 📊 Dashboard
            * `damage` - ⚠️ Damage
            * `document` - 📄 Document
            * `other` - ❓ Other
        sequence (Union[Unset, int]): Display order of the photo
        is_main (Union[Unset, bool]):
        width (Union[None, Unset, int]):
        height (Union[None, Unset, int]):
    """

    uuid: UUID
    url: Union[None, str]
    thumbnail_url: Union[None, str]
    photo_type: Union[Unset, V1VehiclePhotoPhotoType] = UNSET
    sequence: Union[Unset, int] = UNSET
    is_main: Union[Unset, bool] = UNSET
    width: Union[None, Unset, int] = UNSET
    height: Union[None, Unset, int] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        uuid = str(self.uuid)

        url: Union[None, str]
        url = self.url

        thumbnail_url: Union[None, str]
        thumbnail_url = self.thumbnail_url

        photo_type: Union[Unset, str] = UNSET
        if not isinstance(self.photo_type, Unset):
            photo_type = self.photo_type

        sequence = self.sequence

        is_main = self.is_main

        width: Union[None, Unset, int]
        if isinstance(self.width, Unset):
            width = UNSET
        else:
            width = self.width

        height: Union[None, Unset, int]
        if isinstance(self.height, Unset):
            height = UNSET
        else:
            height = self.height

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "uuid": uuid,
                "url": url,
                "thumbnail_url": thumbnail_url,
            }
        )
        if photo_type is not UNSET:
            field_dict["photo_type"] = photo_type
        if sequence is not UNSET:
            field_dict["sequence"] = sequence
        if is_main is not UNSET:
            field_dict["is_main"] = is_main
        if width is not UNSET:
            field_dict["width"] = width
        if height is not UNSET:
            field_dict["height"] = height

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        uuid = UUID(d.pop("uuid"))

        def _parse_url(data: object) -> Union[None, str]:
            if data is None:
                return data
            return cast(Union[None, str], data)

        url = _parse_url(d.pop("url"))

        def _parse_thumbnail_url(data: object) -> Union[None, str]:
            if data is None:
                return data
            return cast(Union[None, str], data)

        thumbnail_url = _parse_thumbnail_url(d.pop("thumbnail_url"))

        _photo_type = d.pop("photo_type", UNSET)
        photo_type: Union[Unset, V1VehiclePhotoPhotoType]
        if isinstance(_photo_type, Unset):
            photo_type = UNSET
        else:
            photo_type = check_v1_vehicle_photo_photo_type(_photo_type)

        sequence = d.pop("sequence", UNSET)

        is_main = d.pop("is_main", UNSET)

        def _parse_width(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        width = _parse_width(d.pop("width", UNSET))

        def _parse_height(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        height = _parse_height(d.pop("height", UNSET))

        v1_vehicle_photo = cls(
            uuid=uuid,
            url=url,
            thumbnail_url=thumbnail_url,
            photo_type=photo_type,
            sequence=sequence,
            is_main=is_main,
            width=width,
            height=height,
        )

        v1_vehicle_photo.additional_properties = d
        return v1_vehicle_photo

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
