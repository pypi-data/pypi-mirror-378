"""
Catalog types for frontend applications
Based on generated API types but adapted for UI use
"""

from typing import Optional, Dict, Any, List, Union, Literal
from dataclasses import dataclass, field
from datetime import datetime

# Re-export generated types for convenience
try:
    import sys
    from pathlib import Path
    
    # Add the generated API to Python path
    generated_path = Path(__file__).parent / "generated"
    if str(generated_path) not in sys.path:
        sys.path.insert(0, str(generated_path))
    
    from django_revolution_vehicles_api.models import (
        V1Brand,
        V1VehicleList,
        V1VehicleDetail,
        V1VehiclePhoto,
        V1VehicleModel,
        PaginatedV1VehicleListList,
        PaginatedV1BrandList,
        V1Statistics
    )
except ImportError:
    # Fallback types if generated models are not available
    V1Brand = Dict[str, Any]
    V1VehicleList = Dict[str, Any]
    V1VehicleDetail = Dict[str, Any]
    V1VehiclePhoto = Dict[str, Any]
    V1VehicleModel = Dict[str, Any]
    PaginatedV1VehicleListList = Dict[str, Any]
    PaginatedV1BrandList = Dict[str, Any]
    V1Statistics = Dict[str, Any]


# ===============================
# Base catalog types
# ===============================

@dataclass
class CatalogVehicle:
    """
    Vehicle for catalog - extended version of V1VehicleList
    Optimized for frontend display with additional computed fields
    """
    # Main fields from API
    id: Optional[str] = None
    listing_id: str = ""
    
    # Vehicle details
    brand_name: Optional[str] = None
    model_name: Optional[str] = None
    year: Optional[int] = None
    price: Optional[float] = None
    original_price: Optional[float] = None
    mileage: Optional[int] = None
    trim: Optional[str] = None
    condition: Optional[str] = None
    
    # Display fields (computed)
    display_name: str = ""
    formatted_price: str = ""
    primary_image_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    
    # UI state
    is_favorited: bool = False
    condition_score: int = 50  # 0-100
    
    # Additional data
    features: List[str] = field(default_factory=list)
    photos: List[Dict[str, Any]] = field(default_factory=list)
    
    # Compatibility with old types
    make: Optional[str] = None
    model: Optional[str] = None
    
    def __post_init__(self):
        """Compute derived fields after initialization"""
        if not self.display_name:
            parts = [str(self.year) if self.year else "", 
                    self.brand_name or "", 
                    self.model_name or ""]
            self.display_name = " ".join(filter(None, parts))
        
        if not self.formatted_price and self.price:
            self.formatted_price = f"${self.price:,.0f}"
        
        # Set compatibility fields
        if not self.make:
            self.make = self.brand_name
        if not self.model:
            self.model = self.model_name


@dataclass 
class CatalogBrand:
    """
    Brand for catalog - extended version of V1Brand
    """
    # Main fields from API
    id: Optional[int] = None
    name: Optional[str] = None
    code: Optional[str] = None
    logo_url: Optional[str] = None
    
    # Extended fields
    vehicle_count: int = 0
    is_featured: bool = False
    
    # Statistics
    average_price: Optional[float] = None
    price_range_min: Optional[float] = None
    price_range_max: Optional[float] = None


