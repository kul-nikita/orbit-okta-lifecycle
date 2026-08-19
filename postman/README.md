# Postman Collection

This directory holds the Postman assets for manually testing the
Okta lifecycle endpoints that Orbit wraps.

## Files

- **`collection.json`** — A Postman collection with requests for each
  lifecycle operation: List Users, Create User, Activate User,
  Deactivate User, and Delete User. Each request targets the Okta
  REST API (`/api/v1/users/...`) and uses the environment's
  `okta_domain` variable to build the full URL.

- **`environment.json`** — A Postman environment defining two
  variables:
  - `okta_domain` — Your Okta org domain (e.g. `example.okta.com`)
  - `user_id` — Placeholder for the user ID to operate on

## How to import

1. Open Postman.
2. Click **Import** (top-left).
3. Drag and drop `collection.json` — this imports the request collection.
4. Drag and drop `environment.json` — this imports the environment.
5. Select the "User Lifecycle Orchestrator" environment from the
   environment dropdown (top-right).
6. Fill in `okta_domain` with your actual Okta org domain.
7. Set your API token in the collection's authorization settings
   (Header: `Authorization: SSWS <your-token>`).

## Guidelines

- Never commit real tokens or org-specific values.
- Keep the collection in sync with any endpoint changes in `src/`.
