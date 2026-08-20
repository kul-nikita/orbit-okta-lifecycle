# Orbit — Okta User Lifecycle Orchestrator

Orbit is a Python CLI and Streamlit web UI for automating Okta user lifecycle
management across **multiple tenants simultaneously**: create, activate,
deactivate, and export users from one or two Okta orgs in a single operation.

The repo is intentionally split into small, parallel-ownable files so a
team of engineers can each pick up a module and build it out without
colliding.

## Repository layout

| Path | Owner | Responsibility |
| --- | --- | --- |
| `src/okta_client.py` | API client owner | Okta REST client: env config, SSWS auth, 429 retry/backoff, `get_clients()` for multi-tenant. |
| `src/lifecycle.py` | Lifecycle owner | Single-tenant `create_user`, `activate_user`, `deactivate_user`, `list_users`. |
| `src/multi.py` | Multi-tenant owner | Multi-tenant wrappers that run lifecycle ops against all tenants. |
| `src/export.py` | Export owner | CSV export/import with tenant tagging. |
| `src/cli.py` | CLI owner | Click-based CLI — every command runs across all tenants. |
| `src/app.py` | UI owner | Streamlit dashboard with tenant-aware user directory. |
| `src/ui/` | UI owner | Streamlit pages: dashboard, users, create, lifecycle, export. |
| `tests/` | All | pytest unit tests + integration test. |
| `postman/` | Postman owner | Postman `collection.json` + `environment.json`. |

## Setup

1. Create and activate a virtual environment:

   ```
   python -m venv .venv
   .venv\Scripts\activate        # Windows
   source .venv/bin/activate     # macOS / Linux
   ```

2. Install dependencies:

   ```
   pip install -r requirements.txt
   ```

3. Create your config file from the example and fill in your Okta values:

   ```
   cp .env.example .env
   ```

4. Configure your tenants in `.env`:

   ```
   # Tenant 1 — primary Okta org
   OKTA_DOMAIN_1=your-org-1.okta.com
   OKTA_API_TOKEN_1=your-api-token-1

   # Tenant 2 — secondary Okta org (optional, leave blank to use one tenant)
   OKTA_DOMAIN_2=your-org-2.okta.com
   OKTA_API_TOKEN_2=your-api-token-2
   ```

   All CLI commands and the Streamlit UI will automatically run against
   every configured tenant. Leave Tenant 2 blank for single-tenant mode.

## Running the CLI

```
python -m src.cli --help
```

### Quick reference — all commands

```bash
# User lifecycle
python -m src.cli create --email USER --first-name FIRST --last-name LAST
python -m src.cli get USER_ID
python -m src.cli list
python -m src.cli activate USER_ID
python -m src.cli reactivate USER_ID
python -m src.cli deactivate USER_ID
python -m src.cli suspend USER_ID
python -m src.cli unsuspend USER_ID
python -m src.cli unlock USER_ID
python -m src.cli ensure-active USER_ID
python -m src.cli delete USER_ID
<<<<<<< Updated upstream
.venv\Scripts\python.exe -m streamlit run src/app.py

# Import / export
python -m src.cli export --output users.csv
python -m src.cli bulk-import new_users.csv
```

### Detailed command reference

#### `create`

Creates a user on all configured tenants.

```
python -m src.cli create --email ada@example.com --first-name Ada --last-name Lovelace
```

Options (all default to `True`):

| Flag | Default | Effect |
| --- | --- | --- |
| `--activate / --no-activate` | `True` | Activate the user immediately. |
| `--send-email / --no-send-email` | `True` | Send Okta's activation email to the user. |

**Default flow** (`--activate --send-email`): the user is created, activated,
and receives an activation email. They click the link, set their password,
and can log in. No further CLI steps are needed.

**Staged flow** (`--no-activate`): the user is created in `STAGED` status.
Run `activate` separately when ready.

#### `get`

Shows the current Okta state of a user on all tenants.

```
python -m src.cli get 00u1abc123
```

#### `list`

Lists all users across all tenants. Supports optional Okta search/filter.

```
python -m src.cli list
python -m src.cli list --search 'status eq "ACTIVE"'
```

#### `activate`

Activates a `STAGED` or `DEPROVISIONED` user. Sends an activation email
by default.

```
python -m src.cli activate 00u1abc123
python -m src.cli activate 00u1abc123 --no-send-email
```

#### `reactivate`

Re-sends the activation email to a `PROVISIONED` or `RECOVERY` user.

```
python -m src.cli reactivate 00u1abc123
```

#### `deactivate`

Deactivates a user (moves them to `DEPROVISIONED`). Does **not** send
an email by default.

```
python -m src.cli deactivate 00u1abc123
python -m src.cli deactivate 00u1abc123 --send-email
```

#### `suspend` / `unsuspend`

Suspends an `ACTIVE` user or unsuspends a `SUSPENDED` user.

