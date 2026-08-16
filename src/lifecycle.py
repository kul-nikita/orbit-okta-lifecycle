"""User lifecycle operations on the Okta API.

Each function takes an :class:`okta_client.OktaClient` instance and is
kept intentionally thin so the lifecycle logic can evolve per-file.
"""


def create_user(client, profile):
    """Create (and activate) a new Okta user from an Okta profile dict.

    TODO(owner): decide how credentials / activation emails are handled,
    map Okta's 409 "login already exists" responses, and add group
    assignment.
    """
    response = client.post("/users?activate=true", json={"profile": profile})
    return response.json()


def activate_user(client, user_id):
    """Activate an Okta user by id.

    TODO(owner): handle the ``sendEmail`` flag and Okta's "already
    active" response codes.
    """
    response = client.post(f"/users/{user_id}/lifecycle/activate")
    return response.json()


def deactivate_user(client, user_id):
    """Deactivate an Okta user by id.

    TODO(owner): decide whether to also revoke sessions/apps and how to
    surface users that are already deactivated.
    """
    response = client.post(f"/users/{user_id}/lifecycle/deactivate")
    return response.json()


def list_users(client):
    """Return all Okta users, following pagination.

    TODO(owner): add filtering via ``query`` / ``filter`` params and
    settle on a sane page size.
    """
    users = []
    page_size = 200
    after = None
    while True:
        params = {"limit": page_size}
        if after is not None:
            params["after"] = after
        response = client.get("/users", params=params)
        page = response.json()
        users.extend(page)
        if len(page) < page_size:
            break
        after = page[-1]["id"]
    return users
