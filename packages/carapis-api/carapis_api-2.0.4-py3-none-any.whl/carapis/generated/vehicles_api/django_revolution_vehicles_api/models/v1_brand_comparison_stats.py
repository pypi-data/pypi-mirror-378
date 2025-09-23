from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from typing import cast

if TYPE_CHECKING:
    from ..models.v1_brand_comparison_stats_brands_item import V1BrandComparisonStatsBrandsItem


T = TypeVar("T", bound="V1BrandComparisonStats")


@_attrs_define
class V1BrandComparisonStats:
    """Brand comparison statistics serializer

    Attributes:
        brands (list['V1BrandComparisonStatsBrandsItem']):
        comparison_count (int):
    """

    brands: list["V1BrandComparisonStatsBrandsItem"]
    comparison_count: int
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.v1_brand_comparison_stats_brands_item import V1BrandComparisonStatsBrandsItem

        brands = []
        for brands_item_data in self.brands:
            brands_item = brands_item_data.to_dict()
            brands.append(brands_item)

        comparison_count = self.comparison_count

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "brands": brands,
                "comparison_count": comparison_count,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.v1_brand_comparison_stats_brands_item import V1BrandComparisonStatsBrandsItem

        d = dict(src_dict)
        brands = []
        _brands = d.pop("brands")
        for brands_item_data in _brands:
            brands_item = V1BrandComparisonStatsBrandsItem.from_dict(brands_item_data)

            brands.append(brands_item)

        comparison_count = d.pop("comparison_count")

        v1_brand_comparison_stats = cls(
            brands=brands,
            comparison_count=comparison_count,
        )

        v1_brand_comparison_stats.additional_properties = d
        return v1_brand_comparison_stats

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
