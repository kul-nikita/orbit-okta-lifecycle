"""Orbit — Okta user lifecycle orchestration CLI.

Run from the repo root with:

    python -m src.cli --help
"""

from __future__ import annotations

import json

import click
from dotenv import load_dotenv

from . import export, lifecycle
from .okta_client import OktaClient, OktaClientError


def _client():
    return OktaClient()


def _print_user_result(result):
    """Print a consistent lifecycle result."""
    status = result.get("status", "unknown")
    user = result.get("user") or {}

    user_id = user.get("id") or result.get("user_id")

    if user_id:
        click.echo(f"Status: {status}")
        click.echo(f"User  : {user_id}")
    else:
        click.echo(f"Status: {status}")


def _handle_error(exc):
    """Turn known application errors into useful CLI errors."""
    if isinstance(exc, lifecycle.UserAlreadyExists):
        raise click.ClickException(str(exc))

    if isinstance(exc, lifecycle.UserNotFound):
        raise click.ClickException(str(exc))

    if isinstance(exc, lifecycle.ValidationError):
        raise click.ClickException(str(exc))

    if isinstance(exc, lifecycle.InvalidLifecycleTransition):
        raise click.ClickException(str(exc))

    if isinstance(exc, OktaClientError):
        raise click.ClickException(str(exc))

    raise exc


@click.group()
def cli():
    """Orbit commands for managing Okta user lifecycle."""


@cli.command()
@click.option(
    "--email",
    required=True,
    help="Login/email for the user.",
)
@click.option(
    "--first-name",
    required=True,
    help="User's first name.",
)
@click.option(
    "--last-name",
    required=True,
    help="User's last name.",
)
@click.option(
    "--activate/--no-activate",
    default=True,
    show_default=True,
    help="Activate immediately after creation.",
)
@click.option(
    "--send-email/--no-send-email",
    default=True,
    show_default=True,
    help="Ask Okta to send the activation email.",
)
def create(
    email,
    first_name,
    last_name,
    activate,
    send_email,
):
    """Create a user, or reconcile an existing login."""
    client = _client()

    profile = {
        "email": email,
        "login": email,
        "firstName": first_name,
        "lastName": last_name,
    }

    try:
        result = lifecycle.create_or_ensure_user(
            client,
            profile,
            activate=activate,
            send_email=send_email,
        )
    except Exception as exc:
        _handle_error(exc)
        return

    _print_user_result(result)

    if activate:
        click.echo(
            "Activation workflow requested. "
            "Check the user's Okta status before assuming "
            "the asynchronous transition has completed."
        )


@cli.command()
@click.argument("user_id")
def get(user_id):
    """Get the current Okta state of a user."""
    client = _client()

    try:
        user = lifecycle.get_user(client, user_id)
    except Exception as exc:
        _handle_error(exc)
        return

    click.echo(json.dumps(user, indent=2))


@cli.command()
@click.argument("user_id")
@click.option(
    "--send-email/--no-send-email",
    default=True,
    show_default=True,
)
def activate(user_id, send_email):
    """Activate a STAGED or DEPROVISIONED user."""
    client = _client()

    try:
        result = lifecycle.activate_user(
            client,
            user_id,
            send_email=send_email,
        )
    except Exception as exc:
        _handle_error(exc)
        return

    _print_user_result(result)


@cli.command()
@click.argument("user_id")
@click.option(
    "--send-email/--no-send-email",
    default=True,
    show_default=True,
)
def reactivate(user_id, send_email):
    """Restart activation for a PROVISIONED or RECOVERY user."""
    client = _client()

    try:
        result = lifecycle.reactivate_user(
            client,
            user_id,
            send_email=send_email,
        )
    except Exception as exc:
        _handle_error(exc)
        return

    _print_user_result(result)


