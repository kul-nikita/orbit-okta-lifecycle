# Orbit — Okta User Lifecycle Orchestrator

Orbit is a small Python CLI and library for automating common Okta user
lifecycle tasks: create, activate, deactivate, and export users.

The repo is intentionally split into small, parallel-ownable files so a
team of engineers can each pick up a module and build it out without
colliding.

## Repository layout

| Path | Owner | Responsibility |
| --- | --- | --- |
| `src/okta_client.py` | API client owner | Okta REST client: env config, auth headers, 429 retry/backoff, clear errors. Exports `OktaClient`. |
| `src/lifecycle.py` | Lifecycle owner | `create_user`, `activate_user`, `deactivate_user`, `list_users`. |
| `src/export.py` | Export owner | CSV export via `lifecycle.list_users`; CSV import stub. |
| `src/cli.py` | CLI owner | Click-based CLI wiring the lifecycle commands. |
| `tests/test_okta_client.py` | API client owner | pytest tests for `OktaClient`. |
| `tests/test_lifecycle.py` | Lifecycle owner | pytest tests for the lifecycle functions. |
| `tests/test_export.py` | Export owner | pytest tests for CSV import/export. |
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

## Running the CLI

```
python -m src.cli --help

python -m src.cli create --email ada@example.com --first-name Ada --last-name Lovelace
python -m src.cli activate 00u1abc123
python -m src.cli deactivate 00u1abc123
python -m src.cli export --output users.csv
```

Config is read from `.env` (or real environment variables):
`OKTA_DOMAIN` and `OKTA_API_TOKEN`.

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

Development

- Dev tools (tests, linters) were moved to `dev-requirements.txt` to keep the runtime image smaller:

```
python -m pip install -r dev-requirements.txt
```

CI

- GitHub Actions now builds the Docker image and runs a small smoke test to ensure Streamlit is available in the image. See `.github/workflows/ci.yml`.

Notes

- Pinning runtime dependency versions in `requirements.txt` improves reproducible builds.
- Never commit a `.env` file containing a real Okta API token.
