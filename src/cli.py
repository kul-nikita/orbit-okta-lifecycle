"""Orbit — Okta user lifecycle orchestration CLI.

Run from the repo root with: python -m src.cli --help
"""

import click
from dotenv import load_dotenv

from . import export, lifecycle
from .okta_client import OktaClient


@click.group()
def cli():
    """Orbit commands for managing Okta user lifecycle."""


@cli.command()
@click.option("--email", required=True, help="Login email for the new user.")
@click.option("--first-name", required=True, help="User's first name.")
@click.option("--last-name", required=True, help="User's last name.")
def create(email, first_name, last_name):
    """Create and activate a new Okta user."""
    client = OktaClient()
    profile = {
        "email": email,
        "login": email,
        "firstName": first_name,
        "lastName": last_name,
    }
    user = lifecycle.create_user(client, profile)
    click.echo(f"Created user {user['id']}")


@cli.command()
@click.argument("user_id")
def activate(user_id):
    """Activate a user by id."""
    client = OktaClient()
    lifecycle.activate_user(client, user_id)
    click.echo(f"Activated user {user_id}")


@cli.command()
@click.argument("user_id")
def deactivate(user_id):
    """Deactivate a user by id."""
    client = OktaClient()
    lifecycle.deactivate_user(client, user_id)
    click.echo(f"Deactivated user {user_id}")


@cli.command("export")
@click.option("--output", default="users.csv", help="Path to the output CSV file.")
def export_users(output):
    """Export all Okta users to a CSV file."""
    client = OktaClient()
    export.export_users_to_csv(client, output)
    click.echo(f"Exported users to {output}")


# -------------------------
# Your contribution starts here
# -------------------------

@cli.command("bulk-import")
@click.argument("filepath")
def bulk_import(filepath):
    """Bulk import users from a CSV file."""
    client = OktaClient()
    summary = export.import_users_from_csv(client, filepath)

    click.echo(f"Created: {summary['created']}")
    click.echo(f"Failed : {summary['failed']}")

    if summary["errors"]:
        click.echo("\nErrors:")
        for error in summary["errors"]:
            click.echo(f"- {error}")

# -------------------------
# Your contribution ends here
# -------------------------


def main():
    load_dotenv()
    cli()


if __name__ == "__main__":
    main()