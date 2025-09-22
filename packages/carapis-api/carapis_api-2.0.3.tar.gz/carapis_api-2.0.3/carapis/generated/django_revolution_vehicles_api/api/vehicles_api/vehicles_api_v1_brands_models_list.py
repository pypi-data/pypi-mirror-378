from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.paginated_v1_vehicle_model_list import PaginatedV1VehicleModelList
from ...types import UNSET, Unset
from typing import cast
from typing import Union


def _get_kwargs(
    brand_id: str,
    *,
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    search: Union[Unset, str] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["page"] = page

    params["page_size"] = page_size

    params["search"] = search

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/vehicles_api/v1/brands/{brand_id}/models/".format(
            brand_id=brand_id,
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[PaginatedV1VehicleModelList]:
    if response.status_code == 200:
        response_200 = PaginatedV1VehicleModelList.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[PaginatedV1VehicleModelList]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    brand_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    search: Union[Unset, str] = UNSET,
) -> Response[PaginatedV1VehicleModelList]:
    """List brand models

     Get vehicle models for specific brand

    Args:
        brand_id (str):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        search (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PaginatedV1VehicleModelList]
    """

    kwargs = _get_kwargs(
        brand_id=brand_id,
        page=page,
        page_size=page_size,
        search=search,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    brand_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    search: Union[Unset, str] = UNSET,
) -> Optional[PaginatedV1VehicleModelList]:
    """List brand models

     Get vehicle models for specific brand

    Args:
        brand_id (str):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        search (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PaginatedV1VehicleModelList
    """

    return sync_detailed(
        brand_id=brand_id,
        client=client,
        page=page,
        page_size=page_size,
        search=search,
    ).parsed


async def asyncio_detailed(
    brand_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    search: Union[Unset, str] = UNSET,
) -> Response[PaginatedV1VehicleModelList]:
    """List brand models

     Get vehicle models for specific brand

    Args:
        brand_id (str):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        search (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PaginatedV1VehicleModelList]
    """

    kwargs = _get_kwargs(
        brand_id=brand_id,
        page=page,
        page_size=page_size,
        search=search,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    brand_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    page: Union[Unset, int] = UNSET,
    page_size: Union[Unset, int] = UNSET,
    search: Union[Unset, str] = UNSET,
) -> Optional[PaginatedV1VehicleModelList]:
    """List brand models

     Get vehicle models for specific brand

    Args:
        brand_id (str):
        page (Union[Unset, int]):
        page_size (Union[Unset, int]):
        search (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PaginatedV1VehicleModelList
    """

    return (
        await asyncio_detailed(
            brand_id=brand_id,
            client=client,
            page=page,
            page_size=page_size,
            search=search,
        )
    ).parsed
