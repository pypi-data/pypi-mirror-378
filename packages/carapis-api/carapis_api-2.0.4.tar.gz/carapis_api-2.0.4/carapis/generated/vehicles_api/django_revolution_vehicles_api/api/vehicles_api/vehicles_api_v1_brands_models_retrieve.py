from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.v1_vehicle_model import V1VehicleModel
from typing import cast


def _get_kwargs(
    brand_id: str,
    id: str,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/vehicles_api/v1/brands/{brand_id}/models/{id}/".format(
            brand_id=brand_id,
            id=id,
        ),
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[V1VehicleModel]:
    if response.status_code == 200:
        response_200 = V1VehicleModel.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[V1VehicleModel]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    brand_id: str,
    id: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[V1VehicleModel]:
    """Get model details

     Get specific vehicle model information

    Args:
        brand_id (str):
        id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[V1VehicleModel]
    """

    kwargs = _get_kwargs(
        brand_id=brand_id,
        id=id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    brand_id: str,
    id: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[V1VehicleModel]:
    """Get model details

     Get specific vehicle model information

    Args:
        brand_id (str):
        id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        V1VehicleModel
    """

    return sync_detailed(
        brand_id=brand_id,
        id=id,
        client=client,
    ).parsed


async def asyncio_detailed(
    brand_id: str,
    id: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[V1VehicleModel]:
    """Get model details

     Get specific vehicle model information

    Args:
        brand_id (str):
        id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[V1VehicleModel]
    """

    kwargs = _get_kwargs(
        brand_id=brand_id,
        id=id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    brand_id: str,
    id: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[V1VehicleModel]:
    """Get model details

     Get specific vehicle model information

    Args:
        brand_id (str):
        id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        V1VehicleModel
    """

    return (
        await asyncio_detailed(
            brand_id=brand_id,
            id=id,
            client=client,
        )
    ).parsed
