"""Orbit lifecycle management page."""

import streamlit as st

from src import lifecycle

from src.ui.components import (
    friendly_error,
    get_client,
    get_user_email,
    get_user_name,
    get_user_status,
    load_users,
    show_page_header,
    status_badge,
)


def render_lifecycle():
    """Render the lifecycle management screen."""

    show_page_header(
        "Lifecycle",
        "User Lifecycle",
        "Find an identity and manage its Okta lifecycle state.",
    )

    try:

        # ----------------------------------------------------
        # Load users
        # ----------------------------------------------------

        with st.spinner("Loading identities..."):
            users = load_users()

        # ----------------------------------------------------
        # Search
        # ----------------------------------------------------

        st.markdown("### Find an identity")

        st.caption(
            "Search by name, email address or Okta user ID."
        )

        search = st.text_input(
            "Search users",
            placeholder="Search users...",
            label_visibility="collapsed",
            key="lifecycle_search",
        )

        query = search.lower().strip()

        matches = [
            user
            for user in users
            if (
                not query
                or query in get_user_name(user).lower()
                or query in get_user_email(user).lower()
                or query in user.get("id", "").lower()
            )
        ]

        if not matches:
            st.info("No matching users found.")
            return

        # ----------------------------------------------------
        # User selection
        # ----------------------------------------------------

        options = {
            (
                f"{get_user_name(user)}"
                f" — "
                f"{get_user_email(user)}"
            ): user
            for user in matches[:100]
        }

        selected_label = st.selectbox(
            "Select user",
            list(options.keys()),
            key="lifecycle_user",
        )

        selected = options[selected_label]

        status = get_user_status(selected).upper()

        # ----------------------------------------------------
        # User profile
        # ----------------------------------------------------

        with st.container(border=True):

            st.markdown("### User Profile")

            profile_col1, profile_col2, profile_col3 = (
                st.columns(3)
            )

            # ------------------------------------------------
            # Name and email
            # ------------------------------------------------

            with profile_col1:

                st.caption("NAME")

                st.markdown(
                    f'<div class="user-name">'
                    f'{get_user_name(selected)}'
                    f'</div>',
                    unsafe_allow_html=True,
                )

                st.caption("EMAIL")

                st.markdown(
                    f'<div class="user-email">'
                    f'{get_user_email(selected)}'
                    f'</div>',
                    unsafe_allow_html=True,
                )

            # ------------------------------------------------
            # Status and Okta ID
            # ------------------------------------------------

            with profile_col2:

                st.caption("CURRENT STATUS")

                st.markdown(
                    status_badge(status),
                    unsafe_allow_html=True,
                )

                st.caption("OKTA USER ID")

                st.markdown(
                    f'<div class="user-id">'
                    f'{selected.get("id", "—")}'
                    f'</div>',
                    unsafe_allow_html=True,
                )

            # ------------------------------------------------
            # Lifecycle state
            # ------------------------------------------------

            with profile_col3:

                st.caption("LIFECYCLE STATE")

                st.markdown(
                    f'<div class="user-name">'
                    f'{status.title()}'
                    f'</div>',
                    unsafe_allow_html=True,
                )

        # ----------------------------------------------------
        # Lifecycle action
        # ----------------------------------------------------

        st.markdown("### Lifecycle Action")

        with st.container(border=True):

            # =================================================
            # ACTIVE
            # =================================================

            if status == "ACTIVE":

                st.markdown("### ● User is active")

                st.write(
                    "This identity is currently active."
                )

                st.caption(
                    "Deactivating a user is a destructive "
                    "lifecycle operation."
                )

                if st.button(
                    "Deactivate User",
                    key="lifecycle_deactivate",
                    use_container_width=True,
                ):

                    st.session_state.selected_user = selected

                    st.session_state.confirm_deactivate = True

                    st.session_state.page = "User Details"

                    st.rerun()

            # =================================================
            # STAGED
            # =================================================

            elif status == "STAGED":

                st.markdown("### ● User is staged")

                st.write(
                    "This identity has been created and "
                    "is ready for activation."
                )

                send_email = st.checkbox(
                    "Send activation email",
                    value=True,
                    key="lifecycle_send_email",
                    help="Send an activation email to the user.",
                )

                if st.button(
                    "Activate User",
                    type="primary",
                    key="lifecycle_activate",
                    use_container_width=True,
                ):

                    try:

                        with st.spinner(
                            "Activating user..."
                        ):

                            result = lifecycle.activate_user(
                                get_client(),
                                selected["id"],
                                send_email=send_email,
                            )

                        if result.get(
                            "status"
                        ) == "already_active":

                            st.info(
                                "User is already active."
                            )

                        else:

                            st.success(
                                "User activation completed successfully."
                            )

                        st.rerun()

                    except Exception as exc:

                        st.error(
                            friendly_error(exc)
                        )

            # =================================================
            # PROVISIONED
            # =================================================

            elif status == "PROVISIONED":

                st.markdown("### ● User is provisioned")

                st.write(
                    "This identity has been provisioned "
                    "and is awaiting completion of activation."
                )

                st.info(
                    "No lifecycle action is currently "
                    "required for a provisioned user."
                )

            # =================================================
            # DEPROVISIONED / DEACTIVATED
            # =================================================

            elif status in {
                "DEPROVISIONED",
                "DEACTIVATED",
            }:

                st.markdown(
                    "### ● User is deactivated"
                )

                st.write(
                    "This identity is currently deactivated "
                    "and can be activated again."
                )

                send_email = st.checkbox(
                    "Send activation email",
                    value=True,
                    key="lifecycle_send_email",
                    help="Send an activation email to the user.",
                )

                if st.button(
                    "Activate User",
                    type="primary",
                    key="lifecycle_activate",
                    use_container_width=True,
                ):

                    try:

                        with st.spinner(
                            "Activating user..."
                        ):

                            lifecycle.activate_user(
                                get_client(),
                                selected["id"],
                                send_email=send_email,
                            )

                        st.success(
                            "User activation completed successfully."
                        )

                        st.rerun()

                    except Exception as exc:

                        st.error(
                            friendly_error(exc)
                        )

            # =================================================
            # SUSPENDED
            # =================================================

            elif status == "SUSPENDED":

                st.markdown(
                    "### ● User is suspended"
                )

                st.info(
                    "Lifecycle activation is not available "
                    "for suspended users."
                )

            # =================================================
            # UNKNOWN / OTHER STATUS
            # =================================================

            else:

                st.info(
                    f"Lifecycle action is not available "
                    f"for status: {status}"
                )

        # ----------------------------------------------------
        # Back button
        # ----------------------------------------------------

        if st.button(
            "← Back to Users",
            key="lifecycle_back",
        ):

            st.session_state.page = "Users"

            st.session_state.selected_user = None

            st.session_state.confirm_deactivate = False

            st.rerun()

    except Exception as exc:

        st.error(
            "Unable to load lifecycle data: "
            + friendly_error(exc)
        )