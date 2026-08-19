"""Orbit lifecycle management page.

This page exposes every lifecycle operation implemented by
``src.lifecycle`` and only shows operations that are valid for the
selected Okta status.
"""

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


def _select_user(users):
    """Render search + selection and return the selected user."""
    st.markdown("### Find an identity")
    st.caption("Search by name, email address or Okta user ID.")

    search = st.text_input(
        "Search users",
        placeholder="Search users...",
        label_visibility="collapsed",
        key="lifecycle_search",
    )
    query = search.strip().lower()

    matches = [
        user
        for user in users
        if (
            not query
            or query in get_user_name(user).lower()
            or query in get_user_email(user).lower()
            or query in str(user.get("id", "")).lower()
        )
    ]

    if not matches:
        st.info("No matching users found.")
        return None

    options = {
        f"{get_user_name(user)} — {get_user_email(user)}": user
        for user in matches[:100]
    }

    selected_label = st.selectbox(
        "Select user",
        list(options),
        key="lifecycle_user",
    )
    return options[selected_label]


def _run_action(label, operation, user_id, *, confirm=False):
    """Run a lifecycle operation and return whether it was started."""
    if not st.button(
        label,
        type="primary" if not confirm else "secondary",
        use_container_width=True,
    ):
        return False

    try:
        with st.spinner(f"{label}..."):
            result = operation(get_client(), user_id)

        status = result.get("status", "completed")
        if status.startswith("already_"):
            st.info(f"User is already {status[8:].replace('_', ' ')}.")
        else:
            st.success(f"{label} completed/requested successfully.")

        return True
    except Exception as exc:
        st.error(friendly_error(exc))
        return False


def _confirm_destructive_action(
    *,
    title,
    message,
    confirm_key,
    action_label,
    operation,
    user_id,
):
    """Render a two-step confirmation for destructive operations."""
    st.warning(message)
    cancel_col, confirm_col = st.columns(2)

    with cancel_col:
        if st.button("Cancel", key=f"{confirm_key}_cancel", use_container_width=True):
            st.session_state[confirm_key] = False
            st.rerun()

    with confirm_col:
        if st.button(
            action_label,
            key=f"{confirm_key}_confirm",
            type="primary",
            use_container_width=True,
        ):
            try:
                with st.spinner(f"{action_label}..."):
                    result = operation(get_client(), user_id)

                st.session_state[confirm_key] = False
                if result.get("status") == "deleted":
                    st.session_state.lifecycle_deleted = True
                    st.success("User deleted successfully.")
                else:
                    st.success("User deactivation requested successfully.")
                st.rerun()
            except Exception as exc:
                st.error(friendly_error(exc))

    st.caption(title)


def _render_profile(user, status):
    """Render the selected user's profile summary."""
    profile = user.get("profile", {})

    with st.container(border=True):
        st.markdown("### User Profile")
        c1, c2, c3 = st.columns(3)

        with c1:
            st.caption("NAME")
            st.markdown(
                f'<div class="user-name">{get_user_name(user)}</div>',
                unsafe_allow_html=True,
            )
            st.caption("EMAIL")
            st.markdown(
                f'<div class="user-email">{get_user_email(user)}</div>',
                unsafe_allow_html=True,
            )

        with c2:
            st.caption("CURRENT STATUS")
            st.markdown(status_badge(status), unsafe_allow_html=True)
            st.caption("OKTA USER ID")
            st.code(user.get("id", "—"), language=None)

        with c3:
            st.caption("LOGIN")
            st.write(profile.get("login") or "—")
            st.caption("LIFECYCLE STATE")
            st.markdown(
                f'<div class="user-name">{status.title()}</div>',
                unsafe_allow_html=True,
            )


