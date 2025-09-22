from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast
from typing import Union

if TYPE_CHECKING:
    from ..models.v1api_info_response_endpoints import V1APIInfoResponseEndpoints
    from ..models.v1api_info_response_rate_limits import V1APIInfoResponseRateLimits
    from ..models.v1api_info_response_data_sources_item import V1APIInfoResponseDataSourcesItem


T = TypeVar("T", bound="V1APIInfoResponse")


@_attrs_define
class V1APIInfoResponse:
    """API information response

    Attributes:
        name (str):
        version (str):
        description (str):
        endpoints (V1APIInfoResponseEndpoints):
        features (list[str]):
        rate_limits (V1APIInfoResponseRateLimits):
        data_sources (list['V1APIInfoResponseDataSourcesItem']):
        status (str):
        support_email (Union[Unset, str]):
        documentation_url (Union[Unset, str]):
        uptime (Union[Unset, str]):
    """

    name: str
    version: str
    description: str
    endpoints: "V1APIInfoResponseEndpoints"
    features: list[str]
    rate_limits: "V1APIInfoResponseRateLimits"
    data_sources: list["V1APIInfoResponseDataSourcesItem"]
    status: str
    support_email: Union[Unset, str] = UNSET
    documentation_url: Union[Unset, str] = UNSET
    uptime: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.v1api_info_response_endpoints import V1APIInfoResponseEndpoints
        from ..models.v1api_info_response_rate_limits import V1APIInfoResponseRateLimits
        from ..models.v1api_info_response_data_sources_item import V1APIInfoResponseDataSourcesItem

        name = self.name

        version = self.version

        description = self.description

        endpoints = self.endpoints.to_dict()

        features = self.features

        rate_limits = self.rate_limits.to_dict()

        data_sources = []
        for data_sources_item_data in self.data_sources:
            data_sources_item = data_sources_item_data.to_dict()
            data_sources.append(data_sources_item)

        status = self.status

        support_email = self.support_email

        documentation_url = self.documentation_url

        uptime = self.uptime

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "version": version,
                "description": description,
                "endpoints": endpoints,
                "features": features,
                "rate_limits": rate_limits,
                "data_sources": data_sources,
                "status": status,
            }
        )
        if support_email is not UNSET:
            field_dict["support_email"] = support_email
        if documentation_url is not UNSET:
            field_dict["documentation_url"] = documentation_url
        if uptime is not UNSET:
            field_dict["uptime"] = uptime

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.v1api_info_response_endpoints import V1APIInfoResponseEndpoints
        from ..models.v1api_info_response_rate_limits import V1APIInfoResponseRateLimits
        from ..models.v1api_info_response_data_sources_item import V1APIInfoResponseDataSourcesItem

        d = dict(src_dict)
        name = d.pop("name")

        version = d.pop("version")

        description = d.pop("description")

        endpoints = V1APIInfoResponseEndpoints.from_dict(d.pop("endpoints"))

        features = cast(list[str], d.pop("features"))

        rate_limits = V1APIInfoResponseRateLimits.from_dict(d.pop("rate_limits"))

        data_sources = []
        _data_sources = d.pop("data_sources")
        for data_sources_item_data in _data_sources:
            data_sources_item = V1APIInfoResponseDataSourcesItem.from_dict(data_sources_item_data)

            data_sources.append(data_sources_item)

        status = d.pop("status")

        support_email = d.pop("support_email", UNSET)

        documentation_url = d.pop("documentation_url", UNSET)

        uptime = d.pop("uptime", UNSET)

        v1api_info_response = cls(
            name=name,
            version=version,
            description=description,
            endpoints=endpoints,
            features=features,
            rate_limits=rate_limits,
            data_sources=data_sources,
            status=status,
            support_email=support_email,
            documentation_url=documentation_url,
            uptime=uptime,
        )

        v1api_info_response.additional_properties = d
        return v1api_info_response

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
