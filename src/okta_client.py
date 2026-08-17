"""Okta REST API client.

Reads ``OKTA_DOMAIN`` and ``OKTA_API_TOKEN`` from the environment, sends
authenticated requests, retries on HTTP 429 rate limits (honoring
Okta's ``Retry-After`` header when present, otherwise falling back to
exponential backoff), and raises :class:`OktaClientError` on failures.
"""

import os
import time

import requests
from dotenv import load_dotenv

load_dotenv()

DEFAULT_TIMEOUT = 30
MAX_RETRIES = 5
BACKOFF_BASE_SECONDS = 1.0


class OktaClientError(Exception):
    """Raised when an Okta API request fails."""


class OktaClient:
    """Thin wrapper around the Okta REST API."""

    def __init__(self, domain=None, api_token=None, session=None):
        self.domain = (domain or os.getenv("OKTA_DOMAIN") or "").strip().rstrip("/")
        self.api_token = api_token or os.getenv("OKTA_API_TOKEN") or ""
        if not self.domain or not self.api_token:
            raise OktaClientError(
                "OKTA_DOMAIN and OKTA_API_TOKEN must be set (see .env.example)."
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
    def base_url(self):
        return f"https://{self.domain}/api/v1"

    def request(self, method, path, **kwargs):
        url = f"{self.base_url}/{path.lstrip('/')}"
        kwargs.setdefault("timeout", DEFAULT_TIMEOUT)
        for attempt in range(MAX_RETRIES):
            response = self.session.request(method, url, **kwargs)
            if response.status_code == 429:
                time.sleep(self._retry_delay(response, attempt))
                continue
            if response.status_code >= 400:
                raise OktaClientError(
                    f"Okta request failed: {method} {url} -> "
                    f"{response.status_code}: {response.text[:500]}"
                )
            return response
        raise OktaClientError(f"Okta request rate-limited: {method} {url}")

    @staticmethod
    def _retry_delay(response, attempt):
        """Seconds to wait before retrying a 429.

        Prefers Okta's ``Retry-After`` header (seconds until the rate
        limit window resets) when present, since it reflects the
        server's actual state; falls back to a fixed exponential
        backoff otherwise.
        """
        retry_after = response.headers.get("Retry-After")
        if retry_after is not None:
            try:
                return max(0.0, float(retry_after))
            except ValueError:
                pass
        return BACKOFF_BASE_SECONDS * (2**attempt)

    def get(self, path, **kwargs):
        return self.request("GET", path, **kwargs)

    def post(self, path, json=None, **kwargs):
        return self.request("POST", path, json=json, **kwargs)

    def delete(self, path, **kwargs):
        return self.request("DELETE", path, **kwargs)