```
python -m src.cli suspend 00u1abc123
python -m src.cli unsuspend 00u1abc123
```

#### `unlock`

Unlocks a `LOCKED_OUT` user.

```
python -m src.cli unlock 00u1abc123
```

#### `ensure-active`

Automatically moves a user toward `ACTIVE` regardless of their current
status — activates, unsuspends, or unlocks as needed.

```
python -m src.cli ensure-active 00u1abc123
```

#### `delete`

Permanently deletes a `DEPROVISIONED` user (asks for confirmation).

```
python -m src.cli delete 00u1abc123
```

#### `export`

Exports all users from all tenants to a CSV file.

```
python -m src.cli export --output users.csv
```

#### `bulk-import`

Creates users from a CSV file on all tenants.

```
=======

streamlit run src/app.py
.venv\Scripts\python.exe -m streamlit run src/app.py


# Import / export
python -m src.cli export --output users.csv
>>>>>>> Stashed changes
python -m src.cli bulk-import new_users.csv
```

### Detailed command reference

#### `create`

Creates a user on all configured tenants.

```
python -m src.cli create --email ada@example.com --first-name Ada --last-name Lovelace
```

Options (all default to `True`):

| Flag | Default | Effect |
| --- | --- | --- |
| `--activate / --no-activate` | `True` | Activate the user immediately. |
| `--send-email / --no-send-email` | `True` | Send Okta's activation email to the user. |

**Default flow** (`--activate --send-email`): the user is created, activated,
and receives an activation email. They click the link, set their password,
and can log in. No further CLI steps are needed.

**Staged flow** (`--no-activate`): the user is created in `STAGED` status.
Run `activate` separately when ready.

#### `get`

Shows the current Okta state of a user on all tenants.

```
python -m src.cli get 00u1abc123
```

#### `list`

Lists all users across all tenants. Supports optional Okta search/filter.

```
python -m src.cli list
python -m src.cli list --search 'status eq "ACTIVE"'
```

#### `activate`

Activates a `STAGED` or `DEPROVISIONED` user. Sends an activation email
by default.

```
python -m src.cli activate 00u1abc123
python -m src.cli activate 00u1abc123 --no-send-email
```

#### `reactivate`

Re-sends the activation email to a `PROVISIONED` or `RECOVERY` user.

```
python -m src.cli reactivate 00u1abc123
```

#### `deactivate`

Deactivates a user (moves them to `DEPROVISIONED`). Does **not** send
an email by default.

```
python -m src.cli deactivate 00u1abc123
python -m src.cli deactivate 00u1abc123 --send-email
```

#### `suspend` / `unsuspend`

Suspends an `ACTIVE` user or unsuspends a `SUSPENDED` user.

```
python -m src.cli suspend 00u1abc123
python -m src.cli unsuspend 00u1abc123
```

#### `unlock`

Unlocks a `LOCKED_OUT` user.

```
python -m src.cli unlock 00u1abc123
```

#### `ensure-active`

Automatically moves a user toward `ACTIVE` regardless of their current
status — activates, unsuspends, or unlocks as needed.

```
python -m src.cli ensure-active 00u1abc123
```

#### `delete`

Permanently deletes a `DEPROVISIONED` user (asks for confirmation).

```
python -m src.cli delete 00u1abc123
```

#### `export`

Exports all users from all tenants to a CSV file.

```
python -m src.cli export --output users.csv
```

#### `bulk-import`

Creates users from a CSV file on all tenants.

```
python -m src.cli bulk-import new_users.csv
```

## Running the Streamlit UI

```
.venv\Scripts\python.exe -m streamlit run src/app.py
```

The dashboard shows all users from all configured tenants with a
**Tenant** column in the directory table.

## Running tests

```
pytest -v
```

## Linting

```
ruff check .
```

## CI

On every push / pull request, GitHub Actions runs `ruff check .` and
`pytest -v` (see `.github/workflows/ci.yml`).

## Docker

The default container runs the Streamlit web interface on port 8501.

```
cp .env.example .env
# Edit .env with your tenant credentials
docker compose up --build
```

Open `http://localhost:8501` in your browser. Stop the app with `Ctrl+C`.

To run it without Docker Compose:

```
docker build -t orbit .
docker run --rm -p 8501:8501 --env-file .env orbit
```

The same image can also run the command-line interface by overriding its
default command:

```
docker run --rm --env-file .env orbit python -m src.cli --help
```

## Development

- Dev tools (tests, linters) were moved to `dev-requirements.txt` to keep the runtime image smaller:

```
python -m pip install -r dev-requirements.txt
```

## CI

- GitHub Actions now builds the Docker image and runs a small smoke test to ensure Streamlit is available in the image. See `.github/workflows/ci.yml`.

## Notes

- Pinning runtime dependency versions in `requirements.txt` improves reproducible builds.
- Never commit a `.env` file containing real Okta API tokens.
