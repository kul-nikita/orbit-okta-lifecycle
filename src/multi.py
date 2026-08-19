"""Multi-tenant lifecycle operations.

Wraps the single-client lifecycle functions to run against multiple
Okta tenants simultaneously, returning combined results keyed by
tenant label.
"""

from . import lifecycle


def create_user(clients, profile, activate=False, group_ids=None):
    """Create a user across all tenants. Returns per-tenant results."""
    results = {}
    for client in clients:
        try:
            result = lifecycle.create_user(
                client, profile, activate=activate, group_ids=group_ids
            )
            results[client.label] = result
        except Exception as exc:
            results[client.label] = {"error": str(exc)}
    return results


def activate_user(clients, user_id, send_email=False):
    """Activate a user across all tenants. Returns per-tenant results."""
    results = {}
    for client in clients:
        try:
            result = lifecycle.activate_user(
                client, user_id, send_email=send_email
            )
            results[client.label] = result
        except Exception as exc:
            results[client.label] = {"error": str(exc)}
    return results


def deactivate_user(clients, user_id, send_email=False):
    """Deactivate a user across all tenants. Returns per-tenant results."""
    results = {}
    for client in clients:
        try:
            result = lifecycle.deactivate_user(
                client, user_id, send_email=send_email
            )
            results[client.label] = result
        except Exception as exc:
            results[client.label] = {"error": str(exc)}
    return results


def list_users(clients, search=None, filter_=None):
    """List users across all tenants. Returns combined flat list with tenant tag."""
    all_users = []
    for client in clients:
        users = lifecycle.list_users(client, search=search, filter_=filter_)
        for user in users:
            user["_tenant"] = client.label
        all_users.extend(users)
    return all_users


def list_users_by_tenant(clients, search=None, filter_=None):
    """List users grouped by tenant. Returns dict keyed by tenant label."""
    results = {}
    for client in clients:
        results[client.label] = lifecycle.list_users(
            client, search=search, filter_=filter_
        )
    return results
