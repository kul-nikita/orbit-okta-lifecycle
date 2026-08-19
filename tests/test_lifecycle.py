"""Tests for Okta user lifecycle operations.

Validates ``create_user``, ``activate_user``, ``deactivate_user``, and
``list_users`` using the ``responses`` library to mock HTTP calls. Covers
default parameters, custom parameters (activate, send_email, group_ids,
search, filter_), error handling (409, 400, 403, 500), no-op cases, and
pagination behaviour.

Dependencies:
    pytest, responses, src.lifecycle, src.okta_client
"""

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
    """Default call now uses activate=True, sendEmail=True."""
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
        match=[responses.matchers.query_param_matcher({"activate": "true", "sendEmail": "true"})],
    )

    client = OktaClient()
    user = lifecycle.create_user(client, profile)

    assert user["id"] == "00u123"
    assert b"profile" in responses.calls[0].request.body


@responses.activate
def test_create_user_activate_false_sets_query_param(okta_env):
    profile = {"email": "grace@example.com", "login": "grace@example.com"}
    responses.add(
        responses.POST,
        _url("/users"),
        json={"id": "00u456", "profile": profile},
        status=200,
        match=[responses.matchers.query_param_matcher({"activate": "false", "sendEmail": "true"})],
    )

    client = OktaClient()
    user = lifecycle.create_user(client, profile, activate=False)

    assert user["id"] == "00u456"


@responses.activate
def test_create_user_includes_group_ids_when_given(okta_env):
    profile = {"email": "grace@example.com", "login": "grace@example.com"}
    responses.add(
        responses.POST,
        _url("/users"),
        json={"id": "00u789", "profile": profile},
        status=200,
        match=[responses.matchers.query_param_matcher({"activate": "true", "sendEmail": "true"})],
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
        match=[responses.matchers.query_param_matcher({"activate": "true", "sendEmail": "true"})],
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
        match=[responses.matchers.query_param_matcher({"activate": "true", "sendEmail": "true"})],
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
        responses.GET,
        _url("/users/00u123"),
        json={"id": "00u123", "status": "STAGED"},
        status=200,
    )
    responses.add(
        responses.POST,
        _url("/users/00u123/lifecycle/activate"),
        json={"status": "ACTIVE", "activationUrl": "https://example.com/activate"},
        status=200,
        match=[responses.matchers.query_param_matcher({"sendEmail": "true"})],
    )

    client = OktaClient()
    result = lifecycle.activate_user(client, "00u123")

    assert result["status"] == "activation_started"
    assert result["user"]["status"] == "ACTIVE"


@responses.activate
def test_activate_user_send_email_false_sets_query_param(okta_env):
    responses.add(
        responses.GET,
        _url("/users/00u123"),
        json={"id": "00u123", "status": "STAGED"},
        status=200,
    )
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
    responses.add(
        responses.GET,
        _url("/users/00u123"),
        json={"id": "00u123", "status": "ACTIVE"},
        status=200,
    )

    client = OktaClient()
    result = lifecycle.activate_user(client, "00u123")

    assert result["status"] == "already_active"
    assert len(responses.calls) == 1


@responses.activate
def test_activate_user_403_propagates(okta_env):
    """403 from the lifecycle endpoint is not caught by the race-condition
    guard (which only handles 400/409), so it propagates."""
    responses.add(
        responses.GET,
        _url("/users/00u123"),
        json={"id": "00u123", "status": "STAGED"},
        status=200,
    )
    responses.add(
        responses.POST,
        _url("/users/00u123/lifecycle/activate"),
        json={"errorSummary": "Activation failed because the user is already active"},
        status=403,
    )

    client = OktaClient()
    with pytest.raises(lifecycle.OktaClientError):
        lifecycle.activate_user(client, "00u123")


