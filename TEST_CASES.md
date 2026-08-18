# Test Cases — Orbit Okta Lifecycle

## 1. Test Environment

| Item | Value |
|---|---|
| Operating System | Windows |
| Python | 3.14.4 |
| pytest | 9.1.1 |
| Execution Command | `python -m pytest -v` |
| Test Result | 25 passed |
| Execution Time | 3.95 seconds |

## 2. Automated Test Cases

### CSV Export

| ID | Test Case | Expected Result | Actual Result | Status |
|---|---|---|---|---|
| TC-001 | Export users to CSV | User records are written as CSV rows | Rows were written successfully | PASS |

### User Creation

| ID | Test Case | Expected Result | Actual Result | Status |
|---|---|---|---|---|
| TC-002 | Create user with valid profile | Profile is posted and user is returned | Test passed | PASS |
| TC-003 | Create user with activation enabled | Activation query parameter is set correctly | Test passed | PASS |
| TC-004 | Create user with group IDs | Group IDs are included in the request | Test passed | PASS |
| TC-005 | Create duplicate user | Duplicate user is detected and expected error is raised | Test passed | PASS |
| TC-006 | Create user with invalid profile | Validation error is raised | Test passed | PASS |

### User Activation

| ID | Test Case | Expected Result | Actual Result | Status |
|---|---|---|---|---|
| TC-007 | Activate user and read response | Activation response JSON is returned | Test passed | PASS |
| TC-008 | Activate user with email notification | Email query parameter is set correctly | Test passed | PASS |
| TC-009 | Activate already-active user | Operation is handled as no-op | Test passed | PASS |
| TC-010 | Handle already-active 403 response | Known already-active condition is handled as no-op | Test passed | PASS |
| TC-011 | Handle other activation error | Unexpected error is propagated | Test passed | PASS |
| TC-012 | Verify activation response JSON | JSON response is handled correctly | Test passed | PASS |

### User Deactivation

| ID | Test Case | Expected Result | Actual Result | Status |
|---|---|---|---|---|
| TC-013 | Deactivate already-deactivated user | Operation is handled as no-op | Test passed | PASS |
| TC-014 | Deactivate user with email notification | Email query parameter is set correctly | Test passed | PASS |

### User Listing

| ID | Test Case | Expected Result | Actual Result | Status |
|---|---|---|---|---|
| TC-015 | List users with page shorter than limit | Pagination stops correctly | Test passed | PASS |
| TC-016 | List users using pagination cursor | Next page follows returned cursor | Test passed | PASS |
| TC-017 | List users with search/filter parameters | Parameters are passed correctly | Test passed | PASS |

### Okta Client

| ID | Test Case | Expected Result | Actual Result | Status |
|---|---|---|---|---|
| TC-018 | GET request authentication | Authentication header is included and response is returned | Test passed | PASS |
| TC-019 | Retry HTTP 429 | Client retries the request according to retry behavior | Test passed | PASS |
| TC-020 | Handle HTTP error | Expected HTTP exception is raised | Test passed | PASS |
| TC-021 | Missing configuration | Configuration error is raised | Test passed | PASS |
| TC-022 | DELETE request authentication | Authentication header is included and response is returned | Test passed | PASS |
| TC-023 | Stop retries after maximum attempts | Retry limit is respected | Test passed | PASS |
| TC-024 | Exponential backoff | Backoff delays increase as configured | Test passed | PASS |
| TC-025 | Retry-After header | Retry timing uses the response header when applicable | Test passed | PASS |

## 3. Test Execution Summary

| Category | Tests | Passed | Failed |
|---|---:|---:|---:|
| CSV Export | 1 | 1 | 0 |
| User Creation | 5 | 5 | 0 |
| User Activation | 6 | 6 | 0 |
| User Deactivation | 2 | 2 | 0 |
| User Listing | 3 | 3 | 0 |
| Okta Client | 8 | 8 | 0 |
| **Total** | **25** | **25** | **0** |

## 4. Defect Status

No defects were identified by the automated test suite during this execution.

If a defect is discovered during future testing, record it using `BUG_REPORT_TEMPLATE.md`.

## 5. QA Evidence

The automated execution was performed using:

```bash
python -m pytest -v
```

Result:

```text
25 passed in 3.95s
```

## 6. Additional Manual Testing

The following should be performed separately when an authorized test Okta environment is available:

- Verify actual user creation through the configured Okta environment.
- Verify actual activation and deactivation.
- Verify actual user listing and pagination.
- Verify actual CSV output with safe test users.
- Verify behavior with an invalid or expired test token.
- Verify rate-limit behavior without affecting production systems.

Manual results should be added to this document after execution.
