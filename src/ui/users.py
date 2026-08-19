"""Orbit users directory page."""

import streamlit as st

from src.ui.components import (
    friendly_error,
    get_user_email,
    get_user_name,
    get_user_status,
    load_users,
    show_page_header,
    status_badge,
)


PAGE_SIZE = 5


def _matches_search(user, query):
    """Return True when the user matches the search text."""

    query = query.strip().lower()

    if not query:
        return True

    name = get_user_name(user).lower()
    email = get_user_email(user).lower()
    user_id = user.get("id", "").lower()

    return (
        query in name
        or query in email
        or query in user_id
    )


def _normalize_status(status):
    """Normalize Okta status names for filtering."""

    status = (status or "UNKNOWN").upper()

    if status in {"DEPROVISIONED", "DEACTIVATED"}:
        return "DEACTIVATED"

    return status


def _reset_user_page():
    """Reset pagination to the first page."""

    st.session_state.user_page = 0


def _open_user(user):
    """Open the selected user's details page."""

    st.session_state.selected_user = user
    st.session_state.page = "User Details"
    st.session_state.confirm_deactivate = False
    st.rerun()


def render_users():
    """Render the complete Orbit Users directory."""

    # --------------------------------------------------------
    # If a user is already selected, open User Details
    # --------------------------------------------------------

    if st.session_state.get("selected_user"):
        st.session_state.page = "User Details"
        st.rerun()

    # --------------------------------------------------------
    # Page header
    # --------------------------------------------------------

    show_page_header(
        "Directory",
        "Users",
        "Search, inspect and manage identities in the Okta directory.",
    )

    try:

        # ----------------------------------------------------
        # Load users
        # ----------------------------------------------------

        with st.spinner("Loading Okta directory..."):
            users = load_users()

        # ----------------------------------------------------
        # Toolbar
        # ----------------------------------------------------

        st.markdown(
            """
            <div class="toolbar-label">
                Directory controls
            </div>
            """,
            unsafe_allow_html=True,
        )

        search_col, status_col, refresh_col = st.columns(
            [3.2, 1.5, 1]
        )

        with search_col:
            search = st.text_input(
                "Search",
                placeholder="Search by name, email or user ID...",
                label_visibility="collapsed",
                key="users_search",
                on_change=_reset_user_page,
            )

        with status_col:
            status_filter = st.selectbox(
                "Status",
                [
                    "All",
                    "ACTIVE",
                    "STAGED",
                    "PROVISIONED",
                    "SUSPENDED",
                    "DEACTIVATED",
                ],
                format_func=lambda value: (
                    "All statuses"
                    if value == "All"
                    else value.title()
                ),
                label_visibility="collapsed",
                key="users_status_filter",
                on_change=_reset_user_page,
            )

        with refresh_col:
            if st.button(
                "↻  Refresh",
                use_container_width=True,
                key="users_refresh",
            ):
                st.session_state.user_page = 0
                st.rerun()

        # ----------------------------------------------------
        # Apply search
        # ----------------------------------------------------

        filtered_users = [
            user
            for user in users
            if _matches_search(user, search)
        ]

        # ----------------------------------------------------
        # Apply status filter
        # ----------------------------------------------------

        if status_filter != "All":

            filtered_users = [
                user
                for user in filtered_users
                if _normalize_status(
                    get_user_status(user)
                )
                == status_filter
            ]

        # ----------------------------------------------------
        # Results summary
        # ----------------------------------------------------

        total_users = len(filtered_users)

        result_text = (
            f"{total_users} user"
            if total_users == 1
            else f"{total_users} users"
        )

        st.markdown(
            f"""
            <div class="results-summary">
                <strong>{result_text}</strong>
                <span>matching your current filters</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # ----------------------------------------------------
        # Pagination calculation
        # ----------------------------------------------------

        total_pages = max(
            1,
            (total_users + PAGE_SIZE - 1) // PAGE_SIZE,
        )

        current_page = st.session_state.get(
            "user_page",
            0,
        )

        if current_page >= total_pages:
            current_page = total_pages - 1
            st.session_state.user_page = current_page

        start = current_page * PAGE_SIZE
        end = start + PAGE_SIZE

        visible_users = filtered_users[start:end]

        # ----------------------------------------------------
        # Users table
        # ----------------------------------------------------

        with st.container(border=True):

            # Table header
            h1, h2, h3, h4 = st.columns(
                [1.6, 2.8, 1.4, 1]
            )

            with h1:
                st.markdown(
                    '<div class="table-header">NAME</div>',
                    unsafe_allow_html=True,
                )

            with h2:
                st.markdown(
                    '<div class="table-header">EMAIL</div>',
                    unsafe_allow_html=True,
                )

            with h3:
                st.markdown(
                    '<div class="table-header">STATUS</div>',
                    unsafe_allow_html=True,
                )

            with h4:
                st.markdown(
                    '<div class="table-header">ACTION</div>',
                    unsafe_allow_html=True,
                )

            # ------------------------------------------------
            # Empty state
            # ------------------------------------------------

            if not visible_users:

                st.markdown(
                    """
                    <div class="empty-state">
                        <div class="empty-icon">⌕</div>
                        <div class="empty-title">
                            No users found
                        </div>
                        <div class="empty-description">
                            Try changing your search or status filter.
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            # ------------------------------------------------
            # User rows
            # ------------------------------------------------

            for index, user in enumerate(visible_users):

                c1, c2, c3, c4 = st.columns(
                    [1.6, 2.8, 1.4, 1]
                )

                with c1:
                    st.markdown(
                        f"""
                        <div class="user-name">
                            {get_user_name(user)}
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                with c2:
                    st.markdown(
                        f"""
                        <div class="user-email">
                            {get_user_email(user)}
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                with c3:
                    st.markdown(
                        status_badge(
                            get_user_status(user)
                        ),
                        unsafe_allow_html=True,
                    )

                with c4:
                    if st.button(
                        "View →",
                        key=(
                            f"users_view_"
                            f"{user.get('id', index)}"
                        ),
                        use_container_width=True,
                    ):
                        _open_user(user)

                # Visual separation between rows
                if index < len(visible_users) - 1:
                    st.markdown(
                        '<div class="table-row-divider"></div>',
                        unsafe_allow_html=True,
                    )

        # ----------------------------------------------------
        # Pagination
        # ----------------------------------------------------

        if total_users > 0:

            st.markdown(
                "<div class='pagination-space'></div>",
                unsafe_allow_html=True,
            )

            previous_col, info_col, next_col = st.columns(
                [1, 2, 1]
            )

            with previous_col:

                if st.button(
                    "← Previous",
                    disabled=current_page == 0,
                    use_container_width=True,
                    key="users_previous",
                ):
                    st.session_state.user_page -= 1
                    st.rerun()

            with info_col:

                first_item = start + 1
                last_item = min(
                    end,
                    total_users,
                )

                st.markdown(
                    f"""
                    <div class="pagination-info">
                        <strong>
                            {first_item}–{last_item}
                        </strong>
                        of
                        <strong>
                            {total_users}
                        </strong>
                        &nbsp; · &nbsp;
                        Page
                        <strong>
                            {current_page + 1}
                        </strong>
                        of
                        <strong>
                            {total_pages}
                        </strong>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            with next_col:

                if st.button(
                    "Next →",
                    disabled=current_page >= total_pages - 1,
                    use_container_width=True,
                    key="users_next",
                ):
                    st.session_state.user_page += 1
                    st.rerun()

        # ----------------------------------------------------
        # Helpful action
        # ----------------------------------------------------

        st.markdown(
            "<div class='users-bottom-space'></div>",
            unsafe_allow_html=True,
        )

        if st.button(
            "＋  Create New User",
            key="users_create_user",
        ):
            st.session_state.selected_user = None
            st.session_state.page = "Create User"
            st.rerun()

    except Exception as exc:

        st.error(
            "Unable to load users: "
            + friendly_error(exc)
        )