@responses.activate
def test_activate_user_other_error_propagates(okta_env):
    responses.add(
        responses.GET,
        _url("/users/00u123"),
        json={"id": "00u123", "status": "STAGED"},
        status=200,
    )
    responses.add(
        responses.POST,
        _url("/users/00u123/lifecycle/activate"),
        json={"errorSummary": "server error"},
        status=500,
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
        responses.GET,
        _url("/users/00u123"),
        json={"id": "00u123", "status": "ACTIVE"},
        status=200,
    )
    responses.add(
        responses.POST,
        _url("/users/00u123/lifecycle/deactivate"),
        json={"status": "DEPROVISIONED"},
        status=200,
        match=[responses.matchers.query_param_matcher({"sendEmail": "false"})],
    )

    client = OktaClient()
    result = lifecycle.deactivate_user(client, "00u123")

    assert result["status"] == "deactivation_started"
    assert result["user"]["status"] == "DEPROVISIONED"


@responses.activate
def test_deactivate_user_already_deactivated_is_noop(okta_env):
    responses.add(
        responses.GET,
        _url("/users/00u123"),
        json={"id": "00u123", "status": "DEPROVISIONED"},
        status=200,
    )

    client = OktaClient()
    result = lifecycle.deactivate_user(client, "00u123")

    assert result["status"] == "already_deactivated"
    assert len(responses.calls) == 1


@responses.activate
def test_deactivate_user_send_email_true_sets_query_param(okta_env):
    responses.add(
        responses.GET,
        _url("/users/00u123"),
        json={"id": "00u123", "status": "ACTIVE"},
        status=200,
    )
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
    """Default unfiltered call makes two requests: one normal page,
    then a DEPROVISIONED-filtered page."""
    users_page = [{"id": "00u1"}, {"id": "00u2"}]
    responses.add(
        responses.GET,
        _url("/users"),
        json=users_page,
        status=200,
        match=[responses.matchers.query_param_matcher({"limit": "200"})],
    )
    responses.add(
        responses.GET,
        _url("/users"),
        json=[],
        status=200,
        match=[responses.matchers.query_param_matcher({"limit": "200", "filter": 'status eq "DEPROVISIONED"'})],
    )

    client = OktaClient()
    users = lifecycle.list_users(client)

    assert users == users_page
    assert len(responses.calls) == 2


@responses.activate
def test_list_users_follows_pagination_cursor(okta_env):
    """A full page (== page_size) triggers a follow-up request using
    the last user's id as the 'after' cursor."""
    page_size = 200
    first_page = [{"id": f"00u{i}"} for i in range(page_size)]
    second_page = [{"id": "00uLAST"}]

    next_url = _url("/users") + "?limit=200&after=00u199"

    responses.add(
        responses.GET,
        _url("/users"),
        json=first_page,
        status=200,
        match=[responses.matchers.query_param_matcher({"limit": str(page_size)})],
        headers={"Link": f'<{next_url}>; rel="next"'},
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
    # DEPROVISIONED page (empty)
    responses.add(
        responses.GET,
        _url("/users"),
        json=[],
        status=200,
        match=[responses.matchers.query_param_matcher({"limit": str(page_size), "filter": 'status eq "DEPROVISIONED"'})],
    )

    client = OktaClient()
    users = lifecycle.list_users(client)

    assert len(users) == page_size + 1
    assert users[-1]["id"] == "00uLAST"
    assert len(responses.calls) == 3


@responses.activate
def test_list_users_passes_search_and_filter_params(okta_env):
    """Explicit search/filter is passed through to Okta."""
    responses.add(
        responses.GET,
        _url("/users"),
        json=[{"id": "00u1"}],
        status=200,
        match=[
            responses.matchers.query_param_matcher(
                {
                    "limit": "200",
                    "filter": 'status eq "DEPROVISIONED"',
                }
            )
        ],
    )

    client = OktaClient()
    lifecycle.list_users(
        client,
        filter_='status eq "DEPROVISIONED"',
    )


@responses.activate
def test_list_users_both_search_and_filter_raises(okta_env):
    """Passing both search and filter_ raises ValueError."""
    client = OktaClient()
    with pytest.raises(ValueError, match="Use either search or filter_"):
        lifecycle.list_users(
            client,
            search='status eq "ACTIVE"',
            filter_='profile.department eq "eng"',
        )
