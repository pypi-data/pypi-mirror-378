from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_shared_repository_limits_response_getsharedrepositorylimits import (
  GetSharedRepositoryLimitsResponseGetsharedrepositorylimits,
)
from ...models.http_validation_error import HTTPValidationError
from ...types import UNSET, Response, Unset


def _get_kwargs(
  repository: str,
  *,
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
    "method": "get",
    "url": f"/v1/user/limits/shared-repositories/{repository}",
    "cookies": cookies,
  }

  _kwargs["headers"] = headers
  return _kwargs


def _parse_response(
  *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[
  Union[GetSharedRepositoryLimitsResponseGetsharedrepositorylimits, HTTPValidationError]
]:
  if response.status_code == 200:
    response_200 = GetSharedRepositoryLimitsResponseGetsharedrepositorylimits.from_dict(
      response.json()
    )

    return response_200
  if response.status_code == 422:
    response_422 = HTTPValidationError.from_dict(response.json())

    return response_422
  if client.raise_on_unexpected_status:
    raise errors.UnexpectedStatus(response.status_code, response.content)
  else:
    return None


def _build_response(
  *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[
  Union[GetSharedRepositoryLimitsResponseGetsharedrepositorylimits, HTTPValidationError]
]:
  return Response(
    status_code=HTTPStatus(response.status_code),
    content=response.content,
    headers=response.headers,
    parsed=_parse_response(client=client, response=response),
  )


def sync_detailed(
  repository: str,
  *,
  client: AuthenticatedClient,
  authorization: Union[None, Unset, str] = UNSET,
  auth_token: Union[None, Unset, str] = UNSET,
) -> Response[
  Union[GetSharedRepositoryLimitsResponseGetsharedrepositorylimits, HTTPValidationError]
]:
  """Get shared repository rate limit status

   Get current rate limit status and usage for a shared repository.

      Returns:
      - Current usage across different time windows
      - Rate limits based on subscription tier
      - Remaining quota
      - Reset times

      Note: All queries are FREE - this only shows rate limit status.

  Args:
      repository (str): Repository name (e.g., 'sec')
      authorization (Union[None, Unset, str]):
      auth_token (Union[None, Unset, str]):

  Raises:
      errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
      httpx.TimeoutException: If the request takes longer than Client.timeout.

  Returns:
      Response[Union[GetSharedRepositoryLimitsResponseGetsharedrepositorylimits, HTTPValidationError]]
  """

  kwargs = _get_kwargs(
    repository=repository,
    authorization=authorization,
    auth_token=auth_token,
  )

  response = client.get_httpx_client().request(
    **kwargs,
  )

  return _build_response(client=client, response=response)


def sync(
  repository: str,
  *,
  client: AuthenticatedClient,
  authorization: Union[None, Unset, str] = UNSET,
  auth_token: Union[None, Unset, str] = UNSET,
) -> Optional[
  Union[GetSharedRepositoryLimitsResponseGetsharedrepositorylimits, HTTPValidationError]
]:
  """Get shared repository rate limit status

   Get current rate limit status and usage for a shared repository.

      Returns:
      - Current usage across different time windows
      - Rate limits based on subscription tier
      - Remaining quota
      - Reset times

      Note: All queries are FREE - this only shows rate limit status.

  Args:
      repository (str): Repository name (e.g., 'sec')
      authorization (Union[None, Unset, str]):
      auth_token (Union[None, Unset, str]):

  Raises:
      errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
      httpx.TimeoutException: If the request takes longer than Client.timeout.

  Returns:
      Union[GetSharedRepositoryLimitsResponseGetsharedrepositorylimits, HTTPValidationError]
  """

  return sync_detailed(
    repository=repository,
    client=client,
    authorization=authorization,
    auth_token=auth_token,
  ).parsed


async def asyncio_detailed(
  repository: str,
  *,
  client: AuthenticatedClient,
  authorization: Union[None, Unset, str] = UNSET,
  auth_token: Union[None, Unset, str] = UNSET,
) -> Response[
  Union[GetSharedRepositoryLimitsResponseGetsharedrepositorylimits, HTTPValidationError]
]:
  """Get shared repository rate limit status

   Get current rate limit status and usage for a shared repository.

      Returns:
      - Current usage across different time windows
      - Rate limits based on subscription tier
      - Remaining quota
      - Reset times

      Note: All queries are FREE - this only shows rate limit status.

  Args:
      repository (str): Repository name (e.g., 'sec')
      authorization (Union[None, Unset, str]):
      auth_token (Union[None, Unset, str]):

  Raises:
      errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
      httpx.TimeoutException: If the request takes longer than Client.timeout.

  Returns:
      Response[Union[GetSharedRepositoryLimitsResponseGetsharedrepositorylimits, HTTPValidationError]]
  """

  kwargs = _get_kwargs(
    repository=repository,
    authorization=authorization,
    auth_token=auth_token,
  )

  response = await client.get_async_httpx_client().request(**kwargs)

  return _build_response(client=client, response=response)


async def asyncio(
  repository: str,
  *,
  client: AuthenticatedClient,
  authorization: Union[None, Unset, str] = UNSET,
  auth_token: Union[None, Unset, str] = UNSET,
) -> Optional[
  Union[GetSharedRepositoryLimitsResponseGetsharedrepositorylimits, HTTPValidationError]
]:
  """Get shared repository rate limit status

   Get current rate limit status and usage for a shared repository.

      Returns:
      - Current usage across different time windows
      - Rate limits based on subscription tier
      - Remaining quota
      - Reset times

      Note: All queries are FREE - this only shows rate limit status.

  Args:
      repository (str): Repository name (e.g., 'sec')
      authorization (Union[None, Unset, str]):
      auth_token (Union[None, Unset, str]):

  Raises:
      errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
      httpx.TimeoutException: If the request takes longer than Client.timeout.

  Returns:
      Union[GetSharedRepositoryLimitsResponseGetsharedrepositorylimits, HTTPValidationError]
  """

  return (
    await asyncio_detailed(
      repository=repository,
      client=client,
      authorization=authorization,
      auth_token=auth_token,
    )
  ).parsed
