"""Orbit — Okta user lifecycle orchestration CLI.

Run from the repo root with:

    python -m src.cli --help
"""

from __future__ import annotations

import click
from dotenv import load_dotenv

from . import export, multi
from .okta_client import OktaClientError, get_clients


def _handle_error(exc):
    """Turn known application errors into useful CLI errors."""
    from . import lifecycle

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


def _print_result(label, result):
    """Print a multi-tenant lifecycle result."""
    if isinstance(result, dict) and "error" in result:
        click.echo(f"  [{label}] Error: {result['error']}")
    else:
        status = result.get("status", "unknown") if isinstance(result, dict) else str(result)
        user = result.get("user", {}) if isinstance(result, dict) else {}
        user_id = user.get("id") if isinstance(user, dict) else None
        if user_id:
            click.echo(f"  [{label}] Status: {status}  User: {user_id}")
        else:
            click.echo(f"  [{label}] Status: {status}")


@click.group()
def cli():
    """Orbit commands for managing Okta user lifecycle across multiple tenants."""


@cli.command()
@click.option("--email", required=True, help="Login email for the new user.")
@click.option("--first-name", required=True, help="User's first name.")
@click.option("--last-name", required=True, help="User's last name.")
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
def create(email, first_name, last_name, activate, send_email):
    """Create a user, or reconcile an existing login on all tenants."""
    clients = get_clients()
    if not clients:
        click.echo("Error: no Okta tenants configured. Check your .env file.", err=True)
        return

    profile = {
        "email": email,
        "login": email,
        "firstName": first_name,
        "lastName": last_name,
    }

    results = multi.create_user(clients, profile, activate=activate, send_email=send_email)

    for label, result in results.items():
        _print_result(label, result)

    if activate:
        click.echo(
            "Activation workflow requested. "
            "Check the user's Okta status before assuming "
            "the asynchronous transition has completed."
        )


@cli.command()
@click.argument("user_id")
def get(user_id):
    """Get the current Okta state of a user on all tenants."""
    clients = get_clients()
    if not clients:
        click.echo("Error: no Okta tenants configured. Check your .env file.", err=True)
        return

    results = multi.get_user(clients, user_id)

    for label, result in results.items():
        _print_result(label, result)


@cli.command()
@click.argument("user_id")
@click.option(
    "--send-email/--no-send-email",
    default=True,
    show_default=True,
)
def activate(user_id, send_email):
    """Activate a STAGED or DEPROVISIONED user on all tenants."""
    clients = get_clients()
    if not clients:
        click.echo("Error: no Okta tenants configured. Check your .env file.", err=True)
        return

    results = multi.activate_user(clients, user_id, send_email=send_email)

    for label, result in results.items():
        _print_result(label, result)


@cli.command()
@click.argument("user_id")
@click.option(
    "--send-email/--no-send-email",
    default=True,
    show_default=True,
)
def reactivate(user_id, send_email):
    """Restart activation for a PROVISIONED or RECOVERY user on all tenants."""
    clients = get_clients()
    if not clients:
        click.echo("Error: no Okta tenants configured. Check your .env file.", err=True)
        return

    results = multi.reactivate_user(clients, user_id, send_email=send_email)

    for label, result in results.items():
        _print_result(label, result)


@cli.command()
@click.argument("user_id")
@click.option(
    "--send-email/--no-send-email",
    default=False,
    show_default=True,
)
def deactivate(user_id, send_email):
    """Deactivate any user that is not already DEPROVISIONED on all tenants."""
    clients = get_clients()
    if not clients:
        click.echo("Error: no Okta tenants configured. Check your .env file.", err=True)
        return

    results = multi.deactivate_user(clients, user_id, send_email=send_email)

    for label, result in results.items():
        _print_result(label, result)


