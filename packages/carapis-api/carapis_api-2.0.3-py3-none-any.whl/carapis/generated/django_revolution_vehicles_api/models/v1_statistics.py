from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from typing import cast

if TYPE_CHECKING:
    from ..models.v1_statistics_overview import V1StatisticsOverview
    from ..models.v1_statistics_top_brands_item import V1StatisticsTopBrandsItem
    from ..models.v1_statistics_quality_distribution import V1StatisticsQualityDistribution
    from ..models.v1_statistics_price_statistics import V1StatisticsPriceStatistics
    from ..models.v1_statistics_top_sources_item import V1StatisticsTopSourcesItem
    from ..models.v1_statistics_year_statistics import V1StatisticsYearStatistics


T = TypeVar("T", bound="V1Statistics")


@_attrs_define
class V1Statistics:
    """Main statistics response serializer

    Attributes:
        overview (V1StatisticsOverview):
        price_statistics (V1StatisticsPriceStatistics):
        year_statistics (V1StatisticsYearStatistics):
        top_brands (list['V1StatisticsTopBrandsItem']):
        top_sources (list['V1StatisticsTopSourcesItem']):
        quality_distribution (V1StatisticsQualityDistribution):
    """

    overview: "V1StatisticsOverview"
    price_statistics: "V1StatisticsPriceStatistics"
    year_statistics: "V1StatisticsYearStatistics"
    top_brands: list["V1StatisticsTopBrandsItem"]
    top_sources: list["V1StatisticsTopSourcesItem"]
    quality_distribution: "V1StatisticsQualityDistribution"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.v1_statistics_overview import V1StatisticsOverview
        from ..models.v1_statistics_top_brands_item import V1StatisticsTopBrandsItem
        from ..models.v1_statistics_quality_distribution import V1StatisticsQualityDistribution
        from ..models.v1_statistics_price_statistics import V1StatisticsPriceStatistics
        from ..models.v1_statistics_top_sources_item import V1StatisticsTopSourcesItem
        from ..models.v1_statistics_year_statistics import V1StatisticsYearStatistics

        overview = self.overview.to_dict()

        price_statistics = self.price_statistics.to_dict()

        year_statistics = self.year_statistics.to_dict()

        top_brands = []
        for top_brands_item_data in self.top_brands:
            top_brands_item = top_brands_item_data.to_dict()
            top_brands.append(top_brands_item)

        top_sources = []
        for top_sources_item_data in self.top_sources:
            top_sources_item = top_sources_item_data.to_dict()
            top_sources.append(top_sources_item)

        quality_distribution = self.quality_distribution.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "overview": overview,
                "price_statistics": price_statistics,
                "year_statistics": year_statistics,
                "top_brands": top_brands,
                "top_sources": top_sources,
                "quality_distribution": quality_distribution,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.v1_statistics_overview import V1StatisticsOverview
        from ..models.v1_statistics_top_brands_item import V1StatisticsTopBrandsItem
        from ..models.v1_statistics_quality_distribution import V1StatisticsQualityDistribution
        from ..models.v1_statistics_price_statistics import V1StatisticsPriceStatistics
        from ..models.v1_statistics_top_sources_item import V1StatisticsTopSourcesItem
        from ..models.v1_statistics_year_statistics import V1StatisticsYearStatistics

        d = dict(src_dict)
        overview = V1StatisticsOverview.from_dict(d.pop("overview"))

        price_statistics = V1StatisticsPriceStatistics.from_dict(d.pop("price_statistics"))

        year_statistics = V1StatisticsYearStatistics.from_dict(d.pop("year_statistics"))

        top_brands = []
        _top_brands = d.pop("top_brands")
        for top_brands_item_data in _top_brands:
            top_brands_item = V1StatisticsTopBrandsItem.from_dict(top_brands_item_data)

            top_brands.append(top_brands_item)

        top_sources = []
        _top_sources = d.pop("top_sources")
        for top_sources_item_data in _top_sources:
            top_sources_item = V1StatisticsTopSourcesItem.from_dict(top_sources_item_data)

            top_sources.append(top_sources_item)

        quality_distribution = V1StatisticsQualityDistribution.from_dict(d.pop("quality_distribution"))

        v1_statistics = cls(
            overview=overview,
            price_statistics=price_statistics,
            year_statistics=year_statistics,
            top_brands=top_brands,
            top_sources=top_sources,
            quality_distribution=quality_distribution,
        )

        v1_statistics.additional_properties = d
        return v1_statistics

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
