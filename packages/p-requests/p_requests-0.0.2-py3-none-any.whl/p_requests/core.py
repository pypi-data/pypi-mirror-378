"""
Module for sends HTTP requests in parallel
"""

# ----------------------------------------------------
# Imports
# ----------------------------------------------------

import asyncio
import time
from typing import Any
from types import MappingProxyType
from collections.abc import Mapping
from dataclasses import dataclass, field
import httpx

from httpx._types import (
    AsyncByteStream,
    CookieTypes,
    HeaderTypes,
    QueryParamTypes,
    RequestContent,
    RequestData,
    RequestFiles,
    AuthTypes,
    SyncByteStream,
    TimeoutTypes,
    RequestExtensions,
)

# ----------------------------------------------------
# Classes
# ----------------------------------------------------


@dataclass(frozen=True)
class Request:
    url: httpx.URL | str
    method: str = "GET"
    params: QueryParamTypes | None = None
    headers: HeaderTypes | None = None
    cookies: CookieTypes | None = None
    content: RequestContent | None = None
    data: RequestData | None = None
    json: Any = None
    stream: AsyncByteStream | SyncByteStream | None = None
    files: RequestFiles | None = None
    auth: AuthTypes | None = None
    timeout: TimeoutTypes | None = None
    extensions: RequestExtensions | None = None
    follow_redirects: bool = True
    metadata: Mapping[str, Any] = field(default_factory=lambda: MappingProxyType({}))

    def __post_init__(self):
        # Wrap in MappingProxyType unless already immutable
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))

    @classmethod
    def from_dict(cls, d: dict[Any, Any]):
        return cls(**d)

    def get_httpx_request_parameters(self) -> dict[str, Any]:
        """Returns a dict of httpx.request parameters"""
        parameters = [
            "url",
            "method",
            "params",
            "headers",
            "cookies",
            "content",
            "data",
            "json",
            "stream",
            "files",
            "auth",
            "timeout",
            "extensions",
            "follow_redirects",
        ]

        return {p: getattr(self, p) for p in parameters if getattr(self, p) is not None}


@dataclass
class Response:
    request: Request
    response: httpx.Response | None = None
    error: Exception | None = None
    time_elapsed: float = 0

    @property
    def ok(self) -> bool:
        if self.response is None:
            return False
        if self.error is not None:
            return False

        return not self.response.is_error


# ----------------------------------------------------
# Internal Functions
# ----------------------------------------------------


async def _async_request(
    client: httpx.AsyncClient, req: Request, raise_exception: bool
) -> Response:
    """
    Sends an asynchronous request

    Parameters
    ----------
    client : httpx.AsyncClient
        The HTTP client used to send the request.
    request_info : Request
        Request data
    raise_exception : bool
        If True raises exceptions, otherwise only stores them in Response.error

    Returns
    -------
    None
    """

    response = Response(request=req)

    t1 = time.monotonic()
    try:
        r = await client.request(**req.get_httpx_request_parameters())
        response.response = r
    except Exception as e:
        response.error = e
    t2 = time.monotonic()
    response.time_elapsed = t2 - t1

    if not response.ok and raise_exception:
        if response.response is not None:
            status_code = response.response.status_code
            error = response.response.content
        else:
            status_code = None
            error = response.error

        raise RuntimeError(
            f"Request did not return success: Request ({req}) - Status Code ({status_code}) - Error ({error})"
        )
    return response


async def _dispatch_requests_async(
    list_requests: list[Request], raise_exception: bool, max_concurrency: int, **kwargs
) -> list[Response]:
    """
    Internal coroutine to execute requests in parallel
    """

    semaphore = asyncio.Semaphore(max_concurrency)

    async def _semaphored_request(client: httpx.AsyncClient, req: Request, raise_exception: bool):
        async with semaphore:
            return await _async_request(client, req, raise_exception)

    list_responses = []
    async with httpx.AsyncClient(**kwargs) as client:
        tasks = [_semaphored_request(client, request, raise_exception) for request in list_requests]
        list_responses.extend(await asyncio.gather(*tasks))

    return list_responses


# ----------------------------------------------------
# External Functions
# ----------------------------------------------------


def fetch_parallel(
    list_requests: list[Request], raise_exception: bool = True, max_concurrency: int = 50, **kwargs
) -> list[Response]:
    """
    Receives a list Requests and opens `N` connections equal to the number of Requests on the list

    Parameters
    ----------
    list_requests : list of Request
    raise_exception: bool
        If True, raises an exception if any of the requests returns an error. If False, the error
        will only be stored in Response.error and Response.ok will be False.
    **kwargs: Any
        List of parameters sent to httpx.AsyncClient

    Returns
    -------
    list_response: list of Responses
        Each response contains a field with the original request

    Examples
    --------

    >>> req1 = Request(method="GET", "url"="https://httpbin.org/anything")
    >>> req2 = Request.from_dict({"method": "POST", "url": "https://httpbin.org/post", "json": {"var1": 1}})
    >>> list_reqs = [req1, req2]
    >>> list_resps = fetch_parallel(list_reqs)
    >>> for resp in list_resps:
    >>>     print(f"{resp}")
    """

    return asyncio.run(
        _dispatch_requests_async(
            list_requests,
            raise_exception=raise_exception,
            max_concurrency=max_concurrency,
            **kwargs,
        )
    )


async def fetch_parallel_async(
    list_requests: list[Request], raise_exception: bool = True, max_concurrency: int = 50, **kwargs
) -> list[Response]:
    """
    Receives a list Requests and opens `N` connections equal to the number of Requests on the list

    Parameters
    ----------
    list_requests : list of Request
    raise_exception: bool
        If True, raises an exception if any of the requests returns an error. If False, the error
        will only be stored in Response.error and Response.ok will be False.
    **kwargs: Any
        List of parameters sent to httpx.AsyncClient

    Returns
    -------
    list_response: list of Responses
        Each response contains a field with the original request

    Examples
    --------

    >>> req1 = Request(method="GET", "url"="https://httpbin.org/anything")
    >>> req2 = Request.from_dict({"method": "POST", "url": "https://httpbin.org/post", "json": {"var1": 1}})
    >>> list_reqs = [req1, req2]
    >>> list_resps = await fetch_parallel_async(list_reqs)
    >>> for resp in list_resps:
    >>>     print(f"{resp}")
    """

    return await _dispatch_requests_async(
        list_requests, raise_exception=raise_exception, max_concurrency=max_concurrency, **kwargs
    )
