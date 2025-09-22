from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from typing import cast
from typing import cast, Union

if TYPE_CHECKING:
    from ..models.v1_vehicle_stats_by_transmission import V1VehicleStatsByTransmission
    from ..models.v1_vehicle_stats_by_fuel_type import V1VehicleStatsByFuelType
    from ..models.v1_vehicle_stats_year_distribution import V1VehicleStatsYearDistribution
    from ..models.v1_vehicle_stats_price_ranges import V1VehicleStatsPriceRanges
    from ..models.v1_vehicle_stats_by_risk_level import V1VehicleStatsByRiskLevel
    from ..models.v1_vehicle_stats_by_brand import V1VehicleStatsByBrand
    from ..models.v1_vehicle_stats_by_body_type import V1VehicleStatsByBodyType
    from ..models.v1_vehicle_stats_quality_metrics import V1VehicleStatsQualityMetrics
    from ..models.v1_vehicle_stats_by_color import V1VehicleStatsByColor
    from ..models.v1_vehicle_stats_by_investment_grade import V1VehicleStatsByInvestmentGrade


T = TypeVar("T", bound="V1VehicleStats")


@_attrs_define
class V1VehicleStats:
    """Serializer for vehicle statistics responses

    Attributes:
        total_count (int):
        avg_price (Union[None, float]):
        avg_price_usd (Union[None, float]):
        avg_mileage (Union[None, float]):
        avg_year (Union[None, float]):
        by_fuel_type (V1VehicleStatsByFuelType):
        by_transmission (V1VehicleStatsByTransmission):
        by_body_type (V1VehicleStatsByBodyType):
        by_color (V1VehicleStatsByColor):
        by_brand (V1VehicleStatsByBrand):
        by_investment_grade (V1VehicleStatsByInvestmentGrade):
        by_risk_level (V1VehicleStatsByRiskLevel):
        price_ranges (V1VehicleStatsPriceRanges):
        year_distribution (V1VehicleStatsYearDistribution):
        quality_metrics (V1VehicleStatsQualityMetrics):
    """

    total_count: int
    avg_price: Union[None, float]
    avg_price_usd: Union[None, float]
    avg_mileage: Union[None, float]
    avg_year: Union[None, float]
    by_fuel_type: "V1VehicleStatsByFuelType"
    by_transmission: "V1VehicleStatsByTransmission"
    by_body_type: "V1VehicleStatsByBodyType"
    by_color: "V1VehicleStatsByColor"
    by_brand: "V1VehicleStatsByBrand"
    by_investment_grade: "V1VehicleStatsByInvestmentGrade"
    by_risk_level: "V1VehicleStatsByRiskLevel"
    price_ranges: "V1VehicleStatsPriceRanges"
    year_distribution: "V1VehicleStatsYearDistribution"
    quality_metrics: "V1VehicleStatsQualityMetrics"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.v1_vehicle_stats_by_transmission import V1VehicleStatsByTransmission
        from ..models.v1_vehicle_stats_by_fuel_type import V1VehicleStatsByFuelType
        from ..models.v1_vehicle_stats_year_distribution import V1VehicleStatsYearDistribution
        from ..models.v1_vehicle_stats_price_ranges import V1VehicleStatsPriceRanges
        from ..models.v1_vehicle_stats_by_risk_level import V1VehicleStatsByRiskLevel
        from ..models.v1_vehicle_stats_by_brand import V1VehicleStatsByBrand
        from ..models.v1_vehicle_stats_by_body_type import V1VehicleStatsByBodyType
        from ..models.v1_vehicle_stats_quality_metrics import V1VehicleStatsQualityMetrics
        from ..models.v1_vehicle_stats_by_color import V1VehicleStatsByColor
        from ..models.v1_vehicle_stats_by_investment_grade import V1VehicleStatsByInvestmentGrade

        total_count = self.total_count

        avg_price: Union[None, float]
        avg_price = self.avg_price

        avg_price_usd: Union[None, float]
        avg_price_usd = self.avg_price_usd

        avg_mileage: Union[None, float]
        avg_mileage = self.avg_mileage

        avg_year: Union[None, float]
        avg_year = self.avg_year

        by_fuel_type = self.by_fuel_type.to_dict()

        by_transmission = self.by_transmission.to_dict()

        by_body_type = self.by_body_type.to_dict()

        by_color = self.by_color.to_dict()

        by_brand = self.by_brand.to_dict()

        by_investment_grade = self.by_investment_grade.to_dict()

        by_risk_level = self.by_risk_level.to_dict()

        price_ranges = self.price_ranges.to_dict()

        year_distribution = self.year_distribution.to_dict()

        quality_metrics = self.quality_metrics.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "total_count": total_count,
                "avg_price": avg_price,
                "avg_price_usd": avg_price_usd,
                "avg_mileage": avg_mileage,
                "avg_year": avg_year,
                "by_fuel_type": by_fuel_type,
                "by_transmission": by_transmission,
                "by_body_type": by_body_type,
                "by_color": by_color,
                "by_brand": by_brand,
                "by_investment_grade": by_investment_grade,
                "by_risk_level": by_risk_level,
                "price_ranges": price_ranges,
                "year_distribution": year_distribution,
                "quality_metrics": quality_metrics,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.v1_vehicle_stats_by_transmission import V1VehicleStatsByTransmission
        from ..models.v1_vehicle_stats_by_fuel_type import V1VehicleStatsByFuelType
        from ..models.v1_vehicle_stats_year_distribution import V1VehicleStatsYearDistribution
        from ..models.v1_vehicle_stats_price_ranges import V1VehicleStatsPriceRanges
        from ..models.v1_vehicle_stats_by_risk_level import V1VehicleStatsByRiskLevel
        from ..models.v1_vehicle_stats_by_brand import V1VehicleStatsByBrand
        from ..models.v1_vehicle_stats_by_body_type import V1VehicleStatsByBodyType
        from ..models.v1_vehicle_stats_quality_metrics import V1VehicleStatsQualityMetrics
        from ..models.v1_vehicle_stats_by_color import V1VehicleStatsByColor
        from ..models.v1_vehicle_stats_by_investment_grade import V1VehicleStatsByInvestmentGrade

        d = dict(src_dict)
        total_count = d.pop("total_count")

        def _parse_avg_price(data: object) -> Union[None, float]:
            if data is None:
                return data
            return cast(Union[None, float], data)

        avg_price = _parse_avg_price(d.pop("avg_price"))

        def _parse_avg_price_usd(data: object) -> Union[None, float]:
            if data is None:
                return data
            return cast(Union[None, float], data)

        avg_price_usd = _parse_avg_price_usd(d.pop("avg_price_usd"))

        def _parse_avg_mileage(data: object) -> Union[None, float]:
            if data is None:
                return data
            return cast(Union[None, float], data)

        avg_mileage = _parse_avg_mileage(d.pop("avg_mileage"))

        def _parse_avg_year(data: object) -> Union[None, float]:
            if data is None:
                return data
            return cast(Union[None, float], data)

        avg_year = _parse_avg_year(d.pop("avg_year"))

        by_fuel_type = V1VehicleStatsByFuelType.from_dict(d.pop("by_fuel_type"))

        by_transmission = V1VehicleStatsByTransmission.from_dict(d.pop("by_transmission"))

        by_body_type = V1VehicleStatsByBodyType.from_dict(d.pop("by_body_type"))

        by_color = V1VehicleStatsByColor.from_dict(d.pop("by_color"))

        by_brand = V1VehicleStatsByBrand.from_dict(d.pop("by_brand"))

        by_investment_grade = V1VehicleStatsByInvestmentGrade.from_dict(d.pop("by_investment_grade"))

        by_risk_level = V1VehicleStatsByRiskLevel.from_dict(d.pop("by_risk_level"))

        price_ranges = V1VehicleStatsPriceRanges.from_dict(d.pop("price_ranges"))

        year_distribution = V1VehicleStatsYearDistribution.from_dict(d.pop("year_distribution"))

        quality_metrics = V1VehicleStatsQualityMetrics.from_dict(d.pop("quality_metrics"))

        v1_vehicle_stats = cls(
            total_count=total_count,
            avg_price=avg_price,
            avg_price_usd=avg_price_usd,
            avg_mileage=avg_mileage,
            avg_year=avg_year,
            by_fuel_type=by_fuel_type,
            by_transmission=by_transmission,
            by_body_type=by_body_type,
            by_color=by_color,
            by_brand=by_brand,
            by_investment_grade=by_investment_grade,
            by_risk_level=by_risk_level,
            price_ranges=price_ranges,
            year_distribution=year_distribution,
            quality_metrics=quality_metrics,
        )

        v1_vehicle_stats.additional_properties = d
        return v1_vehicle_stats

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
