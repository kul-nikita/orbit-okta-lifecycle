"""Okta user lifecycle operations.

This module provides a state-aware, idempotent lifecycle layer.

Important Okta states handled here include:

    STAGED
    PROVISIONED
    ACTIVE
    SUSPENDED
    DEPROVISIONED
    LOCKED_OUT
    RECOVERY

The lifecycle functions intentionally do not treat every HTTP 400/403
as a successful no-op. The user's actual Okta status is authoritative.
"""

from __future__ import annotations

from urllib.parse import parse_qs, quote, urlparse

from .okta_client import OktaClientError


class UserAlreadyExists(Exception):
    """Raised when creation encounters an existing login."""


class UserNotFound(Exception):
    """Raised when an expected Okta user does not exist."""


class ValidationError(Exception):
    """Raised when Okta rejects invalid user/profile data."""


class InvalidLifecycleTransition(Exception):
    """Raised when a lifecycle operation is invalid for the user's state."""


# States that can be reconciled automatically by ensure_user_active().
ACTIVE_STATUS = "ACTIVE"

ACTIVATABLE_STATUSES = {
    "STAGED",
    "DEPROVISIONED",
}

REACTIVATABLE_STATUSES = {
    "PROVISIONED",
    "RECOVERY",
}

SUSPENDED_STATUS = "SUSPENDED"
LOCKED_OUT_STATUS = "LOCKED_OUT"


def _error_message(exc: OktaClientError) -> str:
    """Extract a useful Okta error message."""
    body = exc.response_body

    if isinstance(body, dict):
        error_summary = body.get("errorSummary")
        if error_summary:
            return str(error_summary)

        error_code = body.get("errorCode")
        if error_code:
            return str(error_code)

    return str(exc)


def _is_not_found(exc: OktaClientError) -> bool:
    """Return True if the error indicates a 404 Not Found."""
    return exc.status_code == 404


def _is_conflict(exc: OktaClientError) -> bool:
    """Return True if the error indicates a 409 Conflict."""
    return exc.status_code == 409


def _response_json(response):
    """Parse and return the JSON body of an Okta API response."""
    return response.json()


def get_user(client, user_id):
    """Get an Okta user by ID or login.

    Okta accepts either a user ID or login in this endpoint.
    """
    try:
        response = client.get(f"/users/{quote(str(user_id), safe='')}")
    except OktaClientError as exc:
        if _is_not_found(exc):
            raise UserNotFound(
                f"Okta user {user_id!r} was not found."
            ) from exc
        raise

    return _response_json(response)


def get_user_by_login(client, login):
    """Find an Okta user by login.

    Returns None if the user does not exist.
    """
    try:
        response = client.get(f"/users/{login}")
    except OktaClientError as exc:
        if _is_not_found(exc):
            return None
        raise

    return _response_json(response)


def create_user(
    client,
    profile,
    activate=True,
    send_email=True,
    group_ids=None,
):
    """Create a new Okta user.

    By default:
        - creates the user
        - activates immediately
        - requests the activation email

    Set activate=False to create a STAGED user.

    Raises:
        UserAlreadyExists: login already exists.
        ValidationError: profile rejected by Okta.
    """
    body = {
        "profile": profile,
    }

    if group_ids:
        body["groupIds"] = list(group_ids)

    try:
        response = client.post(
            "/users",
            params={
                "activate": str(activate).lower(),
                "sendEmail": str(send_email).lower(),
            },
            json=body,
        )
    except OktaClientError as exc:
        if _is_conflict(exc):
            login = profile.get("login") or profile.get("email")

            raise UserAlreadyExists(
                f"A user with login/email {login!r} already exists."
            ) from exc

        if exc.status_code == 400:
            raise ValidationError(
                "Okta rejected this profile as invalid: "
                f"{_error_message(exc)}"
            ) from exc

        raise

    return _response_json(response)


def activate_user(
    client,
    user_id,
    send_email=True,
):
    """Activate a STAGED or DEPROVISIONED user.

    If the user is already ACTIVE, this is an idempotent no-op.

    The operation itself may be asynchronous; the returned object is
    the response from Okta.
    """
    user = get_user(client, user_id)
    status = user.get("status")

    if status == ACTIVE_STATUS:
        return {
            "status": "already_active",
            "user": user,
        }

    if status not in ACTIVATABLE_STATUSES:
        raise InvalidLifecycleTransition(
            f"Cannot activate user {user_id!r} from "
            f"status {status!r}. "
            f"Expected one of {sorted(ACTIVATABLE_STATUSES)}."
        )

    try:
        response = client.post(
            f"/users/{user_id}/lifecycle/activate",
            params={
                "sendEmail": str(send_email).lower(),
            },
        )
    except OktaClientError as exc:
        # Race condition protection:
        # another process may have activated the user between our GET
        # and POST.
        if exc.status_code in (400, 409):
            current = get_user(client, user_id)

            if current.get("status") == ACTIVE_STATUS:
                return {
                    "status": "already_active",
                    "user": current,
                }

        raise

    return {
        "status": "activation_started",
        "user": _response_json(response),
    }


