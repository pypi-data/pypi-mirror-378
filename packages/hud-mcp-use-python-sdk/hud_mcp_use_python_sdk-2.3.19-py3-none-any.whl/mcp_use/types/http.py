"""Type definitions for HTTP-related configurations."""

from __future__ import annotations

from typing import Any, Callable, NotRequired, TypedDict

import httpx


McpHttpClientFactory = Callable[..., httpx.AsyncClient]


class HttpOptions(TypedDict, total=False):
    """Configuration options for HTTP transport.

    - disable_sse_fallback: If True, do not attempt SSE fallback when Streamable HTTP fails.
    - httpx_client_factory: Optional factory to create custom httpx.AsyncClient.
    """

    disable_sse_fallback: NotRequired[bool]
    httpx_client_factory: NotRequired[McpHttpClientFactory]


