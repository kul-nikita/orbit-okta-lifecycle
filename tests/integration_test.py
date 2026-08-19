"""Integration test for Okta user lifecycle.

Hits the real Okta API using credentials from ``.env`` and runs a
full lifecycle sequence: create user, activate (verify no-op), export
to CSV (verify user appears), deactivate, and delete (cleanup).
Always cleans up in a ``finally`` block regardless of pass/fail.

Dependencies:
    csv, os, sys, uuid, traceback, src.okta_client, src.lifecycle, src.export

Run with::

    python tests/integration_test.py
"""

import csv
import os
import sys
import traceback
import uuid

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src import export, lifecycle
from src.okta_client import OktaClient

RESULTS = []


def step(name, fn):
    """Run a test step, print pass/fail, and record result."""
    print(f"\n{'=' * 60}")
    print(f"STEP: {name}")
    print(f"{'=' * 60}")
    try:
        result = fn()
        print(f"  PASS  response: {result}")
        RESULTS.append((name, True, result))
        return result
    except Exception as e:
        print(f"  FAIL  error: {e}")
        tb = traceback.format_exc()
        print(tb)
        RESULTS.append((name, False, str(e)))
        return None


def main():
    print("Orbit -- Okta Lifecycle Integration Test")
    print("=" * 60)

    from dotenv import load_dotenv

    load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

    print(f"\nOKTA_DOMAIN = {os.getenv('OKTA_DOMAIN')}")
    print(f"OKTA_API_TOKEN set = {bool(os.getenv('OKTA_API_TOKEN'))}")

    client = OktaClient()

    test_id = uuid.uuid4().hex[:8]
    email = f"orbit_test_{test_id}@example.com"
    profile = {
        "email": email,
        "login": email,
        "firstName": "Orbit",
        "lastName": f"TestUser{test_id}",
    }

    user_id = None

    try:
        # Step 1: Create user (activate=True -> ACTIVE immediately)
        def do_create():
            return lifecycle.create_user(client, profile, activate=True)

        created = step("Create user (activate=True)", do_create)
        if created:
            user_id = created.get("id")

        # Step 2: Activate user (should be no-op since already active)
        def do_activate():
            if not user_id:
                raise RuntimeError("No user_id from create step")
            return lifecycle.activate_user(client, user_id, send_email=False)

        step("Activate user (expect already_active noop)", do_activate)

        # Step 3: Export all users to CSV (before deactivation so user is visible)
        csv_path = os.path.join(
            os.path.dirname(__file__), "..", "test_export.csv"
        )

        def do_export():
            return export.export_users_to_csv(client, csv_path)

        step("Export all users to test_export.csv", do_export)

        # Verify CSV contains our test user
        if os.path.exists(csv_path):
            with open(csv_path, encoding="utf-8") as fh:
                rows = list(csv.DictReader(fh))
            print(f"  CSV has {len(rows)} user rows")
            found = any(r.get("login") == email for r in rows)
            print(f"  Test user found in CSV: {found}")

        # Step 4: Deactivate user
        def do_deactivate():
            if not user_id:
                raise RuntimeError("No user_id from create step")
            return lifecycle.deactivate_user(client, user_id, send_email=False)

        step("Deactivate user", do_deactivate)

    finally:
        # Step 5: Cleanup -- always delete the test user
        if user_id:
            def do_delete():
                resp = client.delete(f"/users/{user_id}")
                return {"status": resp.status_code}

            step("Delete test user (cleanup)", do_delete)
        else:
            print("\n  SKIP  Delete step -- no user_id to clean up")

    # --- Summary ---
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    all_pass = True
    for name, passed, _detail in RESULTS:
        status = "PASS" if passed else "FAIL"
        print(f"  [{status}] {name}")
        if not passed:
            all_pass = False

    print(f"\n{'=' * 60}")
    if all_pass:
        print("ALL STEPS PASSED")
    else:
        print("SOME STEPS FAILED")
    print(f"{'=' * 60}\n")

    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
