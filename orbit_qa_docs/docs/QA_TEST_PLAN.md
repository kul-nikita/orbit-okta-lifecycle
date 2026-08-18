# QA Test Plan — Orbit Okta User Lifecycle Orchestrator

## 1. Purpose
This document defines the quality-assurance approach for Orbit, a Python CLI/library that automates Okta user lifecycle operations: create, activate, deactivate, list, and CSV export.

## 2. QA Objectives
- Verify that lifecycle operations behave as documented.
- Verify validation and error handling.
- Verify Okta client configuration and HTTP behavior.
- Verify CSV export correctness.
- Verify the CLI exposes the expected commands and options.
- Ensure automated tests remain repeatable and do not require a real Okta tenant.
- Record defects and regression results consistently.

## 3. Scope

### In Scope
- Okta client configuration and request handling.
- User creation.
- User activation and deactivation.
- User listing.
- CSV export.
- CLI command wiring.
- Error and invalid-input handling.
- Automated unit/integration tests.
- CI checks using pytest and Ruff.

### Out of Scope
- Testing a production Okta tenant without authorization.
- Performance/load testing of Okta.
- Testing real customer data.
- Infrastructure outside this repository.

## 4. Test Levels
| Level | Purpose | Expected Environment |
|---|---|---|
| Unit | Verify individual functions/modules | Local test environment |
| Integration | Verify interactions between Orbit modules | Local test environment with mocked HTTP |
| CLI | Verify command wiring and validation | Local CLI |
| CI | Verify tests and linting on changes | GitHub Actions |

## 5. Test Environment
- Python virtual environment.
- Dependencies from `requirements.txt`.
- Test configuration values supplied through test fixtures/environment variables.
- Mocked HTTP responses for tests that exercise Okta API behavior.
- No real API token should be committed to the repository.

## 6. Functional Areas

### User Lifecycle
- Create user with required profile fields.
- Create user with activation option.
- Handle group IDs when supported.
- Activate an existing user.
- Deactivate an existing user.
- List users.

### CSV Export
- Export users to a CSV file.
- Verify output file creation.
- Verify expected headers/fields.
- Verify multiple records are exported.
- Verify empty user lists are handled correctly.

### Okta Client
- Verify required configuration is read.
- Verify authorization headers are generated.
- Verify successful HTTP responses.
- Verify non-success responses are handled clearly.
- Verify retry/backoff behavior where implemented.

### CLI
- Verify help output.
- Verify lifecycle commands are exposed.
- Verify required arguments/options are validated.
- Verify command errors are reported without exposing secrets.

## 7. Security QA Checks
- Never commit `.env` or real Okta credentials.
- Confirm API tokens are not printed in normal error output.
- Use test/mock credentials only in automated tests.
- Confirm invalid or unauthorized requests are handled without leaking sensitive data.
- Review generated CSV files for accidental secrets before sharing them.

## 8. Entry Criteria
Testing can begin when:
- Required dependencies are installed.
- The code under test is available locally.
- Test configuration is prepared.
- The intended feature is implemented.

## 9. Exit Criteria
Testing is complete when:
- Automated tests have been executed.
- Relevant manual/CLI checks have been executed.
- Failures are recorded.
- Known defects are documented.
- A QA status is recorded without claiming unexecuted tests as passed.

## 10. Regression Testing
After changes to lifecycle, export, Okta client, or CLI code, rerun:

```bash
pytest -v
ruff check .
```

Also repeat the affected manual/CLI test cases.

## 11. QA Evidence
Keep evidence such as:
- Test command output.
- CI workflow result.
- Relevant screenshots.
- Defect IDs.
- CSV output samples containing only safe test data.

## 12. QA Status
The final QA status should be updated after the actual test execution. Do not mark tests as passed based only on code inspection.
