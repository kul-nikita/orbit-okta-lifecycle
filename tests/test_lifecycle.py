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


# ---------------------------------------------------------------------
# create_user
# ---------------------------------------------------------------------

@responses.activate
def test_create_user_posts_profile_and_returns_user(okta_env):
    """Default call (activate not passed) must hit activate=false,
    matching create_user's documented default (STAGED, no email)."""
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
        match=[responses.matchers.query_param_matcher({"activate": "false"})],
    )

    client = OktaClient()
    user = lifecycle.create_user(client, profile)

    assert user["id"] == "00u123"
    assert b"profile" in responses.calls[0].request.body


@responses.activate
def test_create_user_activate_true_sets_query_param(okta_env):
    profile = {"email": "grace@example.com", "login": "grace@example.com"}
    responses.add(
        responses.POST,
        _url("/users"),
        json={"id": "00u456", "profile": profile},
        status=200,
        match=[responses.matchers.query_param_matcher({"activate": "true"})],
    )

    client = OktaClient()
    user = lifecycle.create_user(client, profile, activate=True)

    assert user["id"] == "00u456"


@responses.activate
def test_create_user_includes_group_ids_when_given(okta_env):
    profile = {"email": "grace@example.com", "login": "grace@example.com"}
    responses.add(
        responses.POST,
        _url("/users"),
        json={"id": "00u789", "profile": profile},
        status=200,
        match=[responses.matchers.query_param_matcher({"activate": "false"})],
    )

    client = OktaClient()
    lifecycle.create_user(client, profile, group_ids=["00g1", "00g2"])

    body = responses.calls[0].request.body
    assert b"groupIds" in body
    assert b"00g1" in body


@responses.activate
def test_create_user_duplicate_raises_user_already_exists(okta_env):
    profile = {"email": "dupe@example.com", "login": "dupe@example.com"}
    responses.add(
        responses.POST,
        _url("/users"),
        json={"errorSummary": "login already exists"},
        status=409,
        match=[responses.matchers.query_param_matcher({"activate": "false"})],
    )

    client = OktaClient()
    with pytest.raises(lifecycle.UserAlreadyExists):
        lifecycle.create_user(client, profile)


@responses.activate
def test_create_user_invalid_profile_raises_validation_error(okta_env):
    profile = {"email": "not-an-email"}
    responses.add(
        responses.POST,
        _url("/users"),
        json={"errorSummary": "invalid email"},
        status=400,
        match=[responses.matchers.query_param_matcher({"activate": "false"})],
    )

    client = OktaClient()
    with pytest.raises(lifecycle.ValidationError):
        lifecycle.create_user(client, profile)


# ---------------------------------------------------------------------
# activate_user
# ---------------------------------------------------------------------

@responses.activate
def test_activate_user_returns_response_json(okta_env):
    responses.add(
        responses.POST,
        _url("/users/00u123/lifecycle/activate"),
        json={"status": "ACTIVE", "activationUrl": "https://example.com/activate"},
        status=200,
        match=[responses.matchers.query_param_matcher({"sendEmail": "true"})],
    )

    client = OktaClient()
    result = lifecycle.activate_user(client, "00u123")

    assert result["status"] == "ACTIVE"


@responses.activate
def test_activate_user_send_email_false_sets_query_param(okta_env):
    responses.add(
        responses.POST,
        _url("/users/00u123/lifecycle/activate"),
        json={"status": "ACTIVE"},
        status=200,
        match=[responses.matchers.query_param_matcher({"sendEmail": "false"})],
    )

    client = OktaClient()
    lifecycle.activate_user(client, "00u123", send_email=False)


@responses.activate
def test_activate_user_already_active_is_noop(okta_env):
    """Okta 400s when activating an already-active user; this should
    be treated as a no-op, not raise."""
    responses.add(
        responses.POST,
        _url("/users/00u123/lifecycle/activate"),
        json={"errorSummary": "user already active"},
        status=400,
        match=[responses.matchers.query_param_matcher({"sendEmail": "true"})],
    )

    client = OktaClient()
    result = lifecycle.activate_user(client, "00u123")

    assert result == {"status": "already_active"}


