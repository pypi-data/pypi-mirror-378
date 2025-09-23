from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.paginated_v1_brand_list import PaginatedV1BrandList
from ...types import UNSET, Unset
from typing import cast
from typing import Union


def _get_kwargs(
    *,
    code: Union[Unset, str] = UNSET,
    code_icontains: Union[Unset, str] = UNSET,
    country_origin: Union[Unset, str] = UNSET,
    has_models: Union[Unset, bool] = UNSET,
    has_vehicles: Union[Unset, bool] = UNSET,
    is_active: Union[Unset, bool] = UNSET,
    name_icontains: Union[Unset, str] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    search: Union[Unset, str] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["code"] = code

    params["code__icontains"] = code_icontains

    params["country_origin"] = country_origin

    params["has_models"] = has_models

    params["has_vehicles"] = has_vehicles

    params["is_active"] = is_active

    params["name__icontains"] = name_icontains

    params["page"] = page

    params["page_size"] = page_size

    params["search"] = search

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/vehicles_api/v1/brands/",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[PaginatedV1BrandList]:
    if response.status_code == 200:
        response_200 = PaginatedV1BrandList.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[PaginatedV1BrandList]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    code: Union[Unset, str] = UNSET,
    code_icontains: Union[Unset, str] = UNSET,
    country_origin: Union[Unset, str] = UNSET,
    has_models: Union[Unset, bool] = UNSET,
    has_vehicles: Union[Unset, bool] = UNSET,
    is_active: Union[Unset, bool] = UNSET,
    name_icontains: Union[Unset, str] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    search: Union[Unset, str] = UNSET,
) -> Response[PaginatedV1BrandList]:
    """List vehicle brands

     Get list of available vehicle brands

    Args:
        code (Union[Unset, str]):
        code_icontains (Union[Unset, str]):
        country_origin (Union[Unset, str]):
        has_models (Union[Unset, bool]):
        has_vehicles (Union[Unset, bool]):
        is_active (Union[Unset, bool]):
        name_icontains (Union[Unset, str]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        search (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PaginatedV1BrandList]
    """

    kwargs = _get_kwargs(
        code=code,
        code_icontains=code_icontains,
        country_origin=country_origin,
        has_models=has_models,
        has_vehicles=has_vehicles,
        is_active=is_active,
        name_icontains=name_icontains,
        page=page,
        page_size=page_size,
        search=search,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: Union[AuthenticatedClient, Client],
    code: Union[Unset, str] = UNSET,
    code_icontains: Union[Unset, str] = UNSET,
    country_origin: Union[Unset, str] = UNSET,
    has_models: Union[Unset, bool] = UNSET,
    has_vehicles: Union[Unset, bool] = UNSET,
    is_active: Union[Unset, bool] = UNSET,
    name_icontains: Union[Unset, str] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    search: Union[Unset, str] = UNSET,
) -> Optional[PaginatedV1BrandList]:
    """List vehicle brands

     Get list of available vehicle brands

    Args:
        code (Union[Unset, str]):
        code_icontains (Union[Unset, str]):
        country_origin (Union[Unset, str]):
        has_models (Union[Unset, bool]):
        has_vehicles (Union[Unset, bool]):
        is_active (Union[Unset, bool]):
        name_icontains (Union[Unset, str]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        search (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PaginatedV1BrandList
    """

    return sync_detailed(
        client=client,
        code=code,
        code_icontains=code_icontains,
        country_origin=country_origin,
        has_models=has_models,
        has_vehicles=has_vehicles,
        is_active=is_active,
        name_icontains=name_icontains,
        page=page,
        page_size=page_size,
        search=search,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    code: Union[Unset, str] = UNSET,
    code_icontains: Union[Unset, str] = UNSET,
    country_origin: Union[Unset, str] = UNSET,
    has_models: Union[Unset, bool] = UNSET,
    has_vehicles: Union[Unset, bool] = UNSET,
    is_active: Union[Unset, bool] = UNSET,
    name_icontains: Union[Unset, str] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    search: Union[Unset, str] = UNSET,
) -> Response[PaginatedV1BrandList]:
    """List vehicle brands

     Get list of available vehicle brands

    Args:
        code (Union[Unset, str]):
        code_icontains (Union[Unset, str]):
        country_origin (Union[Unset, str]):
        has_models (Union[Unset, bool]):
        has_vehicles (Union[Unset, bool]):
        is_active (Union[Unset, bool]):
        name_icontains (Union[Unset, str]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        search (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PaginatedV1BrandList]
    """

    kwargs = _get_kwargs(
        code=code,
        code_icontains=code_icontains,
        country_origin=country_origin,
        has_models=has_models,
        has_vehicles=has_vehicles,
        is_active=is_active,
        name_icontains=name_icontains,
        page=page,
        page_size=page_size,
        search=search,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
    code: Union[Unset, str] = UNSET,
    code_icontains: Union[Unset, str] = UNSET,
    country_origin: Union[Unset, str] = UNSET,
    has_models: Union[Unset, bool] = UNSET,
    has_vehicles: Union[Unset, bool] = UNSET,
    is_active: Union[Unset, bool] = UNSET,
    name_icontains: Union[Unset, str] = UNSET,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    search: Union[Unset, str] = UNSET,
) -> Optional[PaginatedV1BrandList]:
    """List vehicle brands

     Get list of available vehicle brands

    Args:
        code (Union[Unset, str]):
        code_icontains (Union[Unset, str]):
        country_origin (Union[Unset, str]):
        has_models (Union[Unset, bool]):
        has_vehicles (Union[Unset, bool]):
        is_active (Union[Unset, bool]):
        name_icontains (Union[Unset, str]):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        search (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PaginatedV1BrandList
    """

    return (
        await asyncio_detailed(
            client=client,
            code=code,
            code_icontains=code_icontains,
            country_origin=country_origin,
            has_models=has_models,
            has_vehicles=has_vehicles,
            is_active=is_active,
            name_icontains=name_icontains,
            page=page,
            page_size=page_size,
            search=search,
        )
    ).parsed
