"""
Brands Service

Provides high-level interface for brand-related API operations.
Handles brand listing, details, models, and vehicle relationships.
"""

from typing import Any, Dict, Optional
import sys
from pathlib import Path

# Add the generated API to Python path for imports
generated_path = Path(__file__).parent.parent / "generated"
if str(generated_path) not in sys.path:
    sys.path.insert(0, str(generated_path))

from django_revolution_vehicles_api.api.vehicles_api import (
    vehicles_api_v1_brands_list,
    vehicles_api_v1_brands_retrieve,
    vehicles_api_v1_brands_cache_info_retrieve,
    vehicles_api_v1_brands_models_list,
    vehicles_api_v1_brands_models_retrieve,
    vehicles_api_v1_brands_models_cache_info_retrieve,
    vehicles_api_v1_brands_vehicles_list,
    vehicles_api_v1_brands_vehicles_retrieve,
    vehicles_api_v1_brands_vehicles_cache_info_retrieve,
    vehicles_api_v1_brands_models_vehicles_list,
    vehicles_api_v1_brands_models_vehicles_retrieve,
    vehicles_api_v1_brands_models_vehicles_cache_info_retrieve,
)

from .base import BaseService
from ..models import PaginationParams, BrandCode, ModelCode, VehicleFilter


class BrandsService(BaseService):
    """
    Brands Service
    
    Comprehensive service for managing brands and their relationships.
    Provides access to brands, models, and associated vehicles.
    """
    
    # ===============================
    # Brand Operations
    # ===============================
    
    def list(self, pagination: Optional[PaginationParams] = None, **kwargs) -> Any:
        """
        Get paginated list of brands
        
        Args:
            pagination: Pagination parameters
            **kwargs: Additional query parameters
            
        Returns:
            Paginated list of brands
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
            lambda: vehicles_api_v1_brands_list.asyncio(
                client=self._client,
                **query_params
            )
        )
    
    def get(self, brand_code: BrandCode) -> Any:
        """
        Get brand by code with complete details
        
        Args:
            brand_code: Brand code
            
        Returns:
            Brand details
        """
        return self._make_sync_from_async(self.get_async)(brand_code)
    
    async def get_async(self, brand_code: BrandCode) -> Any:
        """Async version of get()"""
        self._validate_required_params({"brand_code": brand_code}, ["brand_code"])
        
        return await self._execute_async(
            lambda: vehicles_api_v1_brands_retrieve.asyncio(
                client=self._client,
                brand_code=brand_code
            )
        )
    
    def get_cache_info(self) -> Any:
        """
        Get brands cache information
        
        Returns:
            Cache information
        """
        return self._make_sync_from_async(self.get_cache_info_async)()
    
    async def get_cache_info_async(self) -> Any:
        """Async version of get_cache_info()"""
        return await self._execute_async(
            lambda: vehicles_api_v1_brands_cache_info_retrieve.asyncio(
                client=self._client
            )
        )
    
    # ===============================
    # Brand Models Operations
    # ===============================
    
    def get_models(
        self,
        brand_code: BrandCode,
        pagination: Optional[PaginationParams] = None,
        **kwargs
    ) -> Any:
        """
        Get models for a specific brand
        
        Args:
            brand_code: Brand code
            pagination: Pagination parameters
            **kwargs: Additional query parameters
            
        Returns:
            List of models for the brand
        """
        return self._make_sync_from_async(self.get_models_async)(brand_code, pagination, **kwargs)
    
    async def get_models_async(
        self,
        brand_code: BrandCode,
        pagination: Optional[PaginationParams] = None,
        **kwargs
    ) -> Any:
        """Async version of get_models()"""
        self._validate_required_params({"brand_code": brand_code}, ["brand_code"])
        
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
            lambda: vehicles_api_v1_brands_models_list.asyncio(
                client=self._client,
                brand_code=brand_code,
                **query_params
            )
        )
    
    def get_model(self, brand_code: BrandCode, model_code: ModelCode) -> Any:
        """
        Get specific model details
        
        Args:
            brand_code: Brand code
            model_code: Model code
            
        Returns:
            Model details
        """
        return self._make_sync_from_async(self.get_model_async)(brand_code, model_code)
    
    async def get_model_async(self, brand_code: BrandCode, model_code: ModelCode) -> Any:
        """Async version of get_model()"""
        self._validate_required_params(
            {"brand_code": brand_code, "model_code": model_code},
            ["brand_code", "model_code"]
        )
        
        return await self._execute_async(
            lambda: vehicles_api_v1_brands_models_retrieve.asyncio(
                client=self._client,
                brand_code=brand_code,
                model_code=model_code
            )
        )
    
    def get_models_cache_info(self, brand_code: BrandCode) -> Any:
        """
        Get models cache information for a brand
        
        Args:
            brand_code: Brand code
            
        Returns:
            Cache information
        """
        return self._make_sync_from_async(self.get_models_cache_info_async)(brand_code)
    
    async def get_models_cache_info_async(self, brand_code: BrandCode) -> Any:
        """Async version of get_models_cache_info()"""
        self._validate_required_params({"brand_code": brand_code}, ["brand_code"])
        
        return await self._execute_async(
            lambda: vehicles_api_v1_brands_models_cache_info_retrieve.asyncio(
                client=self._client,
                brand_code=brand_code
            )
        )
    
    # ===============================
    # Brand Vehicles Operations
    # ===============================
    
    def get_vehicles(
        self,
        brand_code: BrandCode,
        filters: Optional[VehicleFilter] = None,
        pagination: Optional[PaginationParams] = None,
        **kwargs
    ) -> Any:
        """
        Get vehicles for a specific brand
        
        Args:
            brand_code: Brand code
            filters: Vehicle filter parameters
            pagination: Pagination parameters
            **kwargs: Additional query parameters
            
        Returns:
            List of vehicles for the brand
        """
        return self._make_sync_from_async(self.get_vehicles_async)(brand_code, filters, pagination, **kwargs)
    
    async def get_vehicles_async(
        self,
        brand_code: BrandCode,
        filters: Optional[VehicleFilter] = None,
        pagination: Optional[PaginationParams] = None,
        **kwargs
    ) -> Any:
        """Async version of get_vehicles()"""
        self._validate_required_params({"brand_code": brand_code}, ["brand_code"])
        
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
            lambda: vehicles_api_v1_brands_vehicles_list.asyncio(
                client=self._client,
                brand_code=brand_code,
                **query_params
            )
        )
    
    def get_vehicle(self, brand_code: BrandCode, vehicle_id: str) -> Any:
        """
        Get specific vehicle from a brand
        
        Args:
            brand_code: Brand code
            vehicle_id: Vehicle ID
            
        Returns:
            Vehicle details
        """
        return self._make_sync_from_async(self.get_vehicle_async)(brand_code, vehicle_id)
    
    async def get_vehicle_async(self, brand_code: BrandCode, vehicle_id: str) -> Any:
        """Async version of get_vehicle()"""
        self._validate_required_params(
            {"brand_code": brand_code, "vehicle_id": vehicle_id},
            ["brand_code", "vehicle_id"]
        )
        
        return await self._execute_async(
            lambda: vehicles_api_v1_brands_vehicles_retrieve.asyncio(
                client=self._client,
                brand_code=brand_code,
                id=vehicle_id
            )
        )
    
    def get_vehicles_cache_info(self, brand_code: BrandCode) -> Any:
        """
        Get vehicles cache information for a brand
        
        Args:
            brand_code: Brand code
            
        Returns:
            Cache information
        """
        return self._make_sync_from_async(self.get_vehicles_cache_info_async)(brand_code)
    
    async def get_vehicles_cache_info_async(self, brand_code: BrandCode) -> Any:
        """Async version of get_vehicles_cache_info()"""
        self._validate_required_params({"brand_code": brand_code}, ["brand_code"])
        
        return await self._execute_async(
            lambda: vehicles_api_v1_brands_vehicles_cache_info_retrieve.asyncio(
                client=self._client,
                brand_code=brand_code
            )
        )
    
    # ===============================
    # Brand Model Vehicles Operations
    # ===============================
    
    def get_model_vehicles(
        self,
        brand_code: BrandCode,
        model_code: ModelCode,
        filters: Optional[VehicleFilter] = None,
        pagination: Optional[PaginationParams] = None,
        **kwargs
    ) -> Any:
        """
        Get vehicles for a specific brand and model
        
        Args:
            brand_code: Brand code
            model_code: Model code
            filters: Vehicle filter parameters
            pagination: Pagination parameters
            **kwargs: Additional query parameters
            
        Returns:
            List of vehicles for the brand and model
        """
        return self._make_sync_from_async(self.get_model_vehicles_async)(
            brand_code, model_code, filters, pagination, **kwargs
        )
    
    async def get_model_vehicles_async(
        self,
        brand_code: BrandCode,
        model_code: ModelCode,
        filters: Optional[VehicleFilter] = None,
        pagination: Optional[PaginationParams] = None,
        **kwargs
    ) -> Any:
        """Async version of get_model_vehicles()"""
        self._validate_required_params(
            {"brand_code": brand_code, "model_code": model_code},
            ["brand_code", "model_code"]
        )
        
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
            lambda: vehicles_api_v1_brands_models_vehicles_list.asyncio(
                client=self._client,
                brand_code=brand_code,
                model_code=model_code,
                **query_params
            )
        )
    
    def get_model_vehicle(
        self,
        brand_code: BrandCode,
        model_code: ModelCode,
        vehicle_id: str
    ) -> Any:
        """
        Get specific vehicle from a brand and model
        
        Args:
            brand_code: Brand code
            model_code: Model code
            vehicle_id: Vehicle ID
            
        Returns:
            Vehicle details
        """
        return self._make_sync_from_async(self.get_model_vehicle_async)(brand_code, model_code, vehicle_id)
    
    async def get_model_vehicle_async(
        self,
        brand_code: BrandCode,
        model_code: ModelCode,
        vehicle_id: str
    ) -> Any:
        """Async version of get_model_vehicle()"""
        self._validate_required_params(
            {"brand_code": brand_code, "model_code": model_code, "vehicle_id": vehicle_id},
            ["brand_code", "model_code", "vehicle_id"]
        )
        
        return await self._execute_async(
            lambda: vehicles_api_v1_brands_models_vehicles_retrieve.asyncio(
                client=self._client,
                brand_code=brand_code,
                model_code=model_code,
                id=vehicle_id
            )
        )
    
    def get_model_vehicles_cache_info(self, brand_code: BrandCode, model_code: ModelCode) -> Any:
        """
        Get vehicles cache information for a brand and model
        
        Args:
            brand_code: Brand code
            model_code: Model code
            
        Returns:
            Cache information
        """
        return self._make_sync_from_async(self.get_model_vehicles_cache_info_async)(brand_code, model_code)
    
    async def get_model_vehicles_cache_info_async(self, brand_code: BrandCode, model_code: ModelCode) -> Any:
        """Async version of get_model_vehicles_cache_info()"""
        self._validate_required_params(
            {"brand_code": brand_code, "model_code": model_code},
            ["brand_code", "model_code"]
        )
        
        return await self._execute_async(
            lambda: vehicles_api_v1_brands_models_vehicles_cache_info_retrieve.asyncio(
                client=self._client,
                brand_code=brand_code,
                model_code=model_code
            )
        )
