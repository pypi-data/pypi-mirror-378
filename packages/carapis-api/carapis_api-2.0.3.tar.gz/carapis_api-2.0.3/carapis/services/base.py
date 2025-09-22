"""
Base service class with common functionality
"""

import asyncio
from typing import Any, Dict, Optional, Callable, TypeVar, Union
from functools import wraps
import sys
from pathlib import Path

# Add the generated API to Python path for imports
generated_path = Path(__file__).parent.parent / "generated"
if str(generated_path) not in sys.path:
    sys.path.insert(0, str(generated_path))

from django_revolution_vehicles_api.client import AuthenticatedClient
from django_revolution_vehicles_api.errors import UnexpectedStatus
from django_revolution_vehicles_api.types import Response

from ..exceptions import (
    VehiclesAPIError,
    handle_api_error,
    NetworkError,
    TimeoutError
)
from ..models import APIResponse, QueryParams

T = TypeVar('T')


def handle_errors(func: Callable[..., T]) -> Callable[..., T]:
    """Decorator to handle common API errors"""
    @wraps(func)
    def wrapper(*args, **kwargs) -> T:
        try:
            return func(*args, **kwargs)
        except UnexpectedStatus as e:
            raise handle_api_error(e.status_code, getattr(e, 'content', None))
        except Exception as e:
            if 'timeout' in str(e).lower():
                raise TimeoutError(f"Request timed out: {str(e)}")
            raise NetworkError(f"Network error: {str(e)}", e)
    return wrapper


def handle_errors_async(func: Callable[..., T]) -> Callable[..., T]:
    """Async decorator to handle common API errors"""
    @wraps(func)
    async def wrapper(*args, **kwargs) -> T:
        try:
            return await func(*args, **kwargs)
        except UnexpectedStatus as e:
            raise handle_api_error(e.status_code, getattr(e, 'content', None))
        except Exception as e:
            if 'timeout' in str(e).lower():
                raise TimeoutError(f"Request timed out: {str(e)}")
            raise NetworkError(f"Network error: {str(e)}", e)
    return wrapper


class BaseService:
    """
    Base service class providing common functionality for all API services.
    
    Handles:
    - Error handling and response validation
    - Sync/async method patterns
    - Query parameter building
    - Response processing
    """
    
    def __init__(self, client: AuthenticatedClient):
        self._client = client
    
    def _build_query_params(self, params: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Build query parameters, filtering out None values
        
        Args:
            params: Dictionary of parameters
            
        Returns:
            Cleaned dictionary with non-None values
        """
        if not params:
            return {}
        
        return {k: v for k, v in params.items() if v is not None}
    
    def _process_response(self, response: Response) -> Any:
        """
        Process API response and extract data
        
        Args:
            response: Raw API response
            
        Returns:
            Processed response data
            
        Raises:
            VehiclesAPIError: If response indicates an error
        """
        if not response:
            raise VehiclesAPIError("No response received from API")
        
        if response.status_code >= 400:
            raise handle_api_error(response.status_code, response.parsed)
        
        return response.parsed
    
    @handle_errors
    def _execute_sync(self, api_call: Callable[[], Response]) -> Any:
        """
        Execute synchronous API call with error handling
        
        Args:
            api_call: Function that makes the API call
            
        Returns:
            Processed response data
        """
        response = api_call()
        return self._process_response(response)
    
    @handle_errors_async
    async def _execute_async(self, api_call: Callable[[], Response]) -> Any:
        """
        Execute asynchronous API call with error handling
        
        Args:
            api_call: Async function that makes the API call
            
        Returns:
            Processed response data
        """
        response = await api_call()
        return self._process_response(response)
    
    def _make_sync_from_async(self, async_func: Callable[..., Any]) -> Callable[..., Any]:
        """
        Create synchronous version of async function
        
        Args:
            async_func: Async function to wrap
            
        Returns:
            Synchronous wrapper function
        """
        def sync_wrapper(*args, **kwargs):
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # If we're already in an event loop, we can't use run()
                    # This is a limitation - sync methods won't work in async contexts
                    raise RuntimeError(
                        "Cannot call synchronous method from within an async context. "
                        "Use the async version instead (method name ending with '_async')"
                    )
                return loop.run_until_complete(async_func(*args, **kwargs))
            except RuntimeError:
                # No event loop running, create a new one
                return asyncio.run(async_func(*args, **kwargs))
        
        return sync_wrapper
    
    def _validate_required_params(self, params: Dict[str, Any], required: list[str]) -> None:
        """
        Validate that required parameters are present
        
        Args:
            params: Parameters dictionary
            required: List of required parameter names
            
        Raises:
            VehiclesAPIError: If required parameters are missing
        """
        missing = [param for param in required if param not in params or params[param] is None]
        if missing:
            raise VehiclesAPIError(f"Missing required parameters: {', '.join(missing)}")
    
    def _format_list_param(self, value: Union[str, list[str]]) -> str:
        """
        Format list parameter as comma-separated string
        
        Args:
            value: String or list of strings
            
        Returns:
            Comma-separated string
        """
        if isinstance(value, list):
            return ",".join(str(v) for v in value)
        return str(value)
