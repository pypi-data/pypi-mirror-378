"""Contains all the data models used in inputs/outputs"""

from .paginated_v1_brand_list import PaginatedV1BrandList
from .paginated_v1_source_list import PaginatedV1SourceList
from .paginated_v1_vehicle_list_list import PaginatedV1VehicleListList
from .paginated_v1_vehicle_model_list import PaginatedV1VehicleModelList
from .v1_brand import V1Brand
from .v1_brand_comparison_stats import V1BrandComparisonStats
from .v1_brand_comparison_stats_brands_item import V1BrandComparisonStatsBrandsItem
from .v1_price_trends import V1PriceTrends
from .v1_price_trends_analysis import V1PriceTrendsAnalysis
from .v1_price_trends_by_body_type import V1PriceTrendsByBodyType
from .v1_price_trends_by_fuel_type import V1PriceTrendsByFuelType
from .v1_price_trends_by_year_range import V1PriceTrendsByYearRange
from .v1_quality_insights import V1QualityInsights
from .v1_quality_insights_brand_quality_ranking_item import V1QualityInsightsBrandQualityRankingItem
from .v1_quality_insights_insights import V1QualityInsightsInsights
from .v1_quality_insights_investment_grades import V1QualityInsightsInvestmentGrades
from .v1_quality_insights_risk_levels import V1QualityInsightsRiskLevels
from .v1_source import V1Source
from .v1_source_default_currency import V1SourceDefaultCurrency
from .v1_statistics import V1Statistics
from .v1_statistics_overview import V1StatisticsOverview
from .v1_statistics_price_statistics import V1StatisticsPriceStatistics
from .v1_statistics_quality_distribution import V1StatisticsQualityDistribution
from .v1_statistics_top_brands_item import V1StatisticsTopBrandsItem
from .v1_statistics_top_sources_item import V1StatisticsTopSourcesItem
from .v1_statistics_year_statistics import V1StatisticsYearStatistics
from .v1_vehicle_detail import V1VehicleDetail
from .v1_vehicle_detail_body_type import V1VehicleDetailBodyType
from .v1_vehicle_detail_color import V1VehicleDetailColor
from .v1_vehicle_detail_fuel_type import V1VehicleDetailFuelType
from .v1_vehicle_detail_investment_grade import V1VehicleDetailInvestmentGrade
from .v1_vehicle_detail_price_currency import V1VehicleDetailPriceCurrency
from .v1_vehicle_detail_risk_level import V1VehicleDetailRiskLevel
from .v1_vehicle_detail_status import V1VehicleDetailStatus
from .v1_vehicle_detail_transmission import V1VehicleDetailTransmission
from .v1_vehicle_export import V1VehicleExport
from .v1_vehicle_export_body_type import V1VehicleExportBodyType
from .v1_vehicle_export_color import V1VehicleExportColor
from .v1_vehicle_export_fuel_type import V1VehicleExportFuelType
from .v1_vehicle_export_investment_grade import V1VehicleExportInvestmentGrade
from .v1_vehicle_export_price_currency import V1VehicleExportPriceCurrency
from .v1_vehicle_export_risk_level import V1VehicleExportRiskLevel
from .v1_vehicle_export_status import V1VehicleExportStatus
from .v1_vehicle_export_transmission import V1VehicleExportTransmission
from .v1_vehicle_list import V1VehicleList
from .v1_vehicle_list_body_type import V1VehicleListBodyType
from .v1_vehicle_list_color import V1VehicleListColor
from .v1_vehicle_list_fuel_type import V1VehicleListFuelType
from .v1_vehicle_list_investment_grade import V1VehicleListInvestmentGrade
from .v1_vehicle_list_main_photo_type_0 import V1VehicleListMainPhotoType0
from .v1_vehicle_list_price_currency import V1VehicleListPriceCurrency
from .v1_vehicle_list_risk_level import V1VehicleListRiskLevel
from .v1_vehicle_list_transmission import V1VehicleListTransmission
from .v1_vehicle_model import V1VehicleModel
from .v1_vehicle_model_primary_body_type import V1VehicleModelPrimaryBodyType
from .v1_vehicle_photo import V1VehiclePhoto
from .v1_vehicle_photo_photo_type import V1VehiclePhotoPhotoType
from .v1_vehicle_stats import V1VehicleStats
from .v1_vehicle_stats_by_body_type import V1VehicleStatsByBodyType
from .v1_vehicle_stats_by_brand import V1VehicleStatsByBrand
from .v1_vehicle_stats_by_color import V1VehicleStatsByColor
from .v1_vehicle_stats_by_fuel_type import V1VehicleStatsByFuelType
from .v1_vehicle_stats_by_investment_grade import V1VehicleStatsByInvestmentGrade
from .v1_vehicle_stats_by_risk_level import V1VehicleStatsByRiskLevel
from .v1_vehicle_stats_by_transmission import V1VehicleStatsByTransmission
from .v1_vehicle_stats_price_ranges import V1VehicleStatsPriceRanges
from .v1_vehicle_stats_quality_metrics import V1VehicleStatsQualityMetrics
from .v1_vehicle_stats_year_distribution import V1VehicleStatsYearDistribution
from .v1api_info_response import V1APIInfoResponse
from .v1api_info_response_data_sources_item import V1APIInfoResponseDataSourcesItem
from .v1api_info_response_endpoints import V1APIInfoResponseEndpoints
from .v1api_info_response_rate_limits import V1APIInfoResponseRateLimits
from .vehicles_api_v1_sources_list_default_currency import VehiclesApiV1SourcesListDefaultCurrency
from .vehicles_api_v1_vehicles_list_body_type import VehiclesApiV1VehiclesListBodyType
from .vehicles_api_v1_vehicles_list_body_types_item import VehiclesApiV1VehiclesListBodyTypesItem
from .vehicles_api_v1_vehicles_list_color import VehiclesApiV1VehiclesListColor
from .vehicles_api_v1_vehicles_list_colors_item import VehiclesApiV1VehiclesListColorsItem
from .vehicles_api_v1_vehicles_list_fuel_types_item import VehiclesApiV1VehiclesListFuelTypesItem
from .vehicles_api_v1_vehicles_list_investment_grades_item import VehiclesApiV1VehiclesListInvestmentGradesItem
from .vehicles_api_v1_vehicles_list_risk_level import VehiclesApiV1VehiclesListRiskLevel
from .vehicles_api_v1_vehicles_list_risk_levels_item import VehiclesApiV1VehiclesListRiskLevelsItem
from .vehicles_api_v1_vehicles_list_status import VehiclesApiV1VehiclesListStatus
from .vehicles_api_v1_vehicles_list_transmission import VehiclesApiV1VehiclesListTransmission
from .vehicles_api_v1_vehicles_list_transmissions_item import VehiclesApiV1VehiclesListTransmissionsItem

