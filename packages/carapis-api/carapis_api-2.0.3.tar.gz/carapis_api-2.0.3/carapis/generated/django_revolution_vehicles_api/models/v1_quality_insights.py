from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from typing import cast

if TYPE_CHECKING:
    from ..models.v1_quality_insights_insights import V1QualityInsightsInsights
    from ..models.v1_quality_insights_risk_levels import V1QualityInsightsRiskLevels
    from ..models.v1_quality_insights_investment_grades import V1QualityInsightsInvestmentGrades
    from ..models.v1_quality_insights_brand_quality_ranking_item import V1QualityInsightsBrandQualityRankingItem


T = TypeVar("T", bound="V1QualityInsights")


@_attrs_define
class V1QualityInsights:
    """Quality insights serializer

    Attributes:
        investment_grades (V1QualityInsightsInvestmentGrades):
        risk_levels (V1QualityInsightsRiskLevels):
        brand_quality_ranking (list['V1QualityInsightsBrandQualityRankingItem']):
        insights (V1QualityInsightsInsights):
    """

    investment_grades: "V1QualityInsightsInvestmentGrades"
    risk_levels: "V1QualityInsightsRiskLevels"
    brand_quality_ranking: list["V1QualityInsightsBrandQualityRankingItem"]
    insights: "V1QualityInsightsInsights"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.v1_quality_insights_insights import V1QualityInsightsInsights
        from ..models.v1_quality_insights_risk_levels import V1QualityInsightsRiskLevels
        from ..models.v1_quality_insights_investment_grades import V1QualityInsightsInvestmentGrades
        from ..models.v1_quality_insights_brand_quality_ranking_item import V1QualityInsightsBrandQualityRankingItem

        investment_grades = self.investment_grades.to_dict()

        risk_levels = self.risk_levels.to_dict()

        brand_quality_ranking = []
        for brand_quality_ranking_item_data in self.brand_quality_ranking:
            brand_quality_ranking_item = brand_quality_ranking_item_data.to_dict()
            brand_quality_ranking.append(brand_quality_ranking_item)

        insights = self.insights.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "investment_grades": investment_grades,
                "risk_levels": risk_levels,
                "brand_quality_ranking": brand_quality_ranking,
                "insights": insights,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.v1_quality_insights_insights import V1QualityInsightsInsights
        from ..models.v1_quality_insights_risk_levels import V1QualityInsightsRiskLevels
        from ..models.v1_quality_insights_investment_grades import V1QualityInsightsInvestmentGrades
        from ..models.v1_quality_insights_brand_quality_ranking_item import V1QualityInsightsBrandQualityRankingItem

        d = dict(src_dict)
        investment_grades = V1QualityInsightsInvestmentGrades.from_dict(d.pop("investment_grades"))

        risk_levels = V1QualityInsightsRiskLevels.from_dict(d.pop("risk_levels"))

        brand_quality_ranking = []
        _brand_quality_ranking = d.pop("brand_quality_ranking")
        for brand_quality_ranking_item_data in _brand_quality_ranking:
            brand_quality_ranking_item = V1QualityInsightsBrandQualityRankingItem.from_dict(
                brand_quality_ranking_item_data
            )

            brand_quality_ranking.append(brand_quality_ranking_item)

        insights = V1QualityInsightsInsights.from_dict(d.pop("insights"))

        v1_quality_insights = cls(
            investment_grades=investment_grades,
            risk_levels=risk_levels,
            brand_quality_ranking=brand_quality_ranking,
            insights=insights,
        )

        v1_quality_insights.additional_properties = d
        return v1_quality_insights

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
