import asyncio
import logging
from typing import Any, Self
from urllib.parse import urljoin

import aiohttp
from aiohttp import ClientError, ClientResponseError, ClientTimeout

from .exceptions import APIError, APINetworkError, APITimeoutError

logger = logging.getLogger(__name__)


class BaseAPIClient:
    """Base HTTP client with retry logic and error handling."""

    def __init__(
        self,
        base_url: str,
        timeout: float = 30.0,
        max_retries: int = 3,
        retry_delay: float = 1.0,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = ClientTimeout(total=timeout)
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self._session: aiohttp.ClientSession | None = None

    async def __aenter__(self) -> Self:
        await self._ensure_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:  # type: ignore[no-untyped-def]
        await self.close()

    async def _ensure_session(self) -> aiohttp.ClientSession:
        """Ensure session is created."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                timeout=self.timeout,
                headers={
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                },
            )
        return self._session

    async def close(self) -> None:
        """Close the session."""
        if self._session and not self._session.closed:
            await self._session.close()

    def _build_url(self, endpoint: str) -> str:
        """Build full URL for endpoint."""
        return urljoin(f"{self.base_url}/", endpoint.lstrip("/"))

    async def _request_with_retry(
        self,
        method: str,
        endpoint: str,
        **kwargs: Any,
    ) -> Any:
        """Make HTTP request with retry logic."""
        last_exception: Exception | None = None
        max_attempts = self.max_retries + 1

        for attempt in range(max_attempts):
            try:
                return await self._make_request(method, endpoint, **kwargs)

            except (TimeoutError, ClientError) as e:
                last_exception = e

                if attempt < max_attempts - 1:
                    wait_time = self.retry_delay * (2**attempt)  # Exponential backoff
                    logger.warning(
                        "Request failed (attempt %d/%d), retrying in %.1fs: %s",
                        attempt + 1,
                        max_attempts,
                        wait_time,
                        str(e),
                    )
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(
                        "Request failed after %d attempts: %s",
                        max_attempts,
                        str(e),
                    )

        # If we get here, all retries failed
        if isinstance(last_exception, TimeoutError):
            raise APITimeoutError(
                f"Request timeout after {max_attempts} attempts"
            ) from last_exception
        raise APINetworkError(
            f"Request failed after {max_attempts} attempts: {last_exception!s}"
        ) from last_exception

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        **kwargs: Any,
    ) -> Any:
        """Make single HTTP request."""
        session = await self._ensure_session()
        url = self._build_url(endpoint)
        try:
            async with session.request(method, url, **kwargs) as response:
                response.raise_for_status()

                no_content = 204
                if response.status == no_content:
                    return {}

                content_type = response.headers.get("Content-Type", "")
                if "application/json" in content_type:
                    return await response.json()
                else:
                    text = await response.text()
                    return {"text": text}

        except ClientResponseError as e:
            logger.error(
                "API request failed with status %d: %s",
                e.status,
                e.message,
            )
            raise APIError(
                f"API request failed: {e.message}",
                status_code=e.status,
            ) from e

        except TimeoutError as e:
            logger.error("API request timeout for %s", url)
            raise APITimeoutError(f"Request timeout after {self.timeout.total} seconds") from e

        except ClientError as e:
            logger.error("Network error for %s: %s", url, e)
            raise APINetworkError(f"Network error: {e!s}") from e

    async def _request(
        self,
        method: str,
        endpoint: str,
        **kwargs: Any,
    ) -> Any:
        """Make HTTP request with retry logic."""
        return await self._request_with_retry(method, endpoint, **kwargs)

    async def get(
        self,
        endpoint: str,
        params: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> Any:
        """Make GET request."""
        return await self._request("GET", endpoint, params=params, **kwargs)

    async def post(
        self,
        endpoint: str,
        data: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> Any:
        """Make POST request."""
        return await self._request("POST", endpoint, data=data, json=json, **kwargs)