__all__ = (
    "PaginatedV1BrandList",
    "PaginatedV1SourceList",
    "PaginatedV1VehicleListList",
    "PaginatedV1VehicleModelList",
    "V1APIInfoResponse",
    "V1APIInfoResponseDataSourcesItem",
    "V1APIInfoResponseEndpoints",
    "V1APIInfoResponseRateLimits",
    "V1Brand",
    "V1BrandComparisonStats",
    "V1BrandComparisonStatsBrandsItem",
    "V1PriceTrends",
    "V1PriceTrendsAnalysis",
    "V1PriceTrendsByBodyType",
    "V1PriceTrendsByFuelType",
    "V1PriceTrendsByYearRange",
    "V1QualityInsights",
    "V1QualityInsightsBrandQualityRankingItem",
    "V1QualityInsightsInsights",
    "V1QualityInsightsInvestmentGrades",
    "V1QualityInsightsRiskLevels",
    "V1Source",
    "V1SourceDefaultCurrency",
    "V1Statistics",
    "V1StatisticsOverview",
    "V1StatisticsPriceStatistics",
    "V1StatisticsQualityDistribution",
    "V1StatisticsTopBrandsItem",
    "V1StatisticsTopSourcesItem",
    "V1StatisticsYearStatistics",
    "V1VehicleDetail",
    "V1VehicleDetailBodyType",
    "V1VehicleDetailColor",
    "V1VehicleDetailFuelType",
    "V1VehicleDetailInvestmentGrade",
    "V1VehicleDetailPriceCurrency",
    "V1VehicleDetailRiskLevel",
    "V1VehicleDetailStatus",
    "V1VehicleDetailTransmission",
    "V1VehicleExport",
    "V1VehicleExportBodyType",
    "V1VehicleExportColor",
    "V1VehicleExportFuelType",
    "V1VehicleExportInvestmentGrade",
    "V1VehicleExportPriceCurrency",
    "V1VehicleExportRiskLevel",
    "V1VehicleExportStatus",
    "V1VehicleExportTransmission",
    "V1VehicleList",
    "V1VehicleListBodyType",
    "V1VehicleListColor",
    "V1VehicleListFuelType",
    "V1VehicleListInvestmentGrade",
    "V1VehicleListMainPhotoType0",
    "V1VehicleListPriceCurrency",
    "V1VehicleListRiskLevel",
    "V1VehicleListTransmission",
    "V1VehicleModel",
    "V1VehicleModelPrimaryBodyType",
    "V1VehiclePhoto",
    "V1VehiclePhotoPhotoType",
    "V1VehicleStats",
    "V1VehicleStatsByBodyType",
    "V1VehicleStatsByBrand",
    "V1VehicleStatsByColor",
    "V1VehicleStatsByFuelType",
    "V1VehicleStatsByInvestmentGrade",
    "V1VehicleStatsByRiskLevel",
    "V1VehicleStatsByTransmission",
    "V1VehicleStatsPriceRanges",
    "V1VehicleStatsQualityMetrics",
    "V1VehicleStatsYearDistribution",
    "VehiclesApiV1SourcesListDefaultCurrency",
    "VehiclesApiV1VehiclesListBodyType",
    "VehiclesApiV1VehiclesListBodyTypesItem",
    "VehiclesApiV1VehiclesListColor",
    "VehiclesApiV1VehiclesListColorsItem",
    "VehiclesApiV1VehiclesListFuelTypesItem",
    "VehiclesApiV1VehiclesListInvestmentGradesItem",
    "VehiclesApiV1VehiclesListRiskLevel",
    "VehiclesApiV1VehiclesListRiskLevelsItem",
    "VehiclesApiV1VehiclesListStatus",
    "VehiclesApiV1VehiclesListTransmission",
    "VehiclesApiV1VehiclesListTransmissionsItem",
)
