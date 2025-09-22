"""
Main Vehicles API Client

Universal client that provides access to all API services.
Based on the architecture patterns from encar parser and vamcar frontend.
"""

import asyncio
from typing import Optional, Dict, Any
from pathlib import Path
import sys

# Add the generated API to Python path for imports
generated_path = Path(__file__).parent / "generated"
if str(generated_path) not in sys.path:
    sys.path.insert(0, str(generated_path))

from django_revolution_vehicles_api.client import AuthenticatedClient
from .services import (
    VehiclesService,
    BrandsService,
    SourcesService,
    StatisticsService,
    ApiService
)
from .exceptions import VehiclesAPIError, AuthenticationError, NetworkError
from .models import APIResponse


class VehiclesAPIClient:
    """
    Universal Vehicles API Client
    
    Provides clean, high-level interface to the Vehicles API.
    Manages authentication, error handling, and service access.
    
    Usage:
        client = VehiclesAPIClient(
            base_url="https://api.example.com",
            api_key="your-api-key"
        )
        
        # Sync usage
        vehicles = client.vehicles.list()
        
        # Async usage  
        vehicles = await client.vehicles.list_async()
    """
    
    def __init__(
        self,
        base_url: str,
        api_key: str,
        timeout: int = 30,
        verify_ssl: bool = True,
        headers: Optional[Dict[str, str]] = None
    ):
        """
        Initialize the Vehicles API client
        
        Args:
            base_url: Base URL of the API (e.g., "https://api.example.com")
            api_key: API key for authentication
            timeout: Request timeout in seconds
            verify_ssl: Whether to verify SSL certificates
            headers: Additional headers to send with requests
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.timeout = timeout
        self.verify_ssl = verify_ssl
        self.custom_headers = headers or {}
        
        # Initialize the generated client
        self._client = self._create_client()
        
        # Initialize services
        self.vehicles = VehiclesService(self._client)
        self.brands = BrandsService(self._client)
        self.sources = SourcesService(self._client)
        self.statistics = StatisticsService(self._client)
        self.api = ApiService(self._client)
    
    def _create_client(self) -> AuthenticatedClient:
        """Create and configure the underlying API client"""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            **self.custom_headers
        }
        
        return AuthenticatedClient(
            base_url=self.base_url,
            token=self.api_key,
            headers=headers,
            timeout=self.timeout,
            verify_ssl=self.verify_ssl
        )
    
    def set_api_key(self, api_key: str) -> None:
        """Update the API key"""
        self.api_key = api_key
        self._client = self._create_client()
        
        # Update services with new client
        self.vehicles._client = self._client
        self.brands._client = self._client
        self.sources._client = self._client
        self.statistics._client = self._client
        self.api._client = self._client
    
    def set_headers(self, headers: Dict[str, str]) -> None:
        """Update custom headers"""
        self.custom_headers.update(headers)
        self._client = self._create_client()
        
        # Update services with new client
        self.vehicles._client = self._client
        self.brands._client = self._client
        self.sources._client = self._client
        self.statistics._client = self._client
        self.api._client = self._client
    
    def set_custom_headers(self, headers: Dict[str, str]) -> None:
        """Set custom headers (alias for set_headers)"""
        self.set_headers(headers)
    
    def clear_headers(self) -> None:
        """Clear all custom headers"""
        self.custom_headers.clear()
        self._client = self._create_client()
        
        # Update services with new client
        self.vehicles._client = self._client
        self.brands._client = self._client
        self.sources._client = self._client
        self.statistics._client = self._client
        self.api._client = self._client
    
    def is_authenticated(self) -> bool:
        """Check if client is authenticated with API key"""
        return bool(self.api_key and self.api_key.strip())
    
    def get_headers(self) -> Dict[str, str]:
        """Get current headers"""
        return self._client.headers.copy() if hasattr(self._client, 'headers') else self.custom_headers.copy()
    
    async def health_check(self) -> APIResponse:
        """
        Check API health and connectivity
        
        Returns:
            APIResponse with health status
        """
        try:
            api_info = await self.api.get_info_async()
            return APIResponse.success_response(
                data={
                    "status": "healthy",
                    "api_info": api_info,
                    "base_url": self.base_url
                },
                message="API is healthy"
            )
        except Exception as e:
            return APIResponse.error_response(
                error=f"Health check failed: {str(e)}",
                details={"base_url": self.base_url}
            )
    
    def close(self) -> None:
        """Close the client and cleanup resources"""
        # The generated client doesn't require explicit cleanup
        pass
    
    async def __aenter__(self):
        """Async context manager entry"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        self.close()
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
    
    def __repr__(self) -> str:
        return f"VehiclesAPIClient(base_url='{self.base_url}')"
