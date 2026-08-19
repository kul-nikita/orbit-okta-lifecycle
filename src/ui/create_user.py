"""Orbit create-user page."""

import re
from html import escape

import streamlit as st

from src import lifecycle
from src.ui.components import (
    friendly_error,
    get_client,
    get_user_name,
    html,
    show_page_header,
    status_badge,
)

# ============================================================
# VALIDATION
# ============================================================

EMAIL_PATTERN = re.compile(
    r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
)


# ============================================================
# HELPERS
# ============================================================

def _clear_created_user():
    """Remove the previously created user from session state."""

    st.session_state.pop(
        "created_user",
        None,
    )


def _open_created_user(user):
    """Open the created user in the User Details page."""

    st.session_state.selected_user = user
    st.session_state.page = "User Details"
    st.session_state.confirm_deactivate = False

    st.rerun()


def _activate_created_user(user):
    """Activate a newly created staged user."""

    user_id = user.get("id")

    if not user_id:
        st.error(
            "The created user does not contain a valid Okta user ID."
        )
        return

    try:

        with st.spinner("Activating user in Okta..."):

            result = lifecycle.activate_user(
                get_client(),
                user_id,
                send_email=True,
            )

        # ----------------------------------------------------
        # Already active
        # ----------------------------------------------------

        if result.get("status") == "already_active":

            st.info(
                "This user is already active."
            )

            return

        # ----------------------------------------------------
        # Successful activation
        # ----------------------------------------------------

        updated_user = dict(user)

        response_status = result.get(
            "status",
            "ACTIVE",
        )

        updated_user["status"] = response_status

        st.session_state.created_user = updated_user

        st.success(
            f"User {get_user_name(updated_user)} "
            "was activated successfully."
        )

        st.rerun()

    except Exception as exc:  # noqa: BLE001

        st.error(
            "Unable to activate the user: "
            + friendly_error(exc)
        )


# ============================================================
# PAGE
# ============================================================

