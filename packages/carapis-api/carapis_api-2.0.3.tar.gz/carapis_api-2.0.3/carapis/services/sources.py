"""
Sources Service

Provides high-level interface for source-related API operations.
Handles source listing, details, and vehicle relationships.
"""

from typing import Any, Dict, Optional
import sys
from pathlib import Path

# Add the generated API to Python path for imports
generated_path = Path(__file__).parent.parent / "generated"
if str(generated_path) not in sys.path:
    sys.path.insert(0, str(generated_path))

from django_revolution_vehicles_api.api.vehicles_api import (
    vehicles_api_v1_sources_list,
    vehicles_api_v1_sources_retrieve,
    vehicles_api_v1_sources_cache_info_retrieve,
    vehicles_api_v1_sources_vehicles_list,
    vehicles_api_v1_sources_vehicles_retrieve,
    vehicles_api_v1_sources_vehicles_cache_info_retrieve,
)

from .base import BaseService
from ..models import PaginationParams, SourceCode, VehicleFilter


class SourcesService(BaseService):
    """
    Sources Service
    
    Comprehensive service for managing data sources and their relationships.
    Provides access to sources and associated vehicles.
    """
    
    # ===============================
    # Source Operations
    # ===============================
    
    def list(self, pagination: Optional[PaginationParams] = None, **kwargs) -> Any:
        """
        Get paginated list of sources
        
        Args:
            pagination: Pagination parameters
            **kwargs: Additional query parameters
            
        Returns:
            Paginated list of sources
        """
        return self._make_sync_from_async(self.list_async)(pagination, **kwargs)
    
    async def list_async(self, pagination: Optional[PaginationParams] = None, **kwargs) -> Any:
        """Async version of list()"""
        query_params = {}
        
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
            lambda: vehicles_api_v1_sources_list.asyncio(
                client=self._client,
                **query_params
            )
        )
    
    def get(self, source_code: SourceCode) -> Any:
        """
        Get source by code with complete details
        
        Args:
            source_code: Source code
            
        Returns:
            Source details
        """
        return self._make_sync_from_async(self.get_async)(source_code)
    
    async def get_async(self, source_code: SourceCode) -> Any:
        """Async version of get()"""
        self._validate_required_params({"source_code": source_code}, ["source_code"])
        
        return await self._execute_async(
            lambda: vehicles_api_v1_sources_retrieve.asyncio(
                client=self._client,
                source_code=source_code
            )
        )
    
    def get_cache_info(self) -> Any:
        """
        Get sources cache information
        
        Returns:
            Cache information
        """
        return self._make_sync_from_async(self.get_cache_info_async)()
    
    async def get_cache_info_async(self) -> Any:
        """Async version of get_cache_info()"""
        return await self._execute_async(
            lambda: vehicles_api_v1_sources_cache_info_retrieve.asyncio(
                client=self._client
            )
        )
    
    # ===============================
    # Source Vehicles Operations
    # ===============================
    
    def get_vehicles(
        self,
        source_code: SourceCode,
        filters: Optional[VehicleFilter] = None,
        pagination: Optional[PaginationParams] = None,
        **kwargs
    ) -> Any:
        """
        Get vehicles for a specific source
        
        Args:
            source_code: Source code
            filters: Vehicle filter parameters
            pagination: Pagination parameters
            **kwargs: Additional query parameters
            
        Returns:
            List of vehicles for the source
        """
        return self._make_sync_from_async(self.get_vehicles_async)(source_code, filters, pagination, **kwargs)
    
    async def get_vehicles_async(
        self,
        source_code: SourceCode,
        filters: Optional[VehicleFilter] = None,
        pagination: Optional[PaginationParams] = None,
        **kwargs
    ) -> Any:
        """Async version of get_vehicles()"""
        self._validate_required_params({"source_code": source_code}, ["source_code"])
        
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
            lambda: vehicles_api_v1_sources_vehicles_list.asyncio(
                client=self._client,
                source_code=source_code,
                **query_params
            )
        )
    
    def get_vehicle(self, source_code: SourceCode, vehicle_id: str) -> Any:
        """
        Get specific vehicle from a source
        
        Args:
            source_code: Source code
            vehicle_id: Vehicle ID
            
        Returns:
            Vehicle details
        """
        return self._make_sync_from_async(self.get_vehicle_async)(source_code, vehicle_id)
    
    async def get_vehicle_async(self, source_code: SourceCode, vehicle_id: str) -> Any:
        """Async version of get_vehicle()"""
        self._validate_required_params(
            {"source_code": source_code, "vehicle_id": vehicle_id},
            ["source_code", "vehicle_id"]
        )
        
        return await self._execute_async(
            lambda: vehicles_api_v1_sources_vehicles_retrieve.asyncio(
                client=self._client,
                source_code=source_code,
                id=vehicle_id
            )
        )
    
    def get_vehicles_cache_info(self, source_code: SourceCode) -> Any:
        """
        Get vehicles cache information for a source
        
        Args:
            source_code: Source code
            
        Returns:
            Cache information
        """
        return self._make_sync_from_async(self.get_vehicles_cache_info_async)(source_code)
    
    async def get_vehicles_cache_info_async(self, source_code: SourceCode) -> Any:
        """Async version of get_vehicles_cache_info()"""
        self._validate_required_params({"source_code": source_code}, ["source_code"])
        
        return await self._execute_async(
            lambda: vehicles_api_v1_sources_vehicles_cache_info_retrieve.asyncio(
                client=self._client,
                source_code=source_code
            )
        )