@dataclass
class CatalogFilters:
    """
    Filters for catalog - comprehensive filtering options
    """
    # Main filters
    search: Optional[str] = None
    brand: Optional[str] = None
    brand_code: Optional[str] = None
    model: Optional[str] = None
    
    # Price filters
    price: Optional[float] = None
    price_min: Optional[float] = None
    price_max: Optional[float] = None
    price_currency: Optional[Literal["KRW", "USD", "JPY", "EUR", "CNY", "RUB", "other"]] = None
    
    # Year filters
    year: Optional[int] = None
    year_min: Optional[int] = None
    year_max: Optional[int] = None
    
    # Mileage filters
    mileage: Optional[int] = None
    mileage_min: Optional[int] = None
    mileage_max: Optional[int] = None
    
    # Body type filters
    body_type: Optional[Literal[
        "bus", "convertible", "coupe", "crossover", "hatchback", 
        "minivan", "other", "pickup", "sedan", "suv", "truck", 
        "unknown", "van", "wagon"
    ]] = None
    body_types: Optional[List[str]] = None
    
    # Fuel type filters
    fuel_type: Optional[Literal[
        "gasoline", "diesel", "hybrid", "plug_hybrid", "electric", 
        "hydrogen", "cng", "lpg", "other", "unknown"
    ]] = None
    fuel_types: Optional[List[str]] = None
    
    # Transmission filters
    transmission: Optional[Literal[
        "manual", "automatic", "cvt", "semi_automatic", "other", "unknown"
    ]] = None
    transmissions: Optional[List[str]] = None
    
    # Drivetrain filters
    drivetrain: Optional[Literal[
        "fwd", "rwd", "awd", "4wd", "other", "unknown"
    ]] = None
    drivetrains: Optional[List[str]] = None
    
    # Color filters
    color: Optional[Literal[
        "white", "black", "gray", "silver", "red", "blue", "yellow", 
        "green", "brown", "purple", "orange", "pink", "gold", "beige", 
        "other", "unknown"
    ]] = None
    colors: Optional[List[str]] = None
    
    # Condition filters
    condition: Optional[Literal[
        "new", "used", "certified", "damaged", "salvage", "other", "unknown"
    ]] = None
    conditions: Optional[List[str]] = None
    
    # Accidents
    accident_count: Optional[int] = None
    accident_count_lte: Optional[int] = None
    
    # Engine volume
    engine_volume: Optional[float] = None
    engine_volume_min: Optional[float] = None
    engine_volume_max: Optional[float] = None
    
    # Power
    power: Optional[int] = None
    power_min: Optional[int] = None
    power_max: Optional[int] = None
    
    # Source
    source: Optional[str] = None
    sources: Optional[List[str]] = None
    
    # Pagination
    page: Optional[int] = None
    page_size: Optional[int] = None
    
    # Sorting
    ordering: Optional[str] = None
    sort: Optional[str] = None  # Alias for ordering
    
    # Additional filters (for compatibility)
    make: Optional[str] = None  # Alias for brand_code
    features: Optional[List[str]] = None
    radius: Optional[float] = None
    dealer_ids: Optional[List[str]] = None
    location: Optional[str] = None
    
    def to_api_params(self) -> Dict[str, Any]:
        """Convert filters to API parameters with proper field mapping"""
        params = {}
        
        # Direct mappings
        direct_fields = [
            'search', 'brand_code', 'model', 'price', 'price_min', 'price_max', 
            'price_currency', 'year', 'year_min', 'year_max', 'mileage', 
            'mileage_min', 'mileage_max', 'body_type', 'fuel_type', 
            'transmission', 'drivetrain', 'color', 'condition', 
            'accident_count', 'engine_volume', 'engine_volume_min', 
            'engine_volume_max', 'power', 'power_min', 'power_max', 
            'source', 'page', 'page_size', 'ordering'
        ]
        
        for field in direct_fields:
            value = getattr(self, field, None)
            if value is not None:
                params[field] = value
        
        # Special mappings
        if self.make and not self.brand_code:
            params['brand_code'] = self.make
        
        if self.sort and not self.ordering:
            params['ordering'] = self.sort
            
        if self.accident_count_lte:
            params['accident_count__lte'] = self.accident_count_lte
        
        # Array fields
        array_fields = [
            'body_types', 'fuel_types', 'transmissions', 'drivetrains', 
            'colors', 'conditions', 'sources'
        ]
        
        for field in array_fields:
            value = getattr(self, field, None)
            if value:
                params[field] = value
        
        # Remove None values
        return {k: v for k, v in params.items() if v is not None}


# ===============================
# Pagination types
# ===============================

@dataclass
class PaginationInfo:
    """Pagination information"""
    count: int
    next: Optional[str] = None
    previous: Optional[str] = None
    current_page: int = 1
    total_pages: int = 1
    page_size: int = 20