def reactivate_user(
    client,
    user_id,
    send_email=True,
):
    """Restart activation for a PROVISIONED or RECOVERY user."""
    user = get_user(client, user_id)
    status = user.get("status")

    if status == ACTIVE_STATUS:
        return {
            "status": "already_active",
            "user": user,
        }

    if status not in REACTIVATABLE_STATUSES:
        raise InvalidLifecycleTransition(
            f"Cannot reactivate user {user_id!r} from "
            f"status {status!r}. "
            f"Expected one of {sorted(REACTIVATABLE_STATUSES)}."
        )

    try:
        response = client.post(
            f"/users/{user_id}/lifecycle/reactivate",
            params={
                "sendEmail": str(send_email).lower(),
            },
        )
    except OktaClientError as exc:
        if exc.status_code in (400, 409):
            current = get_user(client, user_id)

            if current.get("status") == ACTIVE_STATUS:
                return {
                    "status": "already_active",
                    "user": current,
                }

        raise

    return {
        "status": "reactivation_started",
        "user": _response_json(response),
    }


def deactivate_user(
    client,
    user_id,
    send_email=False,
):
    """Deactivate any user that is not already DEPROVISIONED.

    Okta treats deactivation as a destructive operation.  It is
    idempotent here: DEPROVISIONED returns a no-op result.
    """
    user = get_user(client, user_id)
    current_status = user.get("status")

    if current_status == "DEPROVISIONED":
        return {
            "status": "already_deactivated",
            "user": user,
        }

    try:
        response = client.post(
            f"/users/{user_id}/lifecycle/deactivate",
            params={
                "sendEmail": str(send_email).lower(),
            },
        )
    except OktaClientError as exc:
        if exc.status_code in (400, 409):
            current = get_user(client, user_id)

            if current.get("status") == "DEPROVISIONED":
                return {
                    "status": "already_deactivated",
                    "user": current,
                }

        raise

    return {
        "status": "deactivation_started",
        "user": _response_json(response),
    }


def suspend_user(client, user_id):
    """Suspend an active user.

    ACTIVE -> SUSPENDED.
    """
    user = get_user(client, user_id)

    if user.get("status") == SUSPENDED_STATUS:
        return {
            "status": "already_suspended",
            "user": user,
        }

    if user.get("status") != ACTIVE_STATUS:
        raise InvalidLifecycleTransition(
            f"Cannot suspend user {user_id!r} from "
            f"status {user.get('status')!r}. Expected ACTIVE."
        )

    try:
        response = client.post(
            f"/users/{user_id}/lifecycle/suspend"
        )
    except OktaClientError as exc:
        if exc.status_code in (400, 409):
            current = get_user(client, user_id)

            if current.get("status") == SUSPENDED_STATUS:
                return {
                    "status": "already_suspended",
                    "user": current,
                }

        raise

    return {
        "status": "suspension_started",
        "user": _response_json(response),
    }


def unsuspend_user(client, user_id):
    """Unsuspend a suspended user."""
    user = get_user(client, user_id)

    if user.get("status") == ACTIVE_STATUS:
        return {
            "status": "already_active",
            "user": user,
        }

    if user.get("status") != SUSPENDED_STATUS:
        raise InvalidLifecycleTransition(
            f"Cannot unsuspend user {user_id!r} from "
            f"status {user.get('status')!r}. Expected SUSPENDED."
        )

    try:
        response = client.post(
            f"/users/{user_id}/lifecycle/unsuspend"
        )
    except OktaClientError as exc:
        if exc.status_code in (400, 409):
            current = get_user(client, user_id)

            if current.get("status") == ACTIVE_STATUS:
                return {
                    "status": "already_active",
                    "user": current,
                }

        raise

    return {
        "status": "unsuspension_started",
        "user": _response_json(response),
    }


def unlock_user(client, user_id):
    """Unlock a locked-out user."""
    user = get_user(client, user_id)

    if user.get("status") == ACTIVE_STATUS:
        return {
            "status": "already_active",
            "user": user,
        }

    if user.get("status") != LOCKED_OUT_STATUS:
        raise InvalidLifecycleTransition(
            f"Cannot unlock user {user_id!r} from "
            f"status {user.get('status')!r}. Expected LOCKED_OUT."
        )

    try:
        response = client.post(
            f"/users/{user_id}/lifecycle/unlock"
        )
    except OktaClientError as exc:
        if exc.status_code in (400, 409):
            current = get_user(client, user_id)

            if current.get("status") == ACTIVE_STATUS:
                return {
                    "status": "already_active",
                    "user": current,
                }

        raise

    return {
        "status": "unlock_started",
        "user": _response_json(response),
    }


