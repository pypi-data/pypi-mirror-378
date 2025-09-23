"""
Data models and types for the Vehicles API client
"""

from typing import Optional, Dict, Any, List, Union, Literal
from dataclasses import dataclass, field
from enum import Enum


class ExportFormat(str, Enum):
    """Export format options"""
    CSV = "csv"
    EXCEL = "excel"
    JSON = "json"


class SortOrder(str, Enum):
    """Sort order options"""
    ASC = "asc"
    DESC = "desc"


@dataclass
class PaginationParams:
    """Pagination parameters for API requests"""
    page: Optional[int] = None
    page_size: Optional[int] = None
    limit: Optional[int] = None
    offset: Optional[int] = None


@dataclass
class VehicleFilter:
    """Filter parameters for vehicle queries"""
    # Search
    search: Optional[str] = None
    
    # Basic filters
    brand: Optional[str] = None
    model: Optional[str] = None
    source: Optional[str] = None
    
    # Price filters
    price_min: Optional[float] = None
    price_max: Optional[float] = None
    price_currency: Optional[str] = None
    
    # Year filters
    year_min: Optional[int] = None
    year_max: Optional[int] = None
    
    # Mileage filters
    mileage_min: Optional[int] = None
    mileage_max: Optional[int] = None
    
    # Vehicle characteristics
    fuel_type: Optional[str] = None
    transmission: Optional[str] = None
    body_type: Optional[str] = None
    color: Optional[str] = None
    
    # Quality filters
    investment_grade: Optional[str] = None
    risk_level: Optional[str] = None
    high_quality: Optional[bool] = None
    low_risk: Optional[bool] = None
    
    # Status filters
    status: Optional[str] = None
    has_photos: Optional[bool] = None
    
    # Sorting
    ordering: Optional[str] = None
    
    # Multiple values (comma-separated strings or lists)
    brands: Optional[Union[str, List[str]]] = None
    models: Optional[Union[str, List[str]]] = None
    sources: Optional[Union[str, List[str]]] = None
    fuel_types: Optional[Union[str, List[str]]] = None
    transmissions: Optional[Union[str, List[str]]] = None
    body_types: Optional[Union[str, List[str]]] = None
    colors: Optional[Union[str, List[str]]] = None
    investment_grades: Optional[Union[str, List[str]]] = None
    risk_levels: Optional[Union[str, List[str]]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert filter to dictionary for API requests"""
        result = {}
        
        for key, value in self.__dict__.items():
            if value is not None:
                # Convert lists to comma-separated strings
                if isinstance(value, list):
                    result[key] = ",".join(str(v) for v in value)
                else:
                    result[key] = value
        
        return result


@dataclass
class APIResponse:
    """Generic API response wrapper"""
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    status_code: Optional[int] = None
    message: Optional[str] = None
    details: Optional[Dict[str, Any]] = field(default_factory=dict)
    
    @classmethod
    def success_response(cls, data: Any, message: Optional[str] = None) -> "APIResponse":
        """Create successful response"""
        return cls(success=True, data=data, message=message)
    
    @classmethod
    def error_response(
        cls, 
        error: str, 
        status_code: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> "APIResponse":
        """Create error response"""
        return cls(
            success=False, 
            error=error, 
            status_code=status_code,
            details=details or {}
        )


@dataclass
class APIError:
    """API error details"""
    message: str
    code: Optional[str] = None
    field_name: Optional[str] = None
    details: Optional[Dict[str, Any]] = field(default_factory=dict)


@dataclass
class CacheInfo:
    """Cache information"""
    last_updated: Optional[str] = None
    total_records: Optional[int] = None
    cache_key: Optional[str] = None
    expires_at: Optional[str] = None


@dataclass
class ExportOptions:
    """Export options"""
    format: ExportFormat
    filename: Optional[str] = None
    filters: Optional[VehicleFilter] = None
    fields: Optional[List[str]] = None


# Type aliases for better readability
VehicleID = str
BrandCode = str
ModelCode = str
SourceCode = str

# Query parameter types
QueryParams = Dict[str, Union[str, int, float, bool, List[str]]]
Headers = Dict[str, str]
