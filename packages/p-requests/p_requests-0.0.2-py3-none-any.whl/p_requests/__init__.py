__version__ = "0.0.2"

# Import core components
from .core import Request, Response, fetch_parallel, fetch_parallel_async

__all__ = [
    "Request",
    "Response",
    "fetch_parallel",
    "fetch_parallel_async",
]
