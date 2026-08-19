"""Orbit CSV export page."""

import csv
import io

import streamlit as st

from src.ui.components import (
    friendly_error,
    get_user_status,
    load_users,
    show_page_header,
)


def _build_csv(users):
    """Build a CSV string from Okta users."""

    output = io.StringIO()

    writer = csv.writer(output)

    writer.writerow(
        [
            "id",
            "firstName",
            "lastName",
            "email",
            "login",
            "status",
        ]
    )

    for user in users:

        profile = user.get("profile", {})

        writer.writerow(
            [
                user.get("id", ""),
                profile.get("firstName", ""),
                profile.get("lastName", ""),
                profile.get("email", ""),
                profile.get("login", ""),
                user.get("status", ""),
            ]
        )

    return output.getvalue()


def render_export():
    """Render the CSV export page."""

    show_page_header(
        "Operations",
        "Export Users",
        "Generate a CSV snapshot of the Okta directory.",
    )

    try:

        # ----------------------------------------------------
        # Load users
        # ----------------------------------------------------

        with st.spinner("Loading directory..."):
            users = load_users()

        # ----------------------------------------------------
        # Export card
        # ----------------------------------------------------

        with st.container(border=True):

            st.markdown("### User Directory Export")

            st.caption(
                "Export identity information from your Okta "
                "directory as a CSV file."
            )

            st.divider()

            # ------------------------------------------------
            # Statistics
            # ------------------------------------------------

            total = len(users)

            active = sum(
                get_user_status(user).upper() == "ACTIVE"
                for user in users
            )

            staged = sum(
                get_user_status(user).upper() == "STAGED"
                for user in users
            )

            deactivated = sum(
                get_user_status(user).upper()
                in {"DEPROVISIONED", "DEACTIVATED"}
                for user in users
            )

            c1, c2, c3, c4 = st.columns(4)

            with c1:
                st.metric(
                    "Users",
                    total,
                )

            with c2:
                st.metric(
                    "Active",
                    active,
                )

            with c3:
                st.metric(
                    "Staged",
                    staged,
                )

            with c4:
                st.metric(
                    "Deactivated",
                    deactivated,
                )

            st.divider()

            # ------------------------------------------------
            # Export filter
            # ------------------------------------------------

            st.markdown("### Export Options")

            st.caption(
                "Choose which identities should be included "
                "in the CSV export."
            )

            status_filter = st.selectbox(
                "Status",
                [
                    "All",
                    "ACTIVE",
                    "STAGED",
                    "DEPROVISIONED",
                    "DEACTIVATED",
                    "SUSPENDED",
                ],
                format_func=lambda value: (
                    "All statuses"
                    if value == "All"
                    else value.title()
                ),
                key="export_status_filter",
            )

            # ------------------------------------------------
            # Apply filter
            # ------------------------------------------------

            if status_filter == "All":

                export_users = users

            else:

                export_users = [
                    user
                    for user in users
                    if get_user_status(user).upper()
                    == status_filter
                ]

            st.caption(
                f"{len(export_users)} user(s) selected "
                "for export."
            )

            st.divider()

            # ------------------------------------------------
            # Generate CSV
            # ------------------------------------------------

            if st.button(
                "Generate CSV",
                type="primary",
                use_container_width=True,
                key="generate_csv",
            ):

                if not export_users:

                    st.warning(
                        "There are no users matching the "
                        "selected filter."
                    )

                else:

                    csv_data = _build_csv(export_users)

                    st.success(
                        f"CSV ready — "
                        f"{len(export_users)} user(s) included."
                    )

                    st.download_button(
                        "↓ Download users.csv",
                        data=csv_data,
                        file_name="users.csv",
                        mime="text/csv",
                        use_container_width=True,
                        key="download_users_csv",
                    )

        # ----------------------------------------------------
        # Export information
        # ----------------------------------------------------

        st.markdown("### Export Information")

        info1, info2, info3 = st.columns(3)

        with info1, st.container(border=True):

            st.markdown("### CSV")

            st.caption(
                "Portable comma-separated format "
                "compatible with spreadsheets and "
                "administration tools."
            )

        with info2, st.container(border=True):

            st.markdown("### Directory")

            st.caption(
                f"{len(users)} identities are currently "
                "available in the Okta directory."
            )

        with info3, st.container(border=True):

            st.markdown("### Secure")

            st.caption(
                "The export is generated from the "
                "currently loaded directory data."
            )

    except Exception as exc:

        st.error(
            "Unable to export users: "
            + friendly_error(exc)
        )