@dataclass
class PaginatedResponse:
    """Generic paginated response"""
    results: List[Any]
    count: int
    next: Optional[str] = None
    previous: Optional[str] = None
    
    @property
    def pagination_info(self) -> PaginationInfo:
        """Get pagination info"""
        return PaginationInfo(
            count=self.count,
            next=self.next,
            previous=self.previous
        )


# ===============================
# Statistics types
# ===============================

@dataclass
class VehicleStats:
    """Vehicle statistics for catalog"""
    total_count: int
    average_price: float
    price_range: Dict[str, float]  # {"min": 0, "max": 100000}
    popular_brands: List[Dict[str, Union[str, int]]]  # [{"name": "Toyota", "count": 100}]
    popular_models: List[Dict[str, Union[str, int]]]


@dataclass
class BrandStats:
    """Brand statistics"""
    vehicle_count: int
    average_price: float
    price_range: Dict[str, float]
    popular_models: List[str]
    year_range: Dict[str, int]  # {"min": 2010, "max": 2024}


# ===============================
# Search types
# ===============================

@dataclass
class SearchSuggestion:
    """Search suggestion"""
    type: Literal['make', 'model', 'location', 'feature']
    value: str
    label: str
    count: Optional[int] = None


@dataclass
class SearchFacets:
    """Search facets for filtering"""
    makes: List[Dict[str, Union[str, int]]] = field(default_factory=list)
    models: List[Dict[str, Union[str, int]]] = field(default_factory=list)
    years: List[Dict[str, Union[str, int]]] = field(default_factory=list)
    price_ranges: List[Dict[str, Union[str, int, float]]] = field(default_factory=list)
    body_types: List[Dict[str, Union[str, int]]] = field(default_factory=list)
    fuel_types: List[Dict[str, Union[str, int]]] = field(default_factory=list)
    colors: List[Dict[str, Union[str, int]]] = field(default_factory=list)


# ===============================
# Page data types for SSR
# ===============================

@dataclass
class VehiclePageData:
    """Data for vehicle catalog page"""
    vehicles: List[CatalogVehicle]
    total_count: int
    current_page: int
    total_pages: int
    has_next: bool
    has_previous: bool


@dataclass
class VehicleDetailPageData:
    """Data for vehicle detail page"""
    vehicle: CatalogVehicle
    similar_vehicles: List[CatalogVehicle]
    related_vehicles: List[CatalogVehicle]


@dataclass
class BrandPageData:
    """Data for brand page"""
    brand: CatalogBrand
    vehicles: List[CatalogVehicle]
    models: List[Dict[str, Any]]
    total_count: int
    stats: BrandStats


@dataclass
class SearchPageData:
    """Data for search page"""
    vehicles: List[CatalogVehicle]
    filters: CatalogFilters
    suggestions: List[SearchSuggestion]
    facets: SearchFacets


# ===============================
# SEO types
# ===============================

@dataclass
class SEOMetadata:
    """SEO metadata for pages"""
    title: str
    description: str
    keywords: Optional[List[str]] = None
    canonical_url: Optional[str] = None
    og_title: Optional[str] = None
    og_description: Optional[str] = None
    og_image: Optional[str] = None
    og_type: str = "website"
    twitter_card: str = "summary_large_image"
    twitter_title: Optional[str] = None
    twitter_description: Optional[str] = None
    twitter_image: Optional[str] = None


# Export all types
__all__ = [
    # Generated types (re-exported)
    "V1Brand",
    "V1VehicleList", 
    "V1VehicleDetail",
    "V1VehiclePhoto",
    "V1VehicleModel",
    "PaginatedV1VehicleListList",
    "PaginatedV1BrandList",
    "V1Statistics",
    
    # Catalog types
    "CatalogVehicle",
    "CatalogBrand", 
    "CatalogFilters",
    
    # Pagination types
    "PaginationInfo",
    "PaginatedResponse",
    
    # Statistics types
    "VehicleStats",
    "BrandStats",
    
    # Search types
    "SearchSuggestion",
    "SearchFacets",
    
    # Page data types
    "VehiclePageData",
    "VehicleDetailPageData", 
    "BrandPageData",
    "SearchPageData",
    
    # SEO types
    "SEOMetadata"
]