@cli.command()
@click.argument("user_id")
def suspend(user_id):
    """Suspend an ACTIVE user on all tenants."""
    clients = get_clients()
    if not clients:
        click.echo("Error: no Okta tenants configured. Check your .env file.", err=True)
        return

    results = multi.suspend_user(clients, user_id)

    for label, result in results.items():
        _print_result(label, result)


@cli.command()
@click.argument("user_id")
def unsuspend(user_id):
    """Unsuspend a SUSPENDED user on all tenants."""
    clients = get_clients()
    if not clients:
        click.echo("Error: no Okta tenants configured. Check your .env file.", err=True)
        return

    results = multi.unsuspend_user(clients, user_id)

    for label, result in results.items():
        _print_result(label, result)


@cli.command()
@click.argument("user_id")
def unlock(user_id):
    """Unlock a LOCKED_OUT user on all tenants."""
    clients = get_clients()
    if not clients:
        click.echo("Error: no Okta tenants configured. Check your .env file.", err=True)
        return

    results = multi.unlock_user(clients, user_id)

    for label, result in results.items():
        _print_result(label, result)


@cli.command("ensure-active")
@click.argument("user_id")
@click.option(
    "--send-email/--no-send-email",
    default=True,
    show_default=True,
)
def ensure_active(user_id, send_email):
    """Move an existing user toward ACTIVE on all tenants."""
    clients = get_clients()
    if not clients:
        click.echo("Error: no Okta tenants configured. Check your .env file.", err=True)
        return

    results = multi.ensure_user_active(clients, user_id, send_email=send_email)

    for label, result in results.items():
        _print_result(label, result)


@cli.command()
@click.argument("user_id")
@click.confirmation_option(
    prompt="Are you sure you want to permanently delete this user?"
)
def delete(user_id):
    """Permanently delete a DEPROVISIONED user on all tenants."""
    clients = get_clients()
    if not clients:
        click.echo("Error: no Okta tenants configured. Check your .env file.", err=True)
        return

    results = multi.delete_user(clients, user_id)

    for label, result in results.items():
        _print_result(label, result)


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
    """List Okta users from all tenants, following all pagination."""
    clients = get_clients()
    if not clients:
        click.echo("Error: no Okta tenants configured. Check your .env file.", err=True)
        return

    all_users = multi.list_users(clients, search=search, filter_=filter_)

    for user in all_users:
        profile = user.get("profile", {})
        tenant = user.get("_tenant", "unknown")

        click.echo(
            f"[{tenant}] {user.get('id')} | "
            f"{user.get('status')} | "
            f"{profile.get('login')}"
        )

    click.echo(f"\nTotal: {len(all_users)}")


@cli.command("export")
@click.option(
    "--output",
    default="users.csv",
    show_default=True,
    help="Path to the output CSV file.",
)
def export_users(output):
    """Export all Okta users from all tenants to a CSV file."""
    clients = get_clients()
    if not clients:
        click.echo("Error: no Okta tenants configured. Check your .env file.", err=True)
        return

    all_users = multi.list_users(clients)
    click.echo(f"  Loaded {len(all_users)} user(s) from {len(clients)} tenant(s)")

    export.export_users_to_csv_from_list(all_users, output)
    click.echo(f"  Exported users to {output}")


@cli.command("bulk-import")
@click.argument("filepath")
def bulk_import(filepath):
    """Bulk import users from a CSV file to all configured tenants."""
    clients = get_clients()
    if not clients:
        click.echo("Error: no Okta tenants configured. Check your .env file.", err=True)
        return

    for client in clients:
        click.echo(f"\n--- Importing to [{client.label}] ({client.domain}) ---")
        summary = export.import_users_from_csv(client, filepath)

        click.echo(f"  Created: {summary['created']}")
        click.echo(f"  Failed : {summary['failed']}")

        if summary["errors"]:
            click.echo("\n  Errors:")
            for error in summary["errors"]:
                click.echo(f"  - {error}")


def main():
    load_dotenv()
    cli()


if __name__ == "__main__":
    main()
