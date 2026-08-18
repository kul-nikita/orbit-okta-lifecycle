"""Orbit user details and lifecycle action page."""

import streamlit as st

from src import lifecycle

from src.ui.components import (
    clear_selected_user,
    friendly_error,
    get_client,
    get_user_email,
    get_user_name,
    get_user_status,
    show_page_header,
    status_badge,
)


def render_user_details():
    """Render details for the selected user."""

    user = st.session_state.get("selected_user")

    if not user:
        st.session_state.page = "Users"
        st.rerun()

    # --------------------------------------------------------
    # Back to users
    # --------------------------------------------------------

    if st.button(
        "← Back to Users",
        key="back_to_users",
    ):
        clear_selected_user()
        st.session_state.page = "Users"
        st.rerun()

    # --------------------------------------------------------
    # Page header
    # --------------------------------------------------------

    show_page_header(
        "Directory",
        get_user_name(user),
        get_user_email(user),
    )

    status = get_user_status(user).upper()
    profile = user.get("profile", {})

    # --------------------------------------------------------
    # User profile
    # --------------------------------------------------------

    with st.container(border=True):

        st.markdown("### User Profile")

        # ----------------------------------------------------
        # Main identity information
        # ----------------------------------------------------

        name_col, email_col, status_col = st.columns(3)

        with name_col:

            st.caption("NAME")

            st.markdown(
                f'<div class="user-name">'
                f'{get_user_name(user)}'
                f'</div>',
                unsafe_allow_html=True,
            )

            st.caption("FIRST NAME")

            st.write(
                profile.get("firstName") or "—"
            )

        with email_col:

            st.caption("EMAIL")

            st.markdown(
                f'<div class="user-email">'
                f'{get_user_email(user)}'
                f'</div>',
                unsafe_allow_html=True,
            )

            st.caption("LOGIN")

            st.write(
                profile.get("login")
                or "—"
            )

        with status_col:

            st.caption("CURRENT STATUS")

            st.markdown(
                status_badge(status),
                unsafe_allow_html=True,
            )

            st.caption("OKTA USER ID")

            st.code(
                user.get("id", "—"),
                language=None,
            )

        st.divider()

        # ----------------------------------------------------
        # Additional profile information
        # ----------------------------------------------------

        first_col, last_col, state_col = st.columns(3)

        with first_col:

            st.caption("FIRST NAME")

            st.write(
                profile.get("firstName")
                or "—"
            )

        with last_col:

            st.caption("LAST NAME")

            st.write(
                profile.get("lastName")
                or "—"
            )

        with state_col:

            st.caption("LIFECYCLE STATE")

            st.markdown(
                f'<div class="user-name">'
                f'{status.title()}'
                f'</div>',
                unsafe_allow_html=True,
            )

    # --------------------------------------------------------
    # Lifecycle section
    # --------------------------------------------------------

    st.markdown("### Lifecycle")

    with st.container(border=True):

        # ====================================================
        # ACTIVE USER
        # ====================================================

        if status == "ACTIVE":

            st.markdown(
                "### ● User is active"
            )

            st.write(
                "This identity is currently active "
                "in the Okta tenant."
            )

            st.caption(
                "Deactivation is a destructive lifecycle "
                "operation and will disable this identity."
            )

            st.divider()

            if st.button(
                "Deactivate User",
                key="deactivate_user",
                use_container_width=True,
            ):

                st.session_state.confirm_deactivate = True
                st.rerun()

        # ====================================================
        # STAGED / DEACTIVATED USER
        # ====================================================

        elif status in {
            "STAGED",
            "DEPROVISIONED",
            "DEACTIVATED",
        }:

            if status == "STAGED":

                st.markdown(
                    "### ● User is staged"
                )

                st.write(
                    "This identity has been created and "
                    "is ready for activation."
                )

            else:

                st.markdown(
                    "### ● User is deactivated"
                )

                st.write(
                    "This identity is currently deactivated "
                    "and can be activated again."
                )

            st.divider()

            send_email = st.checkbox(
                "Send activation email",
                value=True,
                key="details_send_email",
                help=(
                    "Send an activation email to the user "
                    "after activation."
                ),
            )

            if st.button(
                "Activate User",
                type="primary",
                use_container_width=True,
                key="details_activate",
            ):

                try:

                    with st.spinner(
                        "Activating user..."
                    ):

                        result = lifecycle.activate_user(
                            get_client(),
                            user["id"],
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
                            "User activated successfully."
                        )

                    st.session_state.selected_user = None
                    st.session_state.confirm_deactivate = False
                    st.session_state.page = "Users"

                    st.rerun()

                except Exception as exc:

                    st.error(
                        friendly_error(exc)
                    )

        # ====================================================
        # OTHER STATUS
        # ====================================================

        else:

            st.markdown(
                f"### ● {status.title()} user"
            )

            st.info(
                f"No lifecycle action is currently "
                f"available for status: {status}."
            )

    # --------------------------------------------------------
    # Deactivation confirmation
    # --------------------------------------------------------

    if st.session_state.get(
        "confirm_deactivate",
        False,
    ):

        st.markdown("### Confirm Deactivation")

        with st.container(border=True):

            st.warning(
                f"Are you sure you want to deactivate "
                f"{get_user_name(user)}?"
            )

            st.write(
                "This will deactivate the user's Okta "
                "account and remove their active access."
            )

            st.caption(
                "This action affects the user's lifecycle "
                "state in Okta."
            )

            st.divider()

            cancel_col, confirm_col = st.columns(2)

            # ------------------------------------------------
            # Cancel
            # ------------------------------------------------

            with cancel_col:

                if st.button(
                    "Cancel",
                    use_container_width=True,
                    key="cancel_deactivation",
                ):

                    st.session_state.confirm_deactivate = False
                    st.rerun()

            # ------------------------------------------------
            # Confirm
            # ------------------------------------------------

            with confirm_col:

                if st.button(
                    "Confirm Deactivation",
                    type="primary",
                    use_container_width=True,
                    key="confirm_deactivation",
                ):

                    try:

                        with st.spinner(
                            "Deactivating user..."
                        ):

                            result = lifecycle.deactivate_user(
                                get_client(),
                                user["id"],
                            )

                        if result.get(
                            "status"
                        ) == "already_deactivated":

                            st.info(
                                "User is already deactivated."
                            )

                        else:

                            st.success(
                                "User deactivated successfully."
                            )

                        st.session_state.confirm_deactivate = False
                        st.session_state.selected_user = None
                        st.session_state.page = "Users"

                        st.rerun()

                    except Exception as exc:

                        st.session_state.confirm_deactivate = False

                        st.error(
                            friendly_error(exc)
                        )