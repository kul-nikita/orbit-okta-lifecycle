import re

from .okta_client import OktaClientError


class UserAlreadyExists(Exception):
    """Raised when Okta returns 409 for a duplicate login/email."""
    pass


class ValidationError(Exception):
    """Raised when Okta rejects the profile as invalid (e.g. malformed
    email, missing required field) — a 400 that is NOT the
    'already active/deactivated' no-op case."""
    pass


def _status_code_of(exc: OktaClientError):
    """Best-effort extraction of the HTTP status code from an
    OktaClientError's message. Returns None if it can't be found.
    """
    code = getattr(exc, "status_code", None)
    if code is not None:
        return code
    match = re.search(r"->\s*(\d{3}):", str(exc))
    return int(match.group(1)) if match else None


def create_user(client, profile, activate=False, group_ids=None):
    """Create a new Okta user from an Okta profile dict.

    activate=False (default) creates the user in STAGED status — no
    activation email sent. Pass activate=True to send it immediately.
    group_ids, if given, assigns the user to those Okta group IDs at
    creation time.
    """
    body = {"profile": profile}
    if group_ids:
        body["groupIds"] = group_ids

    try:
        response = client.post(
            f"/users?activate={'true' if activate else 'false'}", json=body
        )
    except OktaClientError as e:
        code = _status_code_of(e)
        if code == 409:
            raise UserAlreadyExists(
                f"A user with this login/email already exists: "
                f"{profile.get('login') or profile.get('email')}"
            ) from e
        if code == 400:
            raise ValidationError(
                f"Okta rejected this profile as invalid "
                f"(check email format / required fields): {e}"
            ) from e
        raise
    return response.json()


def activate_user(client, user_id, send_email=False):
    """Activate an Okta user by id. Only valid from STAGED status.

    Returns the activation response, or {"status": "already_active"}
    if the user was already active (Okta 400s on this — treated as a
    no-op rather than an error).
    """
    try:
        response = client.post(
            f"/users/{user_id}/lifecycle/activate?sendEmail=false"
        )
    except OktaClientError as e:
        if _status_code_of(e) == 400:
            return {"status": "already_active"}
        raise
    return response.json()


def deactivate_user(client, user_id, send_email=False):
    """Deactivate an Okta user by id (ACTIVE/SUSPENDED -> DEPROVISIONED).

    Returns {"status": "already_deactivated"} as a no-op if the user
    was already deprovisioned, instead of raising.
    """
    try:
        response = client.post(
            f"/users/{user_id}/lifecycle/deactivate?sendEmail=false"
        )
    except OktaClientError as e:
        if _status_code_of(e) == 400:
            return {"status": "already_deactivated"}
        raise
    return response.json()


def list_users(client, search=None, filter_=None):
    """Return all Okta users, following pagination.

    search: Okta SCIM-style search expression (e.g. 'status eq "ACTIVE"')
    filter_: Okta filter expression (older/simpler syntax — some
             attributes only support one or the other; check Okta docs
             for which your query needs)
    """
    users = []
    page_size = 200
    after = None
    while True:
        params = {"limit": page_size}
        if after is not None:
            params["after"] = after
        if search:
            params["search"] = search
        if filter_:
            params["filter"] = filter_

        response = client.get("/users", params=params)
        page = response.json()
        users.extend(page)
        if len(page) < page_size:
            break
        after = page[-1]["id"]
    return users
