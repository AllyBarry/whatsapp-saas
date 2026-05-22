"""Thin async HTTP client for the Meta Graph API."""
from typing import Any

import httpx

from app.core.config import settings
from app.core.errors import MetaAPIError
from app.core.logging import get_logger, log_event

logger = get_logger("app.meta.client")


class MetaGraphClient:
    """Wraps httpx with auth, error normalization and logging.

    One instance per request/operation — holds the tenant's access token.
    """

    def __init__(self, access_token: str, timeout: float = 20.0):
        self._access_token = access_token
        self._base = settings.meta_api_base
        self._timeout = timeout

    @property
    def _headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self._access_token}"}

    async def get(self, path: str, params: dict[str, Any] | None = None) -> dict:
        return await self._request("GET", path, params=params)

    async def post(self, path: str, json: dict[str, Any]) -> dict:
        return await self._request("POST", path, json=json)

    async def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict | None = None,
        json: dict | None = None,
    ) -> dict:
        url = f"{self._base}/{path.lstrip('/')}"
        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.request(
                    method, url, headers=self._headers, params=params, json=json
                )
        except httpx.HTTPError as exc:
            log_event(logger, "error", "Meta API transport failure", path=path, error=str(exc))
            raise MetaAPIError(f"Could not reach Meta Graph API: {exc}") from exc

        if response.status_code >= 400:
            detail = _extract_error(response)
            log_event(
                logger, "error", "Meta API error response",
                path=path, status=response.status_code, detail=detail,
            )
            raise MetaAPIError(f"Meta API error ({response.status_code}): {detail}")

        return response.json() if response.content else {}


def _extract_error(response: httpx.Response) -> str:
    try:
        body = response.json()
        return body.get("error", {}).get("message", response.text)
    except ValueError:
        return response.text
