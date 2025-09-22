"""
Vehicles Service

Provides high-level interface for vehicle-related API operations.
Handles vehicle listing, details, search, export, and statistics.
"""

from typing import Any, Dict, Optional, Union, List
import sys
from pathlib import Path

# Add the generated API to Python path for imports
generated_path = Path(__file__).parent.parent / "generated"
if str(generated_path) not in sys.path:
    sys.path.insert(0, str(generated_path))

from django_revolution_vehicles_api.api.vehicles_api import (
    vehicles_api_v1_vehicles_list,
    vehicles_api_v1_vehicles_retrieve,
    vehicles_api_v1_vehicles_similar_retrieve,
    vehicles_api_v1_vehicles_statistics_retrieve,
    vehicles_api_v1_vehicles_cache_info_retrieve,
    vehicles_api_v1_vehicles_export_csv_retrieve,
    vehicles_api_v1_vehicles_export_excel_retrieve,
    vehicles_api_v1_vehicles_export_json_retrieve,
)

from .base import BaseService
from ..models import VehicleFilter, PaginationParams, ExportFormat, VehicleID


class VehiclesService(BaseService):
    """
    Vehicles Service
    
    Comprehensive service for managing vehicles with full CRUD operations.
    Provides advanced filtering, search, export, and analytics capabilities.
    """
    
    # ===============================
    # Main Vehicle Operations
    # ===============================
    
    def list(
        self,
        filters: Optional[VehicleFilter] = None,
        pagination: Optional[PaginationParams] = None,
        **kwargs
    ) -> Any:
        """
        Get paginated list of vehicles with advanced filtering
        
        Args:
            filters: Vehicle filter parameters
            pagination: Pagination parameters
            **kwargs: Additional query parameters
            
        Returns:
            Paginated list of vehicles
        """
        return self._make_sync_from_async(self.list_async)(filters, pagination, **kwargs)
    
    async def list_async(
        self,
        filters: Optional[VehicleFilter] = None,
        pagination: Optional[PaginationParams] = None,
        **kwargs
    ) -> Any:
        """Async version of list()"""
        query_params = {}
        
        # Add filter parameters
        if filters:
            query_params.update(filters.to_dict())
        
        # Add pagination parameters
        if pagination:
            if pagination.page is not None:
                query_params['page'] = pagination.page
            if pagination.page_size is not None:
                query_params['page_size'] = pagination.page_size
            if pagination.limit is not None:
                query_params['limit'] = pagination.limit
            if pagination.offset is not None:
                query_params['offset'] = pagination.offset
        
        # Add additional parameters
        query_params.update(kwargs)
        
        # Clean parameters
        query_params = self._build_query_params(query_params)
        
        return await self._execute_async(
            lambda: vehicles_api_v1_vehicles_list.asyncio(
                client=self._client,
                **query_params
            )
        )
    
    def get(self, vehicle_id: VehicleID) -> Any:
        """
        Get vehicle by ID with complete details
        
        Args:
            vehicle_id: Vehicle ID
            
        Returns:
            Vehicle details
        """
        return self._make_sync_from_async(self.get_async)(vehicle_id)
    
    async def get_async(self, vehicle_id: VehicleID) -> Any:
        """Async version of get()"""
        self._validate_required_params({"vehicle_id": vehicle_id}, ["vehicle_id"])
        
        return await self._execute_async(
            lambda: vehicles_api_v1_vehicles_retrieve.asyncio(
                client=self._client,
                id=vehicle_id
            )
        )
    
    def get_similar(
        self,
        vehicle_id: VehicleID,
        limit: Optional[int] = None,
        **kwargs
    ) -> Any:
        """
        Find similar vehicles
        
        Args:
            vehicle_id: Vehicle ID to find similar vehicles for
            limit: Maximum number of similar vehicles to return
            **kwargs: Additional query parameters
            
        Returns:
            List of similar vehicles
        """
        return self._make_sync_from_async(self.get_similar_async)(vehicle_id, limit, **kwargs)
    
    async def get_similar_async(
        self,
        vehicle_id: VehicleID,
        limit: Optional[int] = None,
        **kwargs
    ) -> Any:
        """Async version of get_similar()"""
        self._validate_required_params({"vehicle_id": vehicle_id}, ["vehicle_id"])
        
        query_params = {}
        if limit is not None:
            query_params['limit'] = limit
        query_params.update(kwargs)
        
        query_params = self._build_query_params(query_params)
        
        return await self._execute_async(
            lambda: vehicles_api_v1_vehicles_similar_retrieve.asyncio(
                client=self._client,
                id=vehicle_id,
                **query_params
            )
        )
    
    # ===============================
    # Statistics & Analytics
    # ===============================
    
    def get_statistics(self, **kwargs) -> Any:
        """
        Get vehicle statistics for filtered dataset
        
        Args:
            **kwargs: Filter parameters for statistics
            
        Returns:
            Vehicle statistics
        """
        return self._make_sync_from_async(self.get_statistics_async)(**kwargs)
    
    async def get_statistics_async(self, **kwargs) -> Any:
        """Async version of get_statistics()"""
        query_params = self._build_query_params(kwargs)
        
        return await self._execute_async(
            lambda: vehicles_api_v1_vehicles_statistics_retrieve.asyncio(
                client=self._client,
                **query_params
            )
        )
    
    # ===============================
    # Export Operations
    # ===============================
    
    def export(
        self,
        format: ExportFormat,
        filters: Optional[VehicleFilter] = None,
        **kwargs
    ) -> Any:
        """
        Export vehicles in specified format
        
        Args:
            format: Export format (csv, excel, json)
            filters: Vehicle filter parameters
            **kwargs: Additional parameters
            
        Returns:
            Export data or download URL
        """
        return self._make_sync_from_async(self.export_async)(format, filters, **kwargs)
    
    async def export_async(
        self,
        format: ExportFormat,
        filters: Optional[VehicleFilter] = None,
        **kwargs
    ) -> Any:
        """Async version of export()"""
        query_params = {}
        
        if filters:
            query_params.update(filters.to_dict())
        query_params.update(kwargs)
        
        query_params = self._build_query_params(query_params)
        
        if format == ExportFormat.CSV:
            return await self._execute_async(
                lambda: vehicles_api_v1_vehicles_export_csv_retrieve.asyncio(
                    client=self._client,
                    **query_params
                )
            )
        elif format == ExportFormat.EXCEL:
            return await self._execute_async(
                lambda: vehicles_api_v1_vehicles_export_excel_retrieve.asyncio(
                    client=self._client,
                    **query_params
                )
            )
        elif format == ExportFormat.JSON:
            return await self._execute_async(
                lambda: vehicles_api_v1_vehicles_export_json_retrieve.asyncio(
                    client=self._client,
                    **query_params
                )
            )
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def export_csv(self, filters: Optional[VehicleFilter] = None, **kwargs) -> Any:
        """Export vehicles to CSV"""
        return self.export(ExportFormat.CSV, filters, **kwargs)
    
    async def export_csv_async(self, filters: Optional[VehicleFilter] = None, **kwargs) -> Any:
        """Async version of export_csv()"""
        return await self.export_async(ExportFormat.CSV, filters, **kwargs)
    
    def export_excel(self, filters: Optional[VehicleFilter] = None, **kwargs) -> Any:
        """Export vehicles to Excel"""
        return self.export(ExportFormat.EXCEL, filters, **kwargs)
    
    async def export_excel_async(self, filters: Optional[VehicleFilter] = None, **kwargs) -> Any:
        """Async version of export_excel()"""
        return await self.export_async(ExportFormat.EXCEL, filters, **kwargs)
    
    def export_json(self, filters: Optional[VehicleFilter] = None, **kwargs) -> Any:
        """Export vehicles to JSON"""
        return self.export(ExportFormat.JSON, filters, **kwargs)
    
    async def export_json_async(self, filters: Optional[VehicleFilter] = None, **kwargs) -> Any:
        """Async version of export_json()"""
        return await self.export_async(ExportFormat.JSON, filters, **kwargs)
    
    # ===============================
    # Cache Management
    # ===============================
    
    def get_cache_info(self) -> Any:
        """
        Get cache information
        
        Returns:
            Cache information
        """
        return self._make_sync_from_async(self.get_cache_info_async)()
    
    async def get_cache_info_async(self) -> Any:
        """Async version of get_cache_info()"""
        return await self._execute_async(
            lambda: vehicles_api_v1_vehicles_cache_info_retrieve.asyncio(
                client=self._client
            )
        )
    
    # ===============================
    # Utility Methods
    # ===============================
    
    def search(
        self,
        query: str,
        filters: Optional[VehicleFilter] = None,
        pagination: Optional[PaginationParams] = None,
        **kwargs
    ) -> Any:
        """
        Search vehicles with text query
        
        Args:
            query: Search query string
            filters: Additional filter parameters
            pagination: Pagination parameters
            **kwargs: Additional parameters
            
        Returns:
            Search results
        """
        if not filters:
            filters = VehicleFilter()
        filters.search = query
        
        return self.list(filters, pagination, **kwargs)
    
    async def search_async(
        self,
        query: str,
        filters: Optional[VehicleFilter] = None,
        pagination: Optional[PaginationParams] = None,
        **kwargs
    ) -> Any:
        """Async version of search()"""
        if not filters:
            filters = VehicleFilter()
        filters.search = query
        
        return await self.list_async(filters, pagination, **kwargs)
    
    def get_by_brand(
        self,
        brand_code: str,
        filters: Optional[VehicleFilter] = None,
        **kwargs
    ) -> Any:
        """Get vehicles by brand"""
        if not filters:
            filters = VehicleFilter()
        filters.brand = brand_code
        
        return self.list(filters, **kwargs)
    
    async def get_by_brand_async(
        self,
        brand_code: str,
        filters: Optional[VehicleFilter] = None,
        **kwargs
    ) -> Any:
        """Async version of get_by_brand()"""
        if not filters:
            filters = VehicleFilter()
        filters.brand = brand_code
        
        return await self.list_async(filters, **kwargs)
    
    def get_by_source(
        self,
        source_code: str,
        filters: Optional[VehicleFilter] = None,
        **kwargs
    ) -> Any:
        """Get vehicles by source"""
        if not filters:
            filters = VehicleFilter()
        filters.source = source_code
        
        return self.list(filters, **kwargs)
    
    async def get_by_source_async(
        self,
        source_code: str,
        filters: Optional[VehicleFilter] = None,
        **kwargs
    ) -> Any:
        """Async version of get_by_source()"""
        if not filters:
            filters = VehicleFilter()
        filters.source = source_code
        
        return await self.list_async(filters, **kwargs)
    
    def get_high_quality(
        self,
        filters: Optional[VehicleFilter] = None,
        **kwargs
    ) -> Any:
        """Get high quality vehicles (A grades only)"""
        if not filters:
            filters = VehicleFilter()
        filters.high_quality = True
        
        return self.list(filters, **kwargs)
    
    async def get_high_quality_async(
        self,
        filters: Optional[VehicleFilter] = None,
        **kwargs
    ) -> Any:
        """Async version of get_high_quality()"""
        if not filters:
            filters = VehicleFilter()
        filters.high_quality = True
        
        return await self.list_async(filters, **kwargs)
    
    def get_low_risk(
        self,
        filters: Optional[VehicleFilter] = None,
        **kwargs
    ) -> Any:
        """Get low risk vehicles"""
        if not filters:
            filters = VehicleFilter()
        filters.low_risk = True
        
        return self.list(filters, **kwargs)
    
    async def get_low_risk_async(
        self,
        filters: Optional[VehicleFilter] = None,
        **kwargs
    ) -> Any:
        """Async version of get_low_risk()"""
        if not filters:
            filters = VehicleFilter()
        filters.low_risk = True
        
        return await self.list_async(filters, **kwargs)
    
    def get_with_photos(
        self,
        filters: Optional[VehicleFilter] = None,
        **kwargs
    ) -> Any:
        """Get vehicles with photos"""
        if not filters:
            filters = VehicleFilter()
        filters.has_photos = True
        
        return self.list(filters, **kwargs)
    
    async def get_with_photos_async(
        self,
        filters: Optional[VehicleFilter] = None,
        **kwargs
    ) -> Any:
        """Async version of get_with_photos()"""
        if not filters:
            filters = VehicleFilter()
        filters.has_photos = True
        
        return await self.list_async(filters, **kwargs)
    
    def get_in_price_range(
        self,
        min_price: float,
        max_price: float,
        filters: Optional[VehicleFilter] = None,
        **kwargs
    ) -> Any:
        """Get vehicles in price range"""
        if not filters:
            filters = VehicleFilter()
        filters.price_min = min_price
        filters.price_max = max_price
        
        return self.list(filters, **kwargs)
    
    async def get_in_price_range_async(
        self,
        min_price: float,
        max_price: float,
        filters: Optional[VehicleFilter] = None,
        **kwargs
    ) -> Any:
        """Async version of get_in_price_range()"""
        if not filters:
            filters = VehicleFilter()
        filters.price_min = min_price
        filters.price_max = max_price
        
        return await self.list_async(filters, **kwargs)
    
    def get_by_year_range(
        self,
        min_year: int,
        max_year: int,
        filters: Optional[VehicleFilter] = None,
        **kwargs
    ) -> Any:
        """Get vehicles by year range"""
        if not filters:
            filters = VehicleFilter()
        filters.year_min = min_year
        filters.year_max = max_year
        
        return self.list(filters, **kwargs)
    
    async def get_by_year_range_async(
        self,
        min_year: int,
        max_year: int,
        filters: Optional[VehicleFilter] = None,
        **kwargs
    ) -> Any:
        """Async version of get_by_year_range()"""
        if not filters:
            filters = VehicleFilter()
        filters.year_min = min_year
        filters.year_max = max_year
        
        return await self.list_async(filters, **kwargs)
