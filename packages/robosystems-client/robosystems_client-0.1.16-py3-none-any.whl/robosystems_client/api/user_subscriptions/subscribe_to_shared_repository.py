from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.subscription_request import SubscriptionRequest
from ...models.subscription_response import SubscriptionResponse
from ...types import UNSET, Response, Unset


def _get_kwargs(
  *,
  body: SubscriptionRequest,
  authorization: Union[None, Unset, str] = UNSET,
  auth_token: Union[None, Unset, str] = UNSET,
) -> dict[str, Any]:
  headers: dict[str, Any] = {}
  if not isinstance(authorization, Unset):
    headers["authorization"] = authorization

  cookies = {}
  if auth_token is not UNSET:
    cookies["auth-token"] = auth_token

  _kwargs: dict[str, Any] = {
    "method": "post",
    "url": "/v1/user/subscriptions/shared-repositories/subscribe",
    "cookies": cookies,
  }

  _kwargs["json"] = body.to_dict()

  headers["Content-Type"] = "application/json"

  _kwargs["headers"] = headers
  return _kwargs


def _parse_response(
  *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Any, HTTPValidationError, SubscriptionResponse]]:
  if response.status_code == 201:
    response_201 = SubscriptionResponse.from_dict(response.json())

    return response_201
  if response.status_code == 400:
    response_400 = cast(Any, None)
    return response_400
  if response.status_code == 401:
    response_401 = cast(Any, None)
    return response_401
  if response.status_code == 500:
    response_500 = cast(Any, None)
    return response_500
  if response.status_code == 422:
    response_422 = HTTPValidationError.from_dict(response.json())

    return response_422
  if client.raise_on_unexpected_status:
    raise errors.UnexpectedStatus(response.status_code, response.content)
  else:
    return None


def _build_response(
  *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[Any, HTTPValidationError, SubscriptionResponse]]:
  return Response(
    status_code=HTTPStatus(response.status_code),
    content=response.content,
    headers=response.headers,
    parsed=_parse_response(client=client, response=response),
  )


def sync_detailed(
  *,
  client: AuthenticatedClient,
  body: SubscriptionRequest,
  authorization: Union[None, Unset, str] = UNSET,
  auth_token: Union[None, Unset, str] = UNSET,
) -> Response[Union[Any, HTTPValidationError, SubscriptionResponse]]:
  """Subscribe to Shared Repository

   Create a new subscription to a shared repository add-on with specified tier

  Args:
      authorization (Union[None, Unset, str]):
      auth_token (Union[None, Unset, str]):
      body (SubscriptionRequest): Request to create a new subscription.

  Raises:
      errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
      httpx.TimeoutException: If the request takes longer than Client.timeout.

  Returns:
      Response[Union[Any, HTTPValidationError, SubscriptionResponse]]
  """

  kwargs = _get_kwargs(
    body=body,
    authorization=authorization,
    auth_token=auth_token,
  )

  response = client.get_httpx_client().request(
    **kwargs,
  )

  return _build_response(client=client, response=response)


def sync(
  *,
  client: AuthenticatedClient,
  body: SubscriptionRequest,
  authorization: Union[None, Unset, str] = UNSET,
  auth_token: Union[None, Unset, str] = UNSET,
) -> Optional[Union[Any, HTTPValidationError, SubscriptionResponse]]:
  """Subscribe to Shared Repository

   Create a new subscription to a shared repository add-on with specified tier

  Args:
      authorization (Union[None, Unset, str]):
      auth_token (Union[None, Unset, str]):
      body (SubscriptionRequest): Request to create a new subscription.

  Raises:
      errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
      httpx.TimeoutException: If the request takes longer than Client.timeout.

  Returns:
      Union[Any, HTTPValidationError, SubscriptionResponse]
  """

  return sync_detailed(
    client=client,
    body=body,
    authorization=authorization,
    auth_token=auth_token,
  ).parsed


async def asyncio_detailed(
  *,
  client: AuthenticatedClient,
  body: SubscriptionRequest,
  authorization: Union[None, Unset, str] = UNSET,
  auth_token: Union[None, Unset, str] = UNSET,
) -> Response[Union[Any, HTTPValidationError, SubscriptionResponse]]:
  """Subscribe to Shared Repository

   Create a new subscription to a shared repository add-on with specified tier

  Args:
      authorization (Union[None, Unset, str]):
      auth_token (Union[None, Unset, str]):
      body (SubscriptionRequest): Request to create a new subscription.

  Raises:
      errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
      httpx.TimeoutException: If the request takes longer than Client.timeout.

  Returns:
      Response[Union[Any, HTTPValidationError, SubscriptionResponse]]
  """

  kwargs = _get_kwargs(
    body=body,
    authorization=authorization,
    auth_token=auth_token,
  )

  response = await client.get_async_httpx_client().request(**kwargs)

  return _build_response(client=client, response=response)


async def asyncio(
  *,
  client: AuthenticatedClient,
  body: SubscriptionRequest,
  authorization: Union[None, Unset, str] = UNSET,
  auth_token: Union[None, Unset, str] = UNSET,
) -> Optional[Union[Any, HTTPValidationError, SubscriptionResponse]]:
  """Subscribe to Shared Repository

   Create a new subscription to a shared repository add-on with specified tier

  Args:
      authorization (Union[None, Unset, str]):
      auth_token (Union[None, Unset, str]):
      body (SubscriptionRequest): Request to create a new subscription.

  Raises:
      errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
      httpx.TimeoutException: If the request takes longer than Client.timeout.

  Returns:
      Union[Any, HTTPValidationError, SubscriptionResponse]
  """

  return (
    await asyncio_detailed(
      client=client,
      body=body,
      authorization=authorization,
      auth_token=auth_token,
    )
  ).parsed
