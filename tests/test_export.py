"""Tests for CSV import/export helpers."""

import csv
from unittest import mock

from src import export, lifecycle


def test_export_users_to_csv_writes_rows(tmp_path):
    fake_users = [
        {
            "id": "00u1",
            "status": "ACTIVE",
            "profile": {
                "email": "alice@example.com",
                "login": "alice@example.com",
                "firstName": "Alice",
                "lastName": "A.",
            },
        },
        {
            "id": "00u2",
            "status": "SUSPENDED",
            "profile": {
                "email": "bob@example.com",
                "login": "bob@example.com",
                "firstName": "Bob",
                "lastName": "B.",
            },
        },
    ]
    output = tmp_path / "users.csv"

    with mock.patch.object(lifecycle, "list_users", return_value=fake_users) as mocked:
        export.export_users_to_csv(mock.Mock(), str(output))

    mocked.assert_called_once()
    rows = list(csv.DictReader(output.open(encoding="utf-8")))
    assert len(rows) == 2
    assert rows[0]["email"] == "alice@example.com"
    assert rows[1]["status"] == "SUSPENDED"


# TODO(owner): add tests for import_users_from_csv and for malformed /
# missing-profile user data.
