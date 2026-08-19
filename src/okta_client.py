"""Okta REST API client.

Reads OKTA_DOMAIN and OKTA_API_TOKEN from the environment.

The client:
- sends authenticated requests
- honors Okta Retry-After headers for HTTP 429
- retries rate-limited requests with exponential fallback
- exposes HTTP status/body information through OktaClientError
- provides a small, predictable HTTP abstraction for the lifecycle layer
"""

from __future__ import annotations

import os
import time
from typing import Any

import requests
from dotenv import load_dotenv

load_dotenv()

DEFAULT_TIMEOUT = 30
MAX_RETRIES = 5
BACKOFF_BASE_SECONDS = 1.0


class OktaClientError(Exception):
    """Raised when an Okta API request fails."""

    def __init__(
        self,
        message: str,
        *,
        status_code: int | None = None,
        response_body: Any = None,
        headers: Any = None,
    ):
        super().__init__(message)
        self.status_code = status_code
        self.response_body = response_body
        self.headers = headers or {}


class OktaClient:
    """Thin wrapper around the Okta REST API."""

    def __init__(
        self,
        domain: str | None = None,
        api_token: str | None = None,
        session: requests.Session | None = None,
    ):
        self.domain = (
            domain or os.getenv("OKTA_DOMAIN") or ""
        ).strip().rstrip("/")

        self.api_token = (
            api_token or os.getenv("OKTA_API_TOKEN") or ""
        ).strip()

        if not self.domain or not self.api_token:
            raise OktaClientError(
                "OKTA_DOMAIN and OKTA_API_TOKEN must be set "
                "(see .env.example)."
            )

        self.session = session or requests.Session()

        self.session.headers.update(
            {
                "Authorization": f"SSWS {self.api_token}",
                "Accept": "application/json",
                "Content-Type": "application/json",
            }
        )

    @property
    def base_url(self) -> str:
        return f"https://{self.domain}/api/v1"

    def request(self, method: str, path: str, **kwargs) -> requests.Response:
        """Send an HTTP request to Okta.

        HTTP 429 responses are retried using Retry-After when supplied,
        otherwise exponential backoff is used.

        Other HTTP errors are raised immediately.
        """
        url = f"{self.base_url}/{path.lstrip('/')}"

        kwargs.setdefault("timeout", DEFAULT_TIMEOUT)

        for attempt in range(MAX_RETRIES + 1):
            try:
                response = self.session.request(
                    method,
                    url,
                    **kwargs,
                )
            except requests.RequestException as exc:
                raise OktaClientError(
                    f"Okta request failed: {method} {url}: {exc}"
                ) from exc

            if response.status_code == 429:
                if attempt == MAX_RETRIES:
                    raise OktaClientError(
                        f"Okta request rate-limited after "
                        f"{MAX_RETRIES} retries: {method} {url}",
                        status_code=429,
                        response_body=self._response_body(response),
                        headers=response.headers,
                    )

                time.sleep(self._retry_delay(response, attempt))
                continue

            if response.status_code >= 400:
                body = self._response_body(response)

                raise OktaClientError(
                    f"Okta request failed: {method} {url} -> "
                    f"{response.status_code}: "
                    f"{response.text[:500]}",
                    status_code=response.status_code,
                    response_body=body,
                    headers=response.headers,
                )

            return response

        # Defensive; normally unreachable.
        raise OktaClientError(
            f"Okta request failed unexpectedly: {method} {url}"
        )

    @staticmethod
    def _response_body(response: requests.Response) -> Any:
        """Return JSON error body when possible, otherwise text."""
        try:
            return response.json()
        except ValueError:
            return response.text[:500]

    @staticmethod
    def _retry_delay(
        response: requests.Response,
        attempt: int,
    ) -> float:
        """Calculate delay before another 429 attempt."""
        retry_after = response.headers.get("Retry-After")

        if retry_after is not None:
            try:
                return max(0.0, float(retry_after))
            except (TypeError, ValueError):
                pass

        return BACKOFF_BASE_SECONDS * (2**attempt)

    def get(self, path: str, **kwargs) -> requests.Response:
        return self.request("GET", path, **kwargs)

    def post(
        self,
        path: str,
        json: dict[str, Any] | None = None,
        **kwargs,
    ) -> requests.Response:
        return self.request(
            "POST",
            path,
            json=json,
            **kwargs,
        )

    def delete(self, path: str, **kwargs) -> requests.Response:
        return self.request("DELETE", path, **kwargs)