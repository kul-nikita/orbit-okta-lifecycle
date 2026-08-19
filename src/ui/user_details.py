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


def _run(operation, user_id, success_message):
    """Execute an Okta lifecycle operation with common error handling."""
    try:
        with st.spinner("Updating Okta..."):
            result = operation(get_client(), user_id)
        if result.get("status", "").startswith("already_"):
            st.info("No change was necessary; the user is already in that state.")
        else:
            st.success(success_message)
        st.rerun()
    except Exception as exc:
        st.error(friendly_error(exc))


def _confirm_deactivate(user_id):
    """Render deactivation confirmation."""
    st.markdown("### Confirm Deactivation")
    st.error(
        "Deactivation is destructive. Okta deprovisions the user "
        "from assigned applications and this action cannot be undone."
    )
    c1, c2 = st.columns(2)

    with c1:
        if st.button(
            "Cancel",
            key="details_cancel_deactivate",
            use_container_width=True,
        ):
            st.session_state.confirm_deactivate = False
            st.rerun()

    with c2:
        if st.button(
            "Confirm Deactivation",
            type="primary",
            key="details_confirm_deactivate",
            use_container_width=True,
        ):
            _run(
                lifecycle.deactivate_user,
                user_id,
                "User deactivation requested successfully.",
            )


def _confirm_delete(user_id):
    """Render permanent deletion confirmation."""
    st.markdown("### Confirm Permanent Deletion")
    st.error(
        "This permanently deletes the Okta user. "
        "The user must already be DEPROVISIONED."
    )
    c1, c2 = st.columns(2)

    with c1:
        if st.button(
            "Cancel",
            key="details_cancel_delete",
            use_container_width=True,
        ):
            st.session_state.confirm_delete = False
            st.rerun()

    with c2:
        if st.button(
            "Delete User Permanently",
            type="primary",
            key="details_confirm_delete",
            use_container_width=True,
        ):
            try:
                with st.spinner("Deleting user from Okta..."):
                    lifecycle.delete_user(get_client(), user_id)
                st.success("User deleted successfully.")
                clear_selected_user()
                st.session_state.confirm_delete = False
                st.session_state.page = "Users"
                st.rerun()
            except Exception as exc:
                st.error(friendly_error(exc))