def delete_user(client, user_id):
    """Delete an Okta user.

    Okta normally requires the user to be DEPROVISIONED before deletion.
    """
    user = get_user(client, user_id)

    if user.get("status") != "DEPROVISIONED":
        raise InvalidLifecycleTransition(
            f"Cannot delete user {user_id!r} while status is "
            f"{user.get('status')!r}. Deactivate the user first."
        )

    client.delete(f"/users/{user_id}")

    return {
        "status": "deleted",
        "user_id": user_id,
    }


def ensure_user_active(
    client,
    user_id,
    send_email=True,
):
    """Move an existing user toward ACTIVE.

    This is the preferred operation for UI/API workflows where the
    caller does not want to care about the exact current lifecycle
    state.
    """
    user = get_user(client, user_id)
    status = user.get("status")

    if status == ACTIVE_STATUS:
        return {
            "status": "already_active",
            "user": user,
        }

    if status in ACTIVATABLE_STATUSES:
        return activate_user(
            client,
            user_id,
            send_email=send_email,
        )

    if status in REACTIVATABLE_STATUSES:
        return reactivate_user(
            client,
            user_id,
            send_email=send_email,
        )

    if status == SUSPENDED_STATUS:
        return unsuspend_user(client, user_id)

    if status == LOCKED_OUT_STATUS:
        return unlock_user(client, user_id)

    raise InvalidLifecycleTransition(
        f"Cannot automatically activate user {user_id!r} "
        f"from Okta status {status!r}."
    )


def create_or_ensure_user(
    client,
    profile,
    *,
    activate=True,
    send_email=True,
    group_ids=None,
):
    """Create a user, or reconcile an existing user.

    This is the operation your UI should generally use.

    Behavior:

        user doesn't exist
            -> create

        user exists + activate=False
            -> return existing user

        user exists + activate=True
            -> ensure the existing user is active
    """
    try:
        user = create_user(
            client,
            profile,
            activate=activate,
            send_email=send_email,
            group_ids=group_ids,
        )

        return {
            "status": "created",
            "user": user,
        }

    except UserAlreadyExists:
        login = profile.get("login") or profile.get("email")

        if not login:
            raise

        existing = get_user_by_login(client, login)

        if existing is None:
            # Race condition: the user disappeared after the 409.
            raise

        if not activate:
            return {
                "status": "already_exists",
                "user": existing,
            }

        result = ensure_user_active(
            client,
            existing["id"],
            send_email=send_email,
        )

        return {
            "status": "already_exists_reconciled",
            "user": result["user"],
            "lifecycle": result,
        }


def _next_cursor(response):
    """Extract Okta's `after` cursor from Link: rel=next."""
    link_header = response.headers.get("Link", "")

    for link in link_header.split(","):
        if 'rel="next"' not in link and "rel=next" not in link:
            continue

        start = link.find("<")
        end = link.find(">")

        if start == -1 or end == -1:
            continue

        url = link[start + 1:end]
        query = parse_qs(urlparse(url).query)

        values = query.get("after")

        if values:
            return values[0]

    return None


def _list_users_pages(client, *, search=None, filter_=None):
    """Fetch one Okta /users query, following pagination."""
    users = []
    after = None
    page_size = 200

    while True:
        params = {
            "limit": page_size,
        }

        if after:
            params["after"] = after

        if search:
            params["search"] = search

        if filter_:
            params["filter"] = filter_

        response = client.get(
            "/users",
            params=params,
        )

        page = _response_json(response)

        if not isinstance(page, list):
            raise ValidationError(
                "Unexpected Okta /users response: expected a list."
            )

        users.extend(page)

        after = _next_cursor(response)

        if not after:
            break

    return users


def list_users(
    client,
    search=None,
    filter_=None,
):
    """Return Okta users, including DEPROVISIONED users for unfiltered lists.

    Okta's GET /users endpoint excludes DEPROVISIONED users by default.
    Orbit's directory and lifecycle UI must be able to see deprovisioned
    identities so they can be activated again or permanently deleted.

    When an explicit Okta search/filter expression is supplied, its exact
    Okta semantics are preserved.
    """
    if search and filter_:
        raise ValueError(
            "Use either search or filter_, not both."
        )

    # Preserve explicit Okta query semantics for callers that supplied
    # search/filter expressions. The UI's normal directory load is
    # unfiltered, so it takes the branch below and includes deprovisioned
    # users as well.
    if search or filter_:
        return _list_users_pages(
            client,
            search=search,
            filter_=filter_,
        )

    users = _list_users_pages(client)
    users.extend(
        _list_users_pages(
            client,
            filter_='status eq "DEPROVISIONED"',
        )
    )

    # Be defensive about duplicates in case Okta ever changes the default
    # /users behavior or an org has unusual lifecycle configuration.
    users_by_id = {}
    for user in users:
        user_id = user.get("id")
        if user_id:
            users_by_id[user_id] = user

    return list(users_by_id.values())
