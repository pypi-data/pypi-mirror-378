"""
Statistics Service

Provides high-level interface for statistics and analytics API operations.
Handles market overview, price trends, quality insights, and brand comparisons.
"""

from typing import Any, Dict, Optional
import sys
from pathlib import Path

# Add the generated API to Python path for imports
generated_path = Path(__file__).parent.parent / "generated"
if str(generated_path) not in sys.path:
    sys.path.insert(0, str(generated_path))

from django_revolution_vehicles_api.api.vehicles_api import (
    vehicles_api_v1_statistics_market_overview_retrieve,
    vehicles_api_v1_statistics_price_trends_retrieve,
    vehicles_api_v1_statistics_quality_insights_retrieve,
    vehicles_api_v1_statistics_brand_comparison_retrieve,
)

from .base import BaseService


class StatisticsService(BaseService):
    """
    Statistics Service
    
    Comprehensive service for market analytics and insights.
    Provides market overview, price trends, quality insights, and brand comparisons.
    """
    
    # ===============================
    # Market Overview
    # ===============================
    
    def get_market_overview(self, **kwargs) -> Any:
        """
        Get comprehensive market overview statistics
        
        Args:
            **kwargs: Filter parameters for market overview
            
        Returns:
            Market overview statistics
        """
        return self._make_sync_from_async(self.get_market_overview_async)(**kwargs)
    
    async def get_market_overview_async(self, **kwargs) -> Any:
        """Async version of get_market_overview()"""
        query_params = self._build_query_params(kwargs)
        
        return await self._execute_async(
            lambda: vehicles_api_v1_statistics_market_overview_retrieve.asyncio(
                client=self._client,
                **query_params
            )
        )
    
    # ===============================
    # Price Trends
    # ===============================
    
    def get_price_trends(
        self,
        brand: Optional[str] = None,
        model: Optional[str] = None,
        year_min: Optional[int] = None,
        year_max: Optional[int] = None,
        **kwargs
    ) -> Any:
        """
        Get price trend analysis
        
        Args:
            brand: Brand code to filter by
            model: Model code to filter by
            year_min: Minimum year
            year_max: Maximum year
            **kwargs: Additional filter parameters
            
        Returns:
            Price trend analysis
        """
        return self._make_sync_from_async(self.get_price_trends_async)(
            brand, model, year_min, year_max, **kwargs
        )
    
    async def get_price_trends_async(
        self,
        brand: Optional[str] = None,
        model: Optional[str] = None,
        year_min: Optional[int] = None,
        year_max: Optional[int] = None,
        **kwargs
    ) -> Any:
        """Async version of get_price_trends()"""
        query_params = {}
        
        if brand is not None:
            query_params['brand'] = brand
        if model is not None:
            query_params['model'] = model
        if year_min is not None:
            query_params['year_min'] = year_min
        if year_max is not None:
            query_params['year_max'] = year_max
        
        query_params.update(kwargs)
        query_params = self._build_query_params(query_params)
        
        return await self._execute_async(
            lambda: vehicles_api_v1_statistics_price_trends_retrieve.asyncio(
                client=self._client,
                **query_params
            )
        )
    
    # ===============================
    # Quality Insights
    # ===============================
    
    def get_quality_insights(
        self,
        brand: Optional[str] = None,
        model: Optional[str] = None,
        **kwargs
    ) -> Any:
        """
        Get quality insights and investment recommendations
        
        Args:
            brand: Brand code to filter by
            model: Model code to filter by
            **kwargs: Additional filter parameters
            
        Returns:
            Quality insights and recommendations
        """
        return self._make_sync_from_async(self.get_quality_insights_async)(brand, model, **kwargs)
    
    async def get_quality_insights_async(
        self,
        brand: Optional[str] = None,
        model: Optional[str] = None,
        **kwargs
    ) -> Any:
        """Async version of get_quality_insights()"""
        query_params = {}
        
        if brand is not None:
            query_params['brand'] = brand
        if model is not None:
            query_params['model'] = model
        
        query_params.update(kwargs)
        query_params = self._build_query_params(query_params)
        
        return await self._execute_async(
            lambda: vehicles_api_v1_statistics_quality_insights_retrieve.asyncio(
                client=self._client,
                **query_params
            )
        )
    
    # ===============================
    # Brand Comparison
    # ===============================
    
    def get_brand_comparison(
        self,
        brands: Optional[str] = None,
        **kwargs
    ) -> Any:
        """
        Get brand comparison statistics
        
        Args:
            brands: Comma-separated list of brand codes to compare
            **kwargs: Additional filter parameters
            
        Returns:
            Brand comparison statistics
        """
        return self._make_sync_from_async(self.get_brand_comparison_async)(brands, **kwargs)
    
    async def get_brand_comparison_async(
        self,
        brands: Optional[str] = None,
        **kwargs
    ) -> Any:
        """Async version of get_brand_comparison()"""
        query_params = {}
        
        if brands is not None:
            query_params['brands'] = brands
        
        query_params.update(kwargs)
        query_params = self._build_query_params(query_params)
        
        return await self._execute_async(
            lambda: vehicles_api_v1_statistics_brand_comparison_retrieve.asyncio(
                client=self._client,
                **query_params
            )
        )
    
    # ===============================
    # Utility Methods
    # ===============================
    
    def compare_brands(self, brand_codes: list[str], **kwargs) -> Any:
        """
        Compare multiple brands
        
        Args:
            brand_codes: List of brand codes to compare
            **kwargs: Additional filter parameters
            
        Returns:
            Brand comparison statistics
        """
        brands_param = ",".join(brand_codes)
        return self.get_brand_comparison(brands_param, **kwargs)
    
    async def compare_brands_async(self, brand_codes: list[str], **kwargs) -> Any:
        """Async version of compare_brands()"""
        brands_param = ",".join(brand_codes)
        return await self.get_brand_comparison_async(brands_param, **kwargs)
    
    def get_price_trends_by_brand(self, brand_code: str, **kwargs) -> Any:
        """
        Get price trends for a specific brand
        
        Args:
            brand_code: Brand code
            **kwargs: Additional filter parameters
            
        Returns:
            Price trends for the brand
        """
        return self.get_price_trends(brand=brand_code, **kwargs)
    
    async def get_price_trends_by_brand_async(self, brand_code: str, **kwargs) -> Any:
        """Async version of get_price_trends_by_brand()"""
        return await self.get_price_trends_async(brand=brand_code, **kwargs)
    
    def get_quality_insights_by_brand(self, brand_code: str, **kwargs) -> Any:
        """
        Get quality insights for a specific brand
        
        Args:
            brand_code: Brand code
            **kwargs: Additional filter parameters
            
        Returns:
            Quality insights for the brand
        """
        return self.get_quality_insights(brand=brand_code, **kwargs)
    
    async def get_quality_insights_by_brand_async(self, brand_code: str, **kwargs) -> Any:
        """Async version of get_quality_insights_by_brand()"""
        return await self.get_quality_insights_async(brand=brand_code, **kwargs)
    
    def get_model_price_trends(self, brand_code: str, model_code: str, **kwargs) -> Any:
        """
        Get price trends for a specific model
        
        Args:
            brand_code: Brand code
            model_code: Model code
            **kwargs: Additional filter parameters
            
        Returns:
            Price trends for the model
        """
        return self.get_price_trends(brand=brand_code, model=model_code, **kwargs)
    
    async def get_model_price_trends_async(self, brand_code: str, model_code: str, **kwargs) -> Any:
        """Async version of get_model_price_trends()"""
        return await self.get_price_trends_async(brand=brand_code, model=model_code, **kwargs)
    
    def get_model_quality_insights(self, brand_code: str, model_code: str, **kwargs) -> Any:
        """
        Get quality insights for a specific model
        
        Args:
            brand_code: Brand code
            model_code: Model code
            **kwargs: Additional filter parameters
            
        Returns:
            Quality insights for the model
        """
        return self.get_quality_insights(brand=brand_code, model=model_code, **kwargs)
    
    async def get_model_quality_insights_async(self, brand_code: str, model_code: str, **kwargs) -> Any:
        """Async version of get_model_quality_insights()"""
        return await self.get_quality_insights_async(brand=brand_code, model=model_code, **kwargs)
