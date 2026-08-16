# Postman Collection

This directory holds the Postman assets for the Okta Lifecycle
Orchestrator's REST interactions.

## Files to be added by the Postman owner
- `collection.json` — a Postman collection exercising the same Okta
  lifecycle endpoints wrapped by `/src` (create, activate, deactivate,
  list/export users).
- `environment.json` — a Postman environment defining variables such as
  `baseUrl` and `apiToken`, mirroring the values in `.env.example`.

## Guidelines
- Never commit real tokens or org-specific values.
- Keep the collection in sync with any endpoint changes in `/src`.
