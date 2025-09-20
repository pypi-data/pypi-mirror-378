"""
Module for sends HTTP requests in parallel
"""

import time
from typing import Any
from dataclasses import dataclass


import asyncio
import httpx


@dataclass
class Request:
    url: str
    method: str = "GET"
    content: Any = None
    data: Any = None
    files: Any = None
    json: Any = None
    params: Any = None
    headers: Any = None
    cookies: Any = None
    timeout: Any = None
    auth: Any = None
    follow_redirects: Any = None
    extensions: Any = None
    ok: bool | None = None
    response: httpx.Response | None | httpx.RequestError = None
    attempts: int = 0
    time_elapsed: float = 0
    extra: Any = None  # Used to store user-defined data, such as the context that accompanies the request to use later

    @classmethod
    def from_dict(cls, d: dict[Any, Any]):
        return cls(**d)

    def __getitem__(self, item):
        return getattr(self, item)

    def __setitem__(self, key, value):
        return setattr(self, key, value)


async def async_request(client: httpx.AsyncClient, req: Request) -> None:
    """
    Sends an asynchronous request. The type of request is determined by the value of `request_type` in `request_info` or
    the value "method". If both are present and different from each other, request_info["dispatch_successful"] will be False.

    Parameters
    ----------
    client : httpx.AsyncClient
        The HTTP client used to send the request.
    request_info : dict
        A dictionary containing the request information, including the request type.

    Returns
    -------
    None
    """

    req.ok = False
    req.attempts += 1

    t1 = time.monotonic()
    try:
        response = await client.request(
            method=req.method,
            url=req.url,
            content=req.content,
            data=req.data,
            files=req.files,
            json=req.json,
            params=req.params,
            headers=req.headers,
            cookies=req.cookies,
            auth=req.auth,
            follow_redirects=req.follow_redirects,
            timeout=req.timeout,
            extensions=req.extensions,
        )
        req.ok = not response.is_error
        req.response = response
    except httpx.RequestError as exc:
        req.response = exc
    t2 = time.monotonic()
    req.time_elapsed += t2 - t1


def dispatch_requests(list_requests: list[Request], retries: int = 0, **kwargs) -> list[Request]:
    """
    Receives a list of dictionaries containing the request information. These dictionaries
    will store the request responses. The number of elements N in the list is used to open
    N connections to the endpoints.

    Parameters
    ----------
    list_requests : list of Request
    retries: int
        Number of attempts in case a request fails, each request can be executed up to (1+retries) times
    **kwargs: Any
        List of parameters sent to httpx.AsyncClient

    Returns
    -------
    list_requests: list of modified Requests
        The list `list_requests` is also modified in place, so accessing the return value is not necessary

    Examples
    --------

    >>> req1 = {"method": "GET", "url": "https://httpbin.org/anything"}
    >>> req2 = {"method": "POST", "url": "https://httpbin.org/post", "json": {"var1": 1}}
    >>> list_reqs = [req1, req2]
    >>> dispatch_requests(list_reqs)
    >>> for req in list_reqs:
    >>>     print(f"{req}")
    """

    async def create_tasks():
        client = httpx.AsyncClient(**kwargs)
        attempts = max(1, 1 + retries)
        for _ in range(attempts):
            tasks = []
            for request in list_requests:
                if not request.ok:
                    tasks.append(asyncio.create_task(async_request(client=client, req=request)))

            await asyncio.gather(*tasks)

        await client.aclose()

    asyncio.run(create_tasks())

    return list_requests
