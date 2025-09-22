"""
Vehicles SSR Service

Server-side data fetching service for vehicle pages.
Optimized for SSR/SSG with proper error handling and caching.
"""

import asyncio
import re
from typing import Optional, Dict, Any, List, Union
from datetime import datetime

from ..types import (
    CatalogVehicle, CatalogBrand, CatalogFilters,
    VehiclePageData, VehicleDetailPageData, BrandPageData, SearchPageData,
    VehicleStats, BrandStats, SearchSuggestion, SearchFacets,
    SEOMetadata, PaginationInfo
)
from .vehicles import VehiclesService
from .brands import BrandsService
from ..exceptions import VehiclesAPIError


class VehiclesSSRService:
    """
    Vehicles SSR Service
    
    Static methods for server-side data fetching and page generation.
    Optimized for Django, FastAPI, Flask, and other Python web frameworks.
    """
    
    @staticmethod
    async def get_vehicles_for_catalog(
        filters: Optional[CatalogFilters] = None,
        page: int = 1,
        page_size: int = 20,
        client = None
    ) -> VehiclePageData:
        """
        Get vehicles for catalog page with filters
        
        Args:
            filters: Catalog filters
            page: Page number
            page_size: Items per page
            client: API client instance
            
        Returns:
            VehiclePageData with vehicles and pagination info
        """
        try:
            if not client:
                raise VehiclesAPIError("API client is required")
            
            # Convert filters to API parameters
            api_params = {}
            if filters:
                api_params = filters.to_api_params()
            
            api_params.update({
                'page': page,
                'page_size': page_size
            })
            
            # Get vehicles from API
            vehicles_service = VehiclesService(client._client)
            response = await vehicles_service.list_async(**api_params)
            
            # Transform to catalog vehicles
            vehicles = []
            if hasattr(response, 'results') and response.results:
                for vehicle_data in response.results:
                    catalog_vehicle = VehiclesSSRService._transform_vehicle_to_catalog(vehicle_data)
                    vehicles.append(catalog_vehicle)
            
            # Calculate pagination
            total_count = getattr(response, 'count', 0)
            total_pages = (total_count + page_size - 1) // page_size if total_count > 0 else 0
            has_next = getattr(response, 'next', None) is not None
            has_previous = getattr(response, 'previous', None) is not None
            
            return VehiclePageData(
                vehicles=vehicles,
                total_count=total_count,
                current_page=page,
                total_pages=total_pages,
                has_next=has_next,
                has_previous=has_previous
            )
            
        except Exception as error:
            print(f"Error fetching vehicles for catalog: {error}")
            return VehiclesSSRService._get_empty_vehicle_page_data()
    
    @staticmethod
    async def get_vehicle_detail(
        vehicle_id: str,
        client = None
    ) -> Optional[VehicleDetailPageData]:
        """
        Get vehicle detail with related data
        
        Args:
            vehicle_id: Vehicle ID
            client: API client instance
            
        Returns:
            VehicleDetailPageData or None if not found
        """
        try:
            if not client:
                raise VehiclesAPIError("API client is required")
            
            vehicles_service = VehiclesService(client._client)
            
            # Get vehicle details
            vehicle = await vehicles_service.get_async(vehicle_id)
            if not vehicle:
                return None
            
            # Get related vehicles (same brand/model)
            related_vehicles = []
            try:
                brand_code = getattr(vehicle, 'brand_code', None) or getattr(vehicle, 'brand_name', None)
                if brand_code:
                    related_response = await vehicles_service.list_async(
                        brand_code=brand_code,
                        page_size=4
                    )
                    if hasattr(related_response, 'results') and related_response.results:
                        for related_data in related_response.results[:4]:
                            if getattr(related_data, 'id', None) != vehicle_id:  # Exclude current vehicle
                                related_vehicle = VehiclesSSRService._transform_vehicle_to_catalog(related_data)
                                related_vehicles.append(related_vehicle)
            except Exception as e:
                print(f"Error fetching related vehicles: {e}")
            
            return VehicleDetailPageData(
                vehicle=VehiclesSSRService._transform_vehicle_to_catalog(vehicle),
                similar_vehicles=[],  # Similar vehicles would be fetched separately if needed
                related_vehicles=related_vehicles
            )
            
        except Exception as error:
            print(f"Error fetching vehicle detail: {error}")
            return None
    
    @staticmethod
    async def get_brand_page_data(
        brand_slug: str,
        page: int = 1,
        page_size: int = 20,
        client = None
    ) -> Optional[BrandPageData]:
        """
        Get brand page data
        
        Args:
            brand_slug: Brand slug/code
            page: Page number
            page_size: Items per page
            client: API client instance
            
        Returns:
            BrandPageData or None if brand not found
        """
        try:
            if not client:
                raise VehiclesAPIError("API client is required")
            
            brands_service = BrandsService(client._client)
            
            # Find brand by slug
            brands_response = await brands_service.list_async(search=brand_slug, page_size=1)
            if not hasattr(brands_response, 'results') or not brands_response.results:
                return None
            
            brand_data = brands_response.results[0]
            brand_id = getattr(brand_data, 'id', None)
            if not brand_id:
                return None
            
            # Get vehicles for this brand and models in parallel
            vehicles_task = brands_service.get_brand_vehicles_async(
                str(brand_id), page=page, page_size=page_size
            )
            models_task = brands_service.get_brand_models_async(
                str(brand_id), page_size=100
            )
            
            try:
                vehicles_response, models_response = await asyncio.gather(
                    vehicles_task, models_task, return_exceptions=True
                )
            except Exception:
                vehicles_response = await vehicles_task
                models_response = None
            
            # Transform vehicles
            vehicles = []
            if hasattr(vehicles_response, 'results') and vehicles_response.results:
                for vehicle_data in vehicles_response.results:
                    catalog_vehicle = VehiclesSSRService._transform_vehicle_to_catalog(vehicle_data)
                    vehicles.append(catalog_vehicle)
            
            # Calculate statistics
            prices = [v.price for v in vehicles if v.price and v.price > 0]
            stats = BrandStats(
                vehicle_count=len(vehicles),
                average_price=sum(prices) / len(prices) if prices else 0,
                price_range={
                    "min": min(prices) if prices else 0,
                    "max": max(prices) if prices else 0
                },
                popular_models=[],
                year_range={"min": 2010, "max": 2024}  # Default range
            )
            
            # Get popular models
            if models_response and hasattr(models_response, 'results'):
                stats.popular_models = [
                    getattr(model, 'name', '') for model in models_response.results[:8]
                    if getattr(model, 'name', '')
                ]
            
            return BrandPageData(
                brand=VehiclesSSRService._transform_brand_to_catalog(brand_data),
                vehicles=vehicles,
                models=getattr(models_response, 'results', []) if models_response else [],
                total_count=len(vehicles),
                stats=stats
            )
            
        except Exception as error:
            print(f"Error fetching brand page data: {error}")
            return None
    
    @staticmethod
    async def get_search_page_data(
        search_query: str,
        filters: Optional[CatalogFilters] = None,
        page: int = 1,
        page_size: int = 20,
        client = None
    ) -> SearchPageData:
        """
        Get search page data with facets
        
        Args:
            search_query: Search query
            filters: Additional filters
            page: Page number
            page_size: Items per page
            client: API client instance
            
        Returns:
            SearchPageData
        """
        try:
            if not client:
                raise VehiclesAPIError("API client is required")
            
            # Prepare search filters
            search_filters = filters or CatalogFilters()
            search_filters.search = search_query
            
            # Get vehicles and brands in parallel
            vehicles_task = VehiclesSSRService.get_vehicles_for_catalog(
                search_filters, page, page_size, client
            )
            brands_task = BrandsService(client._client).list_async(page_size=50)
            
            try:
                vehicles_data, brands_response = await asyncio.gather(
                    vehicles_task, brands_task, return_exceptions=True
                )
            except Exception:
                vehicles_data = await vehicles_task
                brands_response = None
            
            # Generate suggestions
            suggestions = VehiclesSSRService._generate_search_suggestions(
                search_query, 
                getattr(brands_response, 'results', []) if brands_response else []
            )
            
            # Generate facets
            facets = await VehiclesSSRService._generate_search_facets()
            
            return SearchPageData(
                vehicles=vehicles_data.vehicles,
                filters=search_filters,
                suggestions=suggestions,
                facets=facets
            )
            
        except Exception as error:
            print(f"Error fetching search page data: {error}")
            return SearchPageData(
                vehicles=[],
                filters=CatalogFilters(),
                suggestions=[],
                facets=SearchFacets()
            )
    
    # ===============================
    # Utility Helpers
    # ===============================
    
    @staticmethod
    def _camel_to_snake(name: str) -> str:
        """Convert camelCase to snake_case"""
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
    
    @staticmethod
    def _snake_to_camel(name: str) -> str:
        """Convert snake_case to camelCase"""
        components = name.split('_')
        return components[0] + ''.join(x.capitalize() for x in components[1:])
    
    @staticmethod
    def convert_filters_to_api_params(params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert frontend filters to API parameters with case conversion
        
        Args:
            params: Frontend parameters
            
        Returns:
            API parameters
        """
        converted = {}
        
        for key, value in params.items():
            # Skip empty values
            if value in ('', None):
                continue
            
            # Special mappings
            special_mappings = {
                'make': 'brand_code',
            }
            
            # Skip frontend-only parameters
            frontend_only_params = [
                'features', 'conditions', 'radius', 'dealer_ids'
            ]
            
            if key in frontend_only_params:
                continue
            
            # Use special mapping or convert camelCase to snake_case
            api_key = special_mappings.get(key, VehiclesSSRService._camel_to_snake(key))
            converted[api_key] = value
        
        return converted
    
    # ===============================
    # Transformation Helpers
    # ===============================
    
    @staticmethod
    def _transform_vehicle_to_catalog(vehicle_data: Any) -> CatalogVehicle:
        """Transform API vehicle data to catalog vehicle"""
        # Extract data safely
        vehicle_id = getattr(vehicle_data, 'id', None)
        listing_id = getattr(vehicle_data, 'listing_id', None) or str(vehicle_id) if vehicle_id else ""
        brand_name = getattr(vehicle_data, 'brand_name', None)
        model_name = getattr(vehicle_data, 'model_name', None)
        year = getattr(vehicle_data, 'year', None)
        price = getattr(vehicle_data, 'price', None)
        mileage = getattr(vehicle_data, 'mileage', None)
        
        # Create catalog vehicle
        catalog_vehicle = CatalogVehicle(
            id=str(vehicle_id) if vehicle_id else None,
            listing_id=listing_id,
            brand_name=brand_name,
            model_name=model_name,
            year=year,
            price=float(price) if price else None,
            original_price=getattr(vehicle_data, 'original_price', None),
            mileage=int(mileage) if mileage else None,
            trim=getattr(vehicle_data, 'trim', None),
            condition=getattr(vehicle_data, 'condition', None),
            features=getattr(vehicle_data, 'features', []) or [],
            photos=getattr(vehicle_data, 'photos', []) or []
        )
        
        # Set primary image
        photos = catalog_vehicle.photos
        if photos and len(photos) > 0:
            first_photo = photos[0]
            if isinstance(first_photo, dict):
                catalog_vehicle.primary_image_url = first_photo.get('url')
                catalog_vehicle.thumbnail_url = first_photo.get('thumbnail_url')
        
        # Calculate condition score
        catalog_vehicle.condition_score = VehiclesSSRService._calculate_condition_score(catalog_vehicle)
        
        return catalog_vehicle
    
    @staticmethod
    def _transform_brand_to_catalog(brand_data: Any) -> CatalogBrand:
        """Transform API brand data to catalog brand"""
        return CatalogBrand(
            id=getattr(brand_data, 'id', None),
            name=getattr(brand_data, 'name', None),
            code=getattr(brand_data, 'code', None),
            logo_url=getattr(brand_data, 'logo_url', None),
            vehicle_count=getattr(brand_data, 'vehicle_count', 0),
            is_featured=False
        )
    
    @staticmethod
    def _calculate_condition_score(vehicle: CatalogVehicle) -> int:
        """Calculate condition score based on available data"""
        score = 50  # Base score
        
        if vehicle.year and vehicle.year > 2020:
            score += 20
        if vehicle.mileage and vehicle.mileage < 50000:
            score += 15
        if vehicle.photos and len(vehicle.photos) > 5:
            score += 10
        
        return min(100, max(0, score))
    
    @staticmethod
    def _generate_search_suggestions(
        query: str, 
        brands: List[Any]
    ) -> List[SearchSuggestion]:
        """Generate search suggestions based on query and brands"""
        suggestions = []
        
        if len(query) < 2:
            return suggestions
        
        query_lower = query.lower()
        
        # Add brand suggestions
        for brand in brands[:5]:  # Limit to 5 suggestions
            brand_name = getattr(brand, 'name', '')
            if brand_name and isinstance(brand_name, str) and query_lower in brand_name.lower():
                suggestions.append(SearchSuggestion(
                    type='make',
                    value=getattr(brand, 'code', ''),
                    label=brand_name,
                    count=getattr(brand, 'vehicle_count', None)
                ))
        
        return suggestions
    
    @staticmethod
    async def _generate_search_facets() -> SearchFacets:
        """Generate search facets for filtering"""
        # This would typically make additional API calls to get facet data
        # For now, return empty facets
        return SearchFacets()
    
    @staticmethod
    def _get_empty_vehicle_page_data() -> VehiclePageData:
        """Get empty vehicle page data for error cases"""
        return VehiclePageData(
            vehicles=[],
            total_count=0,
            current_page=1,
            total_pages=0,
            has_next=False,
            has_previous=False
        )
    
    # ===============================
    # SEO Helpers
    # ===============================
    
    @staticmethod
    def generate_vehicle_seo(vehicle: CatalogVehicle) -> SEOMetadata:
        """Generate SEO metadata for vehicle pages"""
        title = f"{vehicle.display_name} - {vehicle.formatted_price} | CARAPIS"
        description = f"{vehicle.display_name} for sale. "
        
        if vehicle.mileage:
            description += f"{vehicle.mileage:,} miles. "
        if vehicle.condition:
            description += f"Condition: {vehicle.condition}. "
        description += "View photos and details."
        
        return SEOMetadata(
            title=title,
            description=description,
            og_title=title,
            og_description=description,
            og_image=vehicle.primary_image_url,
            og_type="product",
            twitter_card="summary_large_image",
            twitter_title=title,
            twitter_description=description,
            twitter_image=vehicle.primary_image_url
        )
    
    @staticmethod
    def generate_brand_seo(brand: CatalogBrand, vehicle_count: int) -> SEOMetadata:
        """Generate SEO metadata for brand pages"""
        title = f"{brand.name} Vehicles for Sale | CARAPIS"
        description = f"Browse {vehicle_count} {brand.name} vehicles for sale. Find your perfect {brand.name} car, truck, or SUV from trusted dealers."
        
        return SEOMetadata(
            title=title,
            description=description,
            og_title=title,
            og_description=description,
            og_image=brand.logo_url,
            og_type="website"
        )
    
    @staticmethod
    def generate_search_seo(query: str, result_count: int) -> SEOMetadata:
        """Generate SEO metadata for search pages"""
        title = f"{query} Vehicles for Sale | CARAPIS"
        description = f"{result_count} {query} vehicles found. Browse cars, trucks, and SUVs matching \"{query}\" from trusted dealers."
        
        return SEOMetadata(
            title=title,
            description=description,
            og_title=title,
            og_description=description,
            og_type="website"
        )
