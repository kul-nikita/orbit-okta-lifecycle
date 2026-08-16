"""CSV import/export helpers for Okta users."""

import csv

from . import lifecycle

EXPORT_FIELDS = [
    "id",
    "status",
    "email",
    "login",
    "first_name",
    "last_name",
]


def export_users_to_csv(client, filepath):
    """Write every Okta user to a CSV file at ``filepath``.

    TODO(owner): confirm the column set, add streaming for large exports,
    and handle missing profile attributes.
    """
    users = lifecycle.list_users(client)
    with open(filepath, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=EXPORT_FIELDS)
        writer.writeheader()
        for user in users:
            profile = user.get("profile", {})
            writer.writerow(
                {
                    "id": user.get("id"),
                    "status": user.get("status"),
                    "email": profile.get("email"),
                    "login": profile.get("login"),
                    "first_name": profile.get("firstName"),
                    "last_name": profile.get("lastName"),
                }
            )
    return filepath


def import_users_from_csv(client, filepath):
    """Import users from a CSV file into Okta.

    TODO(owner): enhancement — validate the CSV, call
    ``lifecycle.create_user`` per row, and collect per-row failures.
    """
    raise NotImplementedError
