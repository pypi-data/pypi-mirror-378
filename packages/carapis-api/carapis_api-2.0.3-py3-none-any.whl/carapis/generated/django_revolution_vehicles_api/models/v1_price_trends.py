from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from typing import cast

if TYPE_CHECKING:
    from ..models.v1_price_trends_by_fuel_type import V1PriceTrendsByFuelType
    from ..models.v1_price_trends_by_year_range import V1PriceTrendsByYearRange
    from ..models.v1_price_trends_by_body_type import V1PriceTrendsByBodyType
    from ..models.v1_price_trends_analysis import V1PriceTrendsAnalysis


T = TypeVar("T", bound="V1PriceTrends")


@_attrs_define
class V1PriceTrends:
    """Price trends analysis serializer

    Attributes:
        by_fuel_type (V1PriceTrendsByFuelType):
        by_body_type (V1PriceTrendsByBodyType):
        by_year_range (V1PriceTrendsByYearRange):
        analysis (V1PriceTrendsAnalysis):
    """

    by_fuel_type: "V1PriceTrendsByFuelType"
    by_body_type: "V1PriceTrendsByBodyType"
    by_year_range: "V1PriceTrendsByYearRange"
    analysis: "V1PriceTrendsAnalysis"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.v1_price_trends_by_fuel_type import V1PriceTrendsByFuelType
        from ..models.v1_price_trends_by_year_range import V1PriceTrendsByYearRange
        from ..models.v1_price_trends_by_body_type import V1PriceTrendsByBodyType
        from ..models.v1_price_trends_analysis import V1PriceTrendsAnalysis

        by_fuel_type = self.by_fuel_type.to_dict()

        by_body_type = self.by_body_type.to_dict()

        by_year_range = self.by_year_range.to_dict()

        analysis = self.analysis.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "by_fuel_type": by_fuel_type,
                "by_body_type": by_body_type,
                "by_year_range": by_year_range,
                "analysis": analysis,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.v1_price_trends_by_fuel_type import V1PriceTrendsByFuelType
        from ..models.v1_price_trends_by_year_range import V1PriceTrendsByYearRange
        from ..models.v1_price_trends_by_body_type import V1PriceTrendsByBodyType
        from ..models.v1_price_trends_analysis import V1PriceTrendsAnalysis

        d = dict(src_dict)
        by_fuel_type = V1PriceTrendsByFuelType.from_dict(d.pop("by_fuel_type"))

        by_body_type = V1PriceTrendsByBodyType.from_dict(d.pop("by_body_type"))

        by_year_range = V1PriceTrendsByYearRange.from_dict(d.pop("by_year_range"))

        analysis = V1PriceTrendsAnalysis.from_dict(d.pop("analysis"))

        v1_price_trends = cls(
            by_fuel_type=by_fuel_type,
            by_body_type=by_body_type,
            by_year_range=by_year_range,
            analysis=analysis,
        )

        v1_price_trends.additional_properties = d
        return v1_price_trends

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