def render_user_details():
    """Render details and every lifecycle action valid for the user."""
    user = st.session_state.get("selected_user")

    if not user:
        st.session_state.page = "Users"
        st.rerun()

    if st.button("← Back to Users", key="back_to_users"):
        clear_selected_user()
        st.session_state.page = "Users"
        st.rerun()

    show_page_header(
        "Directory",
        get_user_name(user),
        get_user_email(user),
    )

    status = get_user_status(user).upper()
    profile = user.get("profile", {})

    with st.container(border=True):
        st.markdown("### User Profile")
        name_col, email_col, status_col = st.columns(3)

        with name_col:
            st.caption("NAME")
            st.markdown(
                f'<div class="user-name">{get_user_name(user)}</div>',
                unsafe_allow_html=True,
            )
            st.caption("FIRST NAME")
            st.write(profile.get("firstName") or "—")

        with email_col:
            st.caption("EMAIL")
            st.markdown(
                f'<div class="user-email">{get_user_email(user)}</div>',
                unsafe_allow_html=True,
            )
            st.caption("LOGIN")
            st.write(profile.get("login") or "—")

        with status_col:
            st.caption("CURRENT STATUS")
            st.markdown(status_badge(status), unsafe_allow_html=True)
            st.caption("OKTA USER ID")
            st.code(user.get("id", "—"), language=None)

        st.divider()

        c1, c2, c3 = st.columns(3)
        with c1:
            st.caption("FIRST NAME")
            st.write(profile.get("firstName") or "—")
        with c2:
            st.caption("LAST NAME")
            st.write(profile.get("lastName") or "—")
        with c3:
            st.caption("LIFECYCLE STATE")
            st.write(status.title())

    st.markdown("### Lifecycle")

    with st.container(border=True):
        # STAGED -> ACTIVE
        if status == "STAGED":
            st.markdown("### ● User is staged")
            send_email = st.checkbox(
                "Send activation email",
                value=True,
                key="details_staged_email",
            )
            if st.button(
                "Activate User",
                type="primary",
                use_container_width=True,
                key="details_activate_staged",
            ):
                _run(
                    lambda client, uid: lifecycle.activate_user(
                        client, uid, send_email=send_email
                    ),
                    user["id"],
                    "User activation requested successfully.",
                )

        # PROVISIONED / RECOVERY -> REACTIVATE
        elif status in {"PROVISIONED", "RECOVERY"}:
            st.markdown(f"### ● User is {status.lower()}")
            send_email = st.checkbox(
                "Send activation email",
                value=True,
                key="details_reactivate_email",
            )
            if st.button(
                "Reactivate User",
                type="primary",
                use_container_width=True,
                key="details_reactivate",
            ):
                _run(
                    lambda client, uid: lifecycle.reactivate_user(
                        client, uid, send_email=send_email
                    ),
                    user["id"],
                    "User reactivation requested successfully.",
                )

        # ACTIVE -> SUSPEND / DEACTIVATE
        elif status == "ACTIVE":
            st.markdown("### ● User is active")
            c1, c2 = st.columns(2)

            with c1:
                if st.button(
                    "Suspend User",
                    use_container_width=True,
                    key="details_suspend",
                ):
                    _run(
                        lifecycle.suspend_user,
                        user["id"],
                        "User suspension requested successfully.",
                    )

            with c2:
                if st.button(
                    "Deactivate User",
                    use_container_width=True,
                    key="details_deactivate",
                ):
                    st.session_state.confirm_deactivate = True
                    st.rerun()

        # SUSPENDED -> UNSUSPEND / DEACTIVATE
        elif status == "SUSPENDED":
            st.markdown("### ● User is suspended")
            c1, c2 = st.columns(2)

            with c1:
                if st.button(
                    "Unsuspend User",
                    type="primary",
                    use_container_width=True,
                    key="details_unsuspend",
                ):
                    _run(
                        lifecycle.unsuspend_user,
                        user["id"],
                        "User unsuspension requested successfully.",
                    )

            with c2:
                if st.button(
                    "Deactivate User",
                    use_container_width=True,
                    key="details_deactivate_suspended",
                ):
                    st.session_state.confirm_deactivate = True
                    st.rerun()

        # LOCKED_OUT -> UNLOCK / DEACTIVATE
        elif status == "LOCKED_OUT":
            st.markdown("### ● User is locked out")
            c1, c2 = st.columns(2)

            with c1:
                if st.button(
                    "Unlock User",
                    type="primary",
                    use_container_width=True,
                    key="details_unlock",
                ):
                    _run(
                        lifecycle.unlock_user,
                        user["id"],
                        "User unlock requested successfully.",
                    )

            with c2:
                if st.button(
                    "Deactivate User",
                    use_container_width=True,
                    key="details_deactivate_locked",
                ):
                    st.session_state.confirm_deactivate = True
                    st.rerun()

        # DEPROVISIONED -> ACTIVATE / DELETE
        elif status == "DEPROVISIONED":
            st.markdown("### ● User is deprovisioned")
            st.write(
                "The user can be activated again or permanently deleted."
            )
            send_email = st.checkbox(
                "Send activation email",
                value=True,
                key="details_deprovisioned_email",
            )

            c1, c2 = st.columns(2)

            with c1:
                if st.button(
                    "Activate User",
                    type="primary",
                    use_container_width=True,
                    key="details_activate_deprovisioned",
                ):
                    _run(
                        lambda client, uid: lifecycle.activate_user(
                            client, uid, send_email=send_email
                        ),
                        user["id"],
                        "User activation requested successfully.",
                    )

            with c2:
                if st.button(
                    "Delete User",
                    use_container_width=True,
                    key="details_delete",
                ):
                    st.session_state.confirm_delete = True
                    st.rerun()

        else:
            st.info(f"No lifecycle action is available for status {status}.")

    if st.session_state.get("confirm_deactivate", False):
        _confirm_deactivate(user["id"])

    if st.session_state.get("confirm_delete", False):
        _confirm_delete(user["id"])