def render_create_user():
    """Render the Orbit Create User page."""

    show_page_header(
        "Directory",
        "Create User",
        "Create a new identity in your Okta tenant.",
    )

    # ========================================================
    # CREATE USER CARD
    # ========================================================

    with st.container(
        border=True,
    ):

        html(
            """
            <div class="form-section-header">

                <div class="form-section-title">
                    User Profile
                </div>

                <div class="form-section-description">
                    Provide the required information for the new identity.
                </div>

            </div>
            """
        )

        # ----------------------------------------------------
        # FORM
        # ----------------------------------------------------

        with st.form(
            "create_user_form",
            clear_on_submit=False,
        ):

            # ------------------------------------------------
            # NAME
            # ------------------------------------------------

            first_col, last_col = st.columns(
                2,
                gap="medium",
            )

            with first_col:

                first_name = st.text_input(
                    "First name",
                    placeholder="Ada",
                    max_chars=100,
                )

            with last_col:

                last_name = st.text_input(
                    "Last name",
                    placeholder="Lovelace",
                    max_chars=100,
                )

            # ------------------------------------------------
            # EMAIL
            # ------------------------------------------------

            email = st.text_input(
                "Email address",
                placeholder="ada@example.com",
                max_chars=254,
            )

            # ------------------------------------------------
            # ACTIVATION
            # ------------------------------------------------

            activate_now = st.checkbox(
                "Activate immediately",
                value=False,
                help=(
                    "When disabled, Okta creates the user "
                    "in STAGED status. When enabled, Okta "
                    "activates the user immediately."
                ),
            )

            html(
                """
                <div class="form-help">
                    Leave this unchecked to create the identity
                    in STAGED status.
                </div>
                """
            )

            st.divider()

            # ------------------------------------------------
            # SUBMIT
            # ------------------------------------------------

            submitted = st.form_submit_button(
                "Create User",
                type="primary",
                use_container_width=True,
            )

    # ========================================================
    # FORM PROCESSING
    # ========================================================

    if submitted:

        # ----------------------------------------------------
        # CLEAN INPUT
        # ----------------------------------------------------

        first_name = first_name.strip()
        last_name = last_name.strip()
        email = email.strip().lower()

        # ----------------------------------------------------
        # VALIDATION
        # ----------------------------------------------------

        if not first_name:

            st.error(
                "Please enter the user's first name."
            )

            return

        if not last_name:

            st.error(
                "Please enter the user's last name."
            )

            return

        if not email:

            st.error(
                "Please enter the user's email address."
            )

            return

        if not EMAIL_PATTERN.match(email):

            st.error(
                "Please enter a valid email address."
            )

            return

        # ----------------------------------------------------
        # PROFILE
        # ----------------------------------------------------

        profile = {
            "firstName": first_name,
            "lastName": last_name,
            "email": email,
            "login": email,
        }

        # ----------------------------------------------------
        # CREATE USER
        # ----------------------------------------------------

        try:

            with st.spinner(
                "Creating user in Okta..."
            ):

                user = lifecycle.create_user(
                    get_client(),
                    profile,
                    activate=activate_now,
                )

            # Store result for the next rerender.
            st.session_state.created_user = user

        except Exception as exc:  # noqa: BLE001

            st.error(
                "Unable to create the user: "
                + friendly_error(exc)
            )

            return

    # ========================================================
    # CREATED USER RESULT
    # ========================================================

    created_user = st.session_state.get(
        "created_user"
    )

    if not created_user:
        return

    # --------------------------------------------------------
    # SUCCESS BANNER
    # --------------------------------------------------------

    created_name = escape(
        get_user_name(created_user)
    )

    html(
        f"""
        <div class="success-panel">

            <div class="success-icon">
                ✓
            </div>

            <div>
                <div class="success-title">
                    User created successfully
                </div>

                <div class="success-description">
                    {created_name} has been added to your
                    Okta directory.
                </div>
            </div>

        </div>
        """
    )

    # ========================================================
    # CREATED USER DETAILS
    # ========================================================

    html(
        """
        <div class="created-user-heading">
            Created User
        </div>
        """
    )

    user_id = str(
        created_user.get(
            "id",
            "—",
        )
    )

    user_status = created_user.get(
        "status",
        "UNKNOWN",
    )

    status_normalized = str(
        user_status
    ).upper()

    # --------------------------------------------------------
    # USER INFORMATION
    # --------------------------------------------------------

    info_col, status_col = st.columns(
        [2.4, 1],
        gap="medium",
    )

    with info_col:

        html(
            """
            <div class="detail-label">
                USER ID
            </div>
            """
        )

        st.code(
            user_id,
            language=None,
        )

    with status_col:

        html(
            """
            <div class="detail-label">
                STATUS
            </div>
            """
        )

        st.html(
            status_badge(
                user_status
            )
        )

    # ========================================================
    # NEXT ACTIONS
    # ========================================================

    st.divider()

    action_col1, action_col2, action_col3 = st.columns(
        [1, 1, 1],
        gap="small",
    )

    # --------------------------------------------------------
    # VIEW USER
    # --------------------------------------------------------

    with action_col1:

        if st.button(
            "View User",
            key="create_view_user",
            use_container_width=True,
        ):

            _open_created_user(
                created_user
            )

    # --------------------------------------------------------
    # ACTIVATE USER
    # --------------------------------------------------------

    with action_col2:

        if status_normalized == "STAGED":

            if st.button(
                "Activate User",
                key="create_activate_user",
                type="primary",
                use_container_width=True,
            ):

                _activate_created_user(
                    created_user
                )

        elif status_normalized == "ACTIVE":

            st.button(
                "Already Active",
                key="create_already_active",
                disabled=True,
                use_container_width=True,
            )

        else:

            st.button(
                "Activate User",
                key="create_activate_disabled",
                disabled=True,
                use_container_width=True,
            )

    # --------------------------------------------------------
    # CREATE ANOTHER
    # --------------------------------------------------------

    with action_col3:

        if st.button(
            "Create Another",
            key="create_another_user",
            use_container_width=True,
        ):

            _clear_created_user()

            st.rerun()