@cli.command()
@click.argument("user_id")
@click.option(
    "--send-email/--no-send-email",
    default=False,
    show_default=True,
)
def deactivate(user_id, send_email):
    """Deactivate any user that is not already DEPROVISIONED."""
    client = _client()

    try:
        result = lifecycle.deactivate_user(
            client,
            user_id,
            send_email=send_email,
        )
    except Exception as exc:
        _handle_error(exc)
        return

    _print_user_result(result)


@cli.command()
@click.argument("user_id")
def suspend(user_id):
    """Suspend an ACTIVE user."""
    client = _client()

    try:
        result = lifecycle.suspend_user(
            client,
            user_id,
        )
    except Exception as exc:
        _handle_error(exc)
        return

    _print_user_result(result)


@cli.command()
@click.argument("user_id")
def unsuspend(user_id):
    """Unsuspend a SUSPENDED user."""
    client = _client()

    try:
        result = lifecycle.unsuspend_user(
            client,
            user_id,
        )
    except Exception as exc:
        _handle_error(exc)
        return

    _print_user_result(result)


@cli.command()
@click.argument("user_id")
def unlock(user_id):
    """Unlock a LOCKED_OUT user."""
    client = _client()

    try:
        result = lifecycle.unlock_user(
            client,
            user_id,
        )
    except Exception as exc:
        _handle_error(exc)
        return

    _print_user_result(result)


@cli.command("ensure-active")
@click.argument("user_id")
@click.option(
    "--send-email/--no-send-email",
    default=True,
    show_default=True,
)
def ensure_active(user_id, send_email):
    """Move an existing user toward ACTIVE."""
    client = _client()

    try:
        result = lifecycle.ensure_user_active(
            client,
            user_id,
            send_email=send_email,
        )
    except Exception as exc:
        _handle_error(exc)
        return

    _print_user_result(result)


@cli.command()
@click.argument("user_id")
@click.confirmation_option(
    prompt="Are you sure you want to permanently delete this user?"
)
def delete(user_id):
    """Permanently delete a DEPROVISIONED user."""
    client = _client()

    try:
        result = lifecycle.delete_user(
            client,
            user_id,
        )
    except Exception as exc:
        _handle_error(exc)
        return

    _print_user_result(result)


@cli.command("list")
@click.option(
    "--search",
    default=None,
    help='Okta search expression, e.g. status eq "ACTIVE".',
)
@click.option(
    "--filter",
    "filter_",
    default=None,
    help="Okta filter expression.",
)
def list_users(search, filter_):
    """List Okta users, following all pagination."""
    client = _client()

    try:
        users = lifecycle.list_users(
            client,
            search=search,
            filter_=filter_,
        )
    except Exception as exc:
        _handle_error(exc)
        return

    for user in users:
        profile = user.get("profile", {})

        click.echo(
            f"{user.get('id')} | "
            f"{user.get('status')} | "
            f"{profile.get('login')}"
        )

    click.echo(f"\nTotal: {len(users)}")


@cli.command("export")
@click.option(
    "--output",
    default="users.csv",
    show_default=True,
    help="Path to the output CSV file.",
)
def export_users(output):
    """Export all Okta users to a CSV file."""
    client = _client()

    try:
        export.export_users_to_csv(
            client,
            output,
        )
    except Exception as exc:
        _handle_error(exc)
        return

    click.echo(f"Exported users to {output}")


@cli.command("bulk-import")
@click.argument("filepath")
def bulk_import(filepath):
    """Bulk import users from a CSV file."""
    client = _client()

    try:
        summary = export.import_users_from_csv(
            client,
            filepath,
        )
    except Exception as exc:
        _handle_error(exc)
        return

    click.echo(f"Created: {summary['created']}")
    click.echo(f"Failed : {summary['failed']}")

    if summary["errors"]:
        click.echo("\nErrors:")

        for error in summary["errors"]:
            click.echo(f"- {error}")


def main():
    load_dotenv()
    cli()


if __name__ == "__main__":
    main()