def render_lifecycle():
    """Render the complete lifecycle management screen."""
    show_page_header(
        "Lifecycle",
        "User Lifecycle",
        "Perform every supported Okta identity lifecycle operation from one screen.",
    )

    try:
        with st.spinner("Loading identities..."):
            users = load_users()

        selected = _select_user(users)
        if not selected:
            return

        status = get_user_status(selected).upper()
        _render_profile(selected, status)

        st.markdown("### Lifecycle Actions")

        with st.container(border=True):
            # STAGED -> ACTIVE
            if status == "STAGED":
                st.markdown("### ● Staged")
                st.write("Activate this newly created identity.")
                send_email = st.checkbox(
                    "Send activation email",
                    value=True,
                    key="lifecycle_staged_email",
                )
                if st.button(
                    "Activate User",
                    type="primary",
                    use_container_width=True,
                    key="lifecycle_activate_staged",
                ):
                    try:
                        lifecycle.activate_user(
                            get_client(),
                            selected["id"],
                            send_email=send_email,
                        )
                        st.success("Activation requested successfully.")
                        st.rerun()
                    except Exception as exc:
                        st.error(friendly_error(exc))

            # PROVISIONED / RECOVERY -> restart activation
            elif status in {"PROVISIONED", "RECOVERY"}:
                st.markdown(f"### ● {status.title()}")
                st.write("Restart the user's activation workflow.")
                send_email = st.checkbox(
                    "Send activation email",
                    value=True,
                    key="lifecycle_reactivate_email",
                )
                if st.button(
                    "Reactivate User",
                    type="primary",
                    use_container_width=True,
                    key="lifecycle_reactivate",
                ):
                    try:
                        lifecycle.reactivate_user(
                            get_client(),
                            selected["id"],
                            send_email=send_email,
                        )
                        st.success("Reactivation requested successfully.")
                        st.rerun()
                    except Exception as exc:
                        st.error(friendly_error(exc))

            # ACTIVE -> suspend/deactivate
            elif status == "ACTIVE":
                st.markdown("### ● Active")
                st.write("The user can be suspended or deactivated.")

                c1, c2 = st.columns(2)
                with c1:
                    if st.button(
                        "Suspend User",
                        use_container_width=True,
                        key="lifecycle_suspend",
                    ):
                        try:
                            lifecycle.suspend_user(get_client(), selected["id"])
                            st.success("Suspension requested successfully.")
                            st.rerun()
                        except Exception as exc:
                            st.error(friendly_error(exc))

                with c2:
                    if st.button(
                        "Deactivate User",
                        use_container_width=True,
                        key="lifecycle_deactivate",
                    ):
                        st.session_state.lifecycle_confirm_deactivate = True
                        st.rerun()

            # SUSPENDED -> unsuspend/deactivate
            elif status == "SUSPENDED":
                st.markdown("### ● Suspended")
                st.write("Restore access or permanently deprovision the identity.")

                c1, c2 = st.columns(2)
                with c1:
                    if st.button(
                        "Unsuspend User",
                        type="primary",
                        use_container_width=True,
                        key="lifecycle_unsuspend",
                    ):
                        try:
                            lifecycle.unsuspend_user(get_client(), selected["id"])
                            st.success("Unsuspension requested successfully.")
                            st.rerun()
                        except Exception as exc:
                            st.error(friendly_error(exc))

                with c2:
                    if st.button(
                        "Deactivate User",
                        use_container_width=True,
                        key="lifecycle_deactivate_suspended",
                    ):
                        st.session_state.lifecycle_confirm_deactivate = True
                        st.rerun()

            # LOCKED_OUT -> unlock/deactivate
            elif status == "LOCKED_OUT":
                st.markdown("### ● Locked out")
                st.write("Unlock the account or deprovision it.")

                c1, c2 = st.columns(2)
                with c1:
                    if st.button(
                        "Unlock User",
                        type="primary",
                        use_container_width=True,
                        key="lifecycle_unlock",
                    ):
                        try:
                            lifecycle.unlock_user(get_client(), selected["id"])
                            st.success("Unlock requested successfully.")
                            st.rerun()
                        except Exception as exc:
                            st.error(friendly_error(exc))

                with c2:
                    if st.button(
                        "Deactivate User",
                        use_container_width=True,
                        key="lifecycle_deactivate_locked",
                    ):
                        st.session_state.lifecycle_confirm_deactivate = True
                        st.rerun()

            # DEPROVISIONED -> activate/delete
            elif status == "DEPROVISIONED":
                st.markdown("### ● Deprovisioned")
                st.write(
                    "The user is inactive. You can activate the identity again "
                    "or permanently delete it."
                )

                send_email = st.checkbox(
                    "Send activation email",
                    value=True,
                    key="lifecycle_deprovisioned_email",
                )

                c1, c2 = st.columns(2)
                with c1:
                    if st.button(
                        "Activate User",
                        type="primary",
                        use_container_width=True,
                        key="lifecycle_activate_deprovisioned",
                    ):
                        try:
                            lifecycle.activate_user(
                                get_client(),
                                selected["id"],
                                send_email=send_email,
                            )
                            st.success("Activation requested successfully.")
                            st.rerun()
                        except Exception as exc:
                            st.error(friendly_error(exc))

                with c2:
                    if st.button(
                        "Delete User",
                        use_container_width=True,
                        key="lifecycle_delete",
                    ):
                        st.session_state.lifecycle_confirm_delete = True
                        st.rerun()

            else:
                st.info(f"No lifecycle action is defined for status {status}.")

        if st.session_state.get("lifecycle_confirm_deactivate", False):
            st.markdown("### Confirm Deactivation")
            st.error(
                "Deactivation is destructive: Okta deprovisions the user "
                "from assigned applications."
            )
            _confirm_destructive_action(
                title="This cannot be undone through an Okta reactivation.",
                message="Are you sure you want to deactivate this user?",
                confirm_key="lifecycle_confirm_deactivate",
                action_label="Confirm Deactivation",
                operation=lifecycle.deactivate_user,
                user_id=selected["id"],
            )

        if st.session_state.get("lifecycle_confirm_delete", False):
            st.markdown("### Confirm Permanent Deletion")
            st.error(
                "Permanent deletion removes the user from Okta. "
                "The user must already be DEPROVISIONED."
            )
            _confirm_destructive_action(
                title="Permanent deletion cannot be undone.",
                message="Are you sure you want to permanently delete this user?",
                confirm_key="lifecycle_confirm_delete",
                action_label="Delete User Permanently",
                operation=lifecycle.delete_user,
                user_id=selected["id"],
            )

    except Exception as exc:
        st.error("Unable to load lifecycle data: " + friendly_error(exc))
