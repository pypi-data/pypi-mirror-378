"""
🚀 Vehicles API Python Library

Universal Python wrapper for the Vehicles API.
Provides clean, easy-to-use interface over the generated API client.

Usage:
    from libs.python import VehiclesAPIClient
    
    client = VehiclesAPIClient(
        base_url="https://api.example.com",
        api_key="your-api-key"
    )
    
    # Get vehicles
    vehicles = await client.vehicles.list()
    
    # Get vehicle details
    vehicle = await client.vehicles.get("vehicle-id")
    
    # Get brands
    brands = await client.brands.list()
"""

from .client import VehiclesAPIClient
from .services import (
    VehiclesService,
    BrandsService,
    SourcesService,
    StatisticsService,
    ApiService,
    VehiclesSSRService
)
from .models import (
    VehicleFilter,
    PaginationParams,
    ExportFormat,
    APIResponse,
    APIError
)
from .exceptions import (
    VehiclesAPIError,
    AuthenticationError,
    NetworkError,
    ValidationError
)
from .types import (
    # Catalog types
    CatalogVehicle,
    CatalogBrand,
    CatalogFilters,
    
    # Page data types
    VehiclePageData,
    VehicleDetailPageData,
    BrandPageData,
    SearchPageData,
    
    # Statistics types
    VehicleStats,
    BrandStats,
    
    # Search types
    SearchSuggestion,
    SearchFacets,
    
    # SEO types
    SEOMetadata,
    
    # Pagination types
    PaginationInfo,
    PaginatedResponse,
    
    # Generated types (re-exported)
    V1Brand,
    V1VehicleList,
    V1VehicleDetail,
    V1VehiclePhoto,
    PaginatedV1VehicleListList
)

__version__ = "2.0.3"
__all__ = [
    # Main client
    "VehiclesAPIClient",
    
    # Services
    "VehiclesService",
    "BrandsService", 
    "SourcesService",
    "StatisticsService",
    "ApiService",
    "VehiclesSSRService",
    
    # Legacy models
    "VehicleFilter",
    "PaginationParams",
    "ExportFormat",
    "APIResponse",
    "APIError",
    
    # Exceptions
    "VehiclesAPIError",
    "AuthenticationError",
    "NetworkError",
    "ValidationError",
    
    # Catalog types
    "CatalogVehicle",
    "CatalogBrand",
    "CatalogFilters",
    
    # Page data types
    "VehiclePageData",
    "VehicleDetailPageData",
    "BrandPageData",
    "SearchPageData",
    
    # Statistics types
    "VehicleStats",
    "BrandStats",
    
    # Search types
    "SearchSuggestion",
    "SearchFacets",
    
    # SEO types
    "SEOMetadata",
    
    # Pagination types
    "PaginationInfo",
    "PaginatedResponse",
    
    # Generated types (re-exported)
    "V1Brand",
    "V1VehicleList",
    "V1VehicleDetail",
    "V1VehiclePhoto",
    "PaginatedV1VehicleListList"
]
