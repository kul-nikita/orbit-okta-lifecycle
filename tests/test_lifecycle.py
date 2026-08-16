"""Tests for Okta user lifecycle operations."""

import pytest
import responses

from src import lifecycle
from src.okta_client import OktaClient


@pytest.fixture
def okta_env(monkeypatch):
    monkeypatch.setenv("OKTA_DOMAIN", "dev-000000.okta.com")
    monkeypatch.setenv("OKTA_API_TOKEN", "test-token")


def _url(path=""):
    return f"https://dev-000000.okta.com/api/v1{path}"


@responses.activate
def test_create_user_posts_profile_and_returns_user(okta_env):
    profile = {
        "email": "ada@example.com",
        "login": "ada@example.com",
        "firstName": "Ada",
        "lastName": "Lovelace",
    }
    responses.add(
        responses.POST,
        _url("/users"),
        json={"id": "00u123", "profile": profile},
        status=200,
        match=[responses.matchers.query_param_matcher({"activate": "true"})],
    )

    client = OktaClient()
    user = lifecycle.create_user(client, profile)

    assert user["id"] == "00u123"
    assert b"profile" in responses.calls[0].request.body


# TODO(owner): add tests for activate_user, deactivate_user, and
# list_users pagination.
