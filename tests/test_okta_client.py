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


# TODO(owner): add tests for backoff delays, the delete() helper, and
# 429-exhaustion behaviour.
