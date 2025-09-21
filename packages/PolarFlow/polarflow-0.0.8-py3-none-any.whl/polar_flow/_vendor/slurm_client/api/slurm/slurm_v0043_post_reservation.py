from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ...client import AuthenticatedClient, Client
from ...models.v0043_openapi_reservation_mod_resp import V0043OpenapiReservationModResp
from ...models.v0043_reservation_desc_msg import V0043ReservationDescMsg
from ...types import Response


def _get_kwargs(
    *,
    body: V0043ReservationDescMsg,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/slurm/v0.0.43/reservation",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> V0043OpenapiReservationModResp:
    if response.status_code == 200:
        response_200 = V0043OpenapiReservationModResp.from_dict(response.json())

        return response_200

    response_default = V0043OpenapiReservationModResp.from_dict(response.json())

    return response_default


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[V0043OpenapiReservationModResp]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    body: V0043ReservationDescMsg,
) -> Response[V0043OpenapiReservationModResp]:
    """create or update a reservation

    Args:
        body (V0043ReservationDescMsg):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[V0043OpenapiReservationModResp]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: Union[AuthenticatedClient, Client],
    body: V0043ReservationDescMsg,
) -> Optional[V0043OpenapiReservationModResp]:
    """create or update a reservation

    Args:
        body (V0043ReservationDescMsg):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        V0043OpenapiReservationModResp
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    body: V0043ReservationDescMsg,
) -> Response[V0043OpenapiReservationModResp]:
    """create or update a reservation

    Args:
        body (V0043ReservationDescMsg):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[V0043OpenapiReservationModResp]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
    body: V0043ReservationDescMsg,
) -> Optional[V0043OpenapiReservationModResp]:
    """create or update a reservation

    Args:
        body (V0043ReservationDescMsg):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        V0043OpenapiReservationModResp
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
