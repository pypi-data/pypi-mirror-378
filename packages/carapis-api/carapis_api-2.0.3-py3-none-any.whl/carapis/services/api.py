"""
API Service

Provides high-level interface for general API operations and utilities.
Handles API information, health checks, testing endpoints, and image proxy.
"""

from typing import Any, Dict, Optional
import sys
from pathlib import Path

# Add the generated API to Python path for imports
generated_path = Path(__file__).parent.parent / "generated"
if str(generated_path) not in sys.path:
    sys.path.insert(0, str(generated_path))

from django_revolution_vehicles_api.api.vehicles_api import (
    vehicles_api_v1_retrieve,
    vehicles_api_v1_urls_test_retrieve,
    vehicles_api_image_retrieve,
)

from .base import BaseService


class ApiService(BaseService):
    """
    API Service
    
    Service for general API operations and utilities.
    Provides API information, health checks, and testing endpoints.
    """
    
    # ===============================
    # API Information
    # ===============================
    
    def get_info(self) -> Any:
        """
        Get API information and features
        
        Returns:
            API information including version, features, endpoints, and rate limits
        """
        return self._make_sync_from_async(self.get_info_async)()
    
    async def get_info_async(self) -> Any:
        """Async version of get_info()"""
        return await self._execute_async(
            lambda: vehicles_api_v1_retrieve.asyncio(
                client=self._client
            )
        )
    
    def test_urls(self) -> Any:
        """
        Test all API URLs and their status
        
        Returns:
            Status of all API endpoints
        """
        return self._make_sync_from_async(self.test_urls_async)()
    
    async def test_urls_async(self) -> Any:
        """Async version of test_urls()"""
        return await self._execute_async(
            lambda: vehicles_api_v1_urls_test_retrieve.asyncio(
                client=self._client
            )
        )
    
    # ===============================
    # Image Proxy
    # ===============================
    
    def get_image(self, image_uuid: str) -> Any:
        """
        Get image by UUID through proxy
        
        Args:
            image_uuid: UUID of the image
            
        Returns:
            Image data or redirect URL
        """
        return self._make_sync_from_async(self.get_image_async)(image_uuid)
    
    async def get_image_async(self, image_uuid: str) -> Any:
        """Async version of get_image()"""
        self._validate_required_params({"image_uuid": image_uuid}, ["image_uuid"])
        
        return await self._execute_async(
            lambda: vehicles_api_image_retrieve.asyncio(
                client=self._client,
                image_uuid=image_uuid
            )
        )
    
    # ===============================
    # Utility Methods
    # ===============================
    
    def health_check(self) -> Dict[str, Any]:
        """
        Check API health and availability
        
        Returns:
            Health status information
        """
        return self._make_sync_from_async(self.health_check_async)()
    
    async def health_check_async(self) -> Dict[str, Any]:
        """Async version of health_check()"""
        try:
            api_info = await self.get_info_async()
            return {
                "status": "healthy",
                "api_info": api_info,
                "timestamp": self._get_current_timestamp()
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": self._get_current_timestamp()
            }
    
    def get_capabilities(self) -> Dict[str, Any]:
        """
        Get API capabilities and features
        
        Returns:
            API capabilities including features, endpoints, rate limits, and data sources
        """
        return self._make_sync_from_async(self.get_capabilities_async)()
    
    async def get_capabilities_async(self) -> Dict[str, Any]:
        """Async version of get_capabilities()"""
        api_info = await self.get_info_async()
        
        return {
            "features": getattr(api_info, 'features', []),
            "endpoints": getattr(api_info, 'endpoints', {}),
            "rate_limits": getattr(api_info, 'rate_limits', {}),
            "data_sources": getattr(api_info, 'data_sources', [])
        }
    
    def get_version(self) -> str:
        """
        Get API version
        
        Returns:
            API version string
        """
        return self._make_sync_from_async(self.get_version_async)()
    
    async def get_version_async(self) -> str:
        """Async version of get_version()"""
        api_info = await self.get_info_async()
        return getattr(api_info, 'version', 'unknown')
    
    def get_rate_limits(self) -> Dict[str, Any]:
        """
        Get API rate limits
        
        Returns:
            Rate limit information
        """
        return self._make_sync_from_async(self.get_rate_limits_async)()
    
    async def get_rate_limits_async(self) -> Dict[str, Any]:
        """Async version of get_rate_limits()"""
        api_info = await self.get_info_async()
        return getattr(api_info, 'rate_limits', {})
    
    def get_data_sources(self) -> list[Dict[str, Any]]:
        """
        Get available data sources
        
        Returns:
            List of available data sources
        """
        return self._make_sync_from_async(self.get_data_sources_async)()
    
    async def get_data_sources_async(self) -> list[Dict[str, Any]]:
        """Async version of get_data_sources()"""
        api_info = await self.get_info_async()
        return getattr(api_info, 'data_sources', [])
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp in ISO format"""
        from datetime import datetime
        return datetime.now().isoformat()