@responses.activate
def test_activate_user_already_active_403_is_noop(okta_env):
    """Some Okta orgs return 403 (not 400) when activating an
    already-active user; treat it the same way."""
    responses.add(
        responses.POST,
        _url("/users/00u123/lifecycle/activate"),
        json={"errorSummary": "Activation failed because the user is already active"},
        status=403,
        match=[responses.matchers.query_param_matcher({"sendEmail": "true"})],
    )

    client = OktaClient()
    result = lifecycle.activate_user(client, "00u123")

    assert result == {"status": "already_active"}


@responses.activate
def test_activate_user_other_error_propagates(okta_env):
    responses.add(
        responses.POST,
        _url("/users/00u123/lifecycle/activate"),
        json={"errorSummary": "server error"},
        status=500,
        match=[responses.matchers.query_param_matcher({"sendEmail": "true"})],
    )

    client = OktaClient()
    with pytest.raises(lifecycle.OktaClientError):
        lifecycle.activate_user(client, "00u123")


# ---------------------------------------------------------------------
# deactivate_user
# ---------------------------------------------------------------------

@responses.activate
def test_deactivate_user_returns_response_json(okta_env):
    responses.add(
        responses.POST,
        _url("/users/00u123/lifecycle/deactivate"),
        json={"status": "DEPROVISIONED"},
        status=200,
        match=[responses.matchers.query_param_matcher({"sendEmail": "false"})],
    )

    client = OktaClient()
    result = lifecycle.deactivate_user(client, "00u123")

    assert result["status"] == "DEPROVISIONED"


@responses.activate
def test_deactivate_user_already_deactivated_is_noop(okta_env):
    responses.add(
        responses.POST,
        _url("/users/00u123/lifecycle/deactivate"),
        json={"errorSummary": "user already deprovisioned"},
        status=400,
        match=[responses.matchers.query_param_matcher({"sendEmail": "false"})],
    )

    client = OktaClient()
    result = lifecycle.deactivate_user(client, "00u123")

    assert result == {"status": "already_deactivated"}


@responses.activate
def test_deactivate_user_send_email_true_sets_query_param(okta_env):
    responses.add(
        responses.POST,
        _url("/users/00u123/lifecycle/deactivate"),
        json={"status": "DEPROVISIONED"},
        status=200,
        match=[responses.matchers.query_param_matcher({"sendEmail": "true"})],
    )

    client = OktaClient()
    lifecycle.deactivate_user(client, "00u123", send_email=True)


# ---------------------------------------------------------------------
# list_users / pagination
# ---------------------------------------------------------------------

@responses.activate
def test_list_users_single_page_short_of_limit(okta_env):
    """A page shorter than the page size means no further pages."""
    users_page = [{"id": "00u1"}, {"id": "00u2"}]
    responses.add(
        responses.GET,
        _url("/users"),
        json=users_page,
        status=200,
        match=[responses.matchers.query_param_matcher({"limit": "200"})],
    )

    client = OktaClient()
    users = lifecycle.list_users(client)

    assert users == users_page
    assert len(responses.calls) == 1


@responses.activate
def test_list_users_follows_pagination_cursor(okta_env):
    """A full page (== page_size) triggers a follow-up request using
    the last user's id as the 'after' cursor."""
    page_size = 200
    first_page = [{"id": f"00u{i}"} for i in range(page_size)]
    second_page = [{"id": "00uLAST"}]

    responses.add(
        responses.GET,
        _url("/users"),
        json=first_page,
        status=200,
        match=[responses.matchers.query_param_matcher({"limit": str(page_size)})],
    )
    responses.add(
        responses.GET,
        _url("/users"),
        json=second_page,
        status=200,
        match=[
            responses.matchers.query_param_matcher(
                {"limit": str(page_size), "after": "00u199"}
            )
        ],
    )

    client = OktaClient()
    users = lifecycle.list_users(client)

    assert len(users) == page_size + 1
    assert users[-1]["id"] == "00uLAST"
    assert len(responses.calls) == 2


@responses.activate
def test_list_users_passes_search_and_filter_params(okta_env):
    responses.add(
        responses.GET,
        _url("/users"),
        json=[{"id": "00u1"}],
        status=200,
        match=[
            responses.matchers.query_param_matcher(
                {
                    "limit": "200",
                    "search": 'status eq "ACTIVE"',
                    "filter": 'profile.department eq "eng"',
                }
            )
        ],
    )

    client = OktaClient()
    lifecycle.list_users(
        client,
        search='status eq "ACTIVE"',
        filter_='profile.department eq "eng"',
    )
