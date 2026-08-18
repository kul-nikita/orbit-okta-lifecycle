"""Tests for the Okta API client."""

import pytest
import responses

from src.okta_client import OktaClient, OktaClientError


@pytest.fixture
def okta_env(monkeypatch):
    monkeypatch.setenv("OKTA_DOMAIN", "dev-000000.okta.com")
    monkeypatch.setenv("OKTA_API_TOKEN", "test-token")


def _url(path=""):
    return f"https://dev-000000.okta.com/api/v1{path}"


@responses.activate
def test_get_returns_response_with_auth_header(okta_env):
    responses.add(responses.GET, _url("/users"), json=[{"id": "00u1"}], status=200)

    client = OktaClient()
    response = client.get("/users")

    assert response.json() == [{"id": "00u1"}]
    assert responses.calls[0].request.headers["Authorization"] == "SSWS test-token"


@responses.activate
def test_retries_on_429(okta_env, monkeypatch):
    monkeypatch.setattr("time.sleep", lambda _: None)
    responses.add(responses.GET, _url("/users"), status=429)
    responses.add(responses.GET, _url("/users"), json=[], status=200)

    client = OktaClient()
    response = client.get("/users")

    assert response.json() == []
    assert len(responses.calls) == 2


@responses.activate
def test_http_error_raises(okta_env):
    responses.add(responses.GET, _url("/users"), status=500, body="boom")

    client = OktaClient()
    with pytest.raises(OktaClientError, match="500"):
        client.get("/users")


def test_missing_config_raises(monkeypatch):
    monkeypatch.delenv("OKTA_DOMAIN", raising=False)
    monkeypatch.delenv("OKTA_API_TOKEN", raising=False)

    with pytest.raises(OktaClientError):
        OktaClient()


@responses.activate
def test_delete_sends_auth_and_returns_response(okta_env):
    responses.add(responses.DELETE, _url("/users/00u1"), status=204)

    client = OktaClient()
    response = client.delete("/users/00u1")

    assert response.status_code == 204
    assert responses.calls[0].request.headers["Authorization"] == "SSWS test-token"
    assert responses.calls[0].request.method == "DELETE"


@responses.activate
def test_429_exhaustion_raises_after_max_retries(okta_env, monkeypatch):
    monkeypatch.setattr("time.sleep", lambda _: None)
    for _ in range(5):
        responses.add(responses.GET, _url("/users"), status=429)

    client = OktaClient()
    with pytest.raises(OktaClientError, match="rate-limited"):
        client.get("/users")

    # MAX_RETRIES attempts were made, no successful response ever returned.
    assert len(responses.calls) == 5


@responses.activate
def test_backoff_sleeps_with_exponential_delays(okta_env, monkeypatch):
    sleep_calls = []
    monkeypatch.setattr("time.sleep", lambda seconds: sleep_calls.append(seconds))

    responses.add(responses.GET, _url("/users"), status=429)
    responses.add(responses.GET, _url("/users"), status=429)
    responses.add(responses.GET, _url("/users"), json=[], status=200)

    client = OktaClient()
    client.get("/users")

    # BACKOFF_BASE_SECONDS * 2**attempt for attempts 0 and 1.
    assert sleep_calls == [1.0, 2.0]


@responses.activate
def test_retry_after_header_overrides_backoff(okta_env, monkeypatch):
    sleep_calls = []
    monkeypatch.setattr("time.sleep", lambda seconds: sleep_calls.append(seconds))

    responses.add(
        responses.GET, _url("/users"), status=429, headers={"Retry-After": "3"}
    )
    responses.add(responses.GET, _url("/users"), json=[], status=200)

    client = OktaClient()
    client.get("/users")

    # Server-provided Retry-After (3s) is honored instead of the
    # exponential fallback (1.0s for attempt 0).
    assert sleep_calls == [3.0]