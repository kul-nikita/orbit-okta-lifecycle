"""CSV import/export helpers for Okta users."""

import csv

from . import lifecycle
from .lifecycle import UserAlreadyExists, ValidationError

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
    """Import users from a CSV file into Okta."""

    summary = {
        "created": 0,
        "failed": 0,
        "errors": [],
    }

    with open(filepath, "r", newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)

        for row in reader:
            try:
                if (
                    not row.get("first_name")
                    or not row.get("last_name")
                    or not row.get("email")
                ):
                    raise ValidationError(
                        "CSV row is missing first_name, last_name, or email."
                    )

                profile = {
                    "firstName": row["first_name"],
                    "lastName": row["last_name"],
                    "email": row["email"],
                    "login": row["email"],
                }

                lifecycle.create_user(client, profile)
                summary["created"] += 1

            except UserAlreadyExists:
                summary["failed"] += 1
                summary["errors"].append(
                    f"{row.get('email', 'Unknown user')}: User already exists."
                )

            except ValidationError as exc:
                summary["failed"] += 1
                summary["errors"].append(
                    f"{row.get('email', 'Unknown user')}: {exc}"
                )

            

    return summary