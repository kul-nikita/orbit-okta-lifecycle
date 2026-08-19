"""Orbit dashboard page."""

from html import escape

import streamlit as st

from src.ui.components import (
    friendly_error,
    get_user_email,
    get_user_name,
    get_user_status,
    html,
    load_users,
    render_metric_card,
    render_section_heading,
    show_page_header,
    status_badge,
)

# ============================================================
# HELPERS
# ============================================================

def _matches_search(user, query):
    """Return True when a user matches the search query."""

    if not query:
        return True

    query = query.strip().lower()

    name = get_user_name(user).lower()
    email = get_user_email(user).lower()
    user_id = str(user.get("id", "")).lower()

    return (
        query in name
        or query in email
        or query in user_id
    )


def _matches_status(user, selected_status):
    """Return True when a user matches the selected status."""

    if selected_status == "All":
        return True

    actual_status = get_user_status(user).upper()

    return actual_status == selected_status.upper()


def _status_label(status):
    """Convert an Okta status into a friendly UI label."""

    normalized = str(status or "UNKNOWN").upper()

    labels = {
        "ACTIVE": "Active",
        "STAGED": "Staged",
        "PROVISIONED": "Provisioned",
        "SUSPENDED": "Suspended",
        "DEPROVISIONED": "Deactivated",
        "DEACTIVATED": "Deactivated",
    }

    return labels.get(
        normalized,
        normalized.title(),
    )


def _open_user(user):
    """Open a user in the User Details page."""

    st.session_state.selected_user = user
    st.session_state.page = "User Details"
    st.session_state.confirm_deactivate = False

    st.rerun()


def _go_to(page):
    """Navigate to another application page."""

    st.session_state.page = page

    if page == "Users":
        st.session_state.user_page = 0

    st.rerun()


# ============================================================
# DASHBOARD
# ============================================================

def render_dashboard():
    """Render the Orbit dashboard."""

    show_page_header(
        "Overview",
        "Dashboard",
        "Monitor and manage Okta identities from one place.",
    )

    # --------------------------------------------------------
    # LOAD DATA
    # --------------------------------------------------------

    try:

        with st.spinner("Loading Okta directory..."):
            users = load_users()

    except Exception as exc:

        st.error(
            "Unable to load dashboard data: "
            + friendly_error(exc)
        )

        return

    # --------------------------------------------------------
    # METRICS
    # --------------------------------------------------------

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

    c1, c2, c3, c4 = st.columns(
        4,
        gap="medium",
    )

    with c1:
        render_metric_card(
            "Total Users",
            total,
            "All identities",
            accent="blue",
        )

    with c2:
        render_metric_card(
            "Active Users",
            active,
            "Currently active",
            accent="green",
        )

    with c3:
        render_metric_card(
            "Staged Users",
            staged,
            "Awaiting activation",
            accent="amber",
        )

    with c4:
        render_metric_card(
            "Deactivated",
            deactivated,
            "Inactive identities",
            accent="red",
        )

    # --------------------------------------------------------
    # USER DIRECTORY
    # --------------------------------------------------------

    render_section_heading(
        "Recent Users",
        "Latest identities available in the Okta directory.",
    )

    # --------------------------------------------------------
    # SEARCH / FILTER / REFRESH
    # --------------------------------------------------------

    search_col, filter_col, refresh_col = st.columns(
        [2.8, 1.2, 0.65],
        gap="small",
    )

    with search_col:

        search_query = st.text_input(
            "Search users",
            placeholder="Search by name, email, or user ID...",
            key="dashboard_search",
            label_visibility="collapsed",
        )

    with filter_col:

        status_filter = st.selectbox(
            "Status",
            [
                "All",
                "ACTIVE",
                "STAGED",
                "PROVISIONED",
                "SUSPENDED",
                "DEPROVISIONED",
                "LOCKED_OUT",
                "RECOVERY",
            ],
            key="dashboard_status_filter",
            format_func=_status_label,
            label_visibility="collapsed",
        )

    with refresh_col:

        if st.button(
            "↻",
            key="dashboard_refresh",
            use_container_width=True,
            help="Refresh the Okta directory",
        ):
            st.rerun()

    # --------------------------------------------------------
    # FILTER USERS
    # --------------------------------------------------------

    filtered_users = [
        user
        for user in users
        if _matches_search(
            user,
            search_query,
        )
        and _matches_status(
            user,
            status_filter,
        )
    ]

    # --------------------------------------------------------
    # DIRECTORY SUMMARY
    # --------------------------------------------------------

    result_count = len(filtered_users)

    filter_active = (
        bool(search_query.strip())
        or status_filter != "All"
    )

    if filter_active:

        html(
            f"""
            <div class="directory-summary">
                Showing
                <strong>{result_count}</strong>
                of
                <strong>{total}</strong>
                users
            </div>
            """
        )

    else:

        html(
            f"""
            <div class="directory-summary">
                {total} users in directory
            </div>
            """
        )

    # --------------------------------------------------------
    # EMPTY STATE
    # --------------------------------------------------------

    if not filtered_users:

        html(
            """
            <div class="empty-state">

                <div class="empty-icon">
                    ⌕
                </div>

                <div class="empty-title">
                    No users found
                </div>

                <div class="empty-description">
                    Try changing your search or status filter.
                </div>

            </div>
            """
        )

    else:

        # Dashboard intentionally shows only five users.
        recent_users = filtered_users[:5]

        # ----------------------------------------------------
        # TABLE
        # ----------------------------------------------------

        with st.container(
            border=True,
        ):

            # ------------------------------------------------
            # TABLE HEADER
            # ------------------------------------------------

            h1, h2, h3, h4, h5 = st.columns(
                [1.4, 2.2, 1.1, 0.9, 0.8],
                gap="medium",
            )

            with h1:

                html(
                    """
                    <div class="table-header">
                        NAME
                    </div>
                    """
                )

            with h2:

                html(
                    """
                    <div class="table-header">
                        EMAIL
                    </div>
                    """
                )

            with h3:

                html(
                    """
                    <div class="table-header">
                        STATUS
                    </div>
                    """
                )

            with h4:

                html(
                    """
                    <div class="table-header">
                        TENANT
                    </div>
                    """
                )

            with h5:

                html(
                    """
                    <div class="table-header">
                        ACTION
                    </div>
                    """
                )

            # ------------------------------------------------
            # USER ROWS
            # ------------------------------------------------

            for index, user in enumerate(recent_users):

                user_id = str(
                    user.get(
                        "id",
                        index,
                    )
                )

                name = escape(
                    get_user_name(user)
                )

                email = escape(
                    get_user_email(user)
                )

                c1, c2, c3, c4, c5 = st.columns(
                    [1.4, 2.2, 1.1, 0.9, 0.8],
                    gap="medium",
                )

                with c1:

                    html(
                        f"""
                        <div class="user-name">
                            {name}
                        </div>
                        """
                    )

                with c2:

                    html(
                        f"""
                        <div class="user-email">
                            {email}
                        </div>
                        """
                    )

                with c3:

                    st.html(
                        status_badge(
                            get_user_status(user)
                        )
                    )

                with c4:
                    tenant = user.get("_tenant", "—")
                    html(
                        f"""
                        <div class="user-email">
                            {tenant}
                        </div>
                        """
                    )

                with c5:

                    if st.button(
                        "View",
                        key=f"dashboard_view_{user_id}",
                        use_container_width=True,
                    ):
                        _open_user(user)

    # --------------------------------------------------------
    # VIEW ALL USERS
    # --------------------------------------------------------

    if len(filtered_users) > 5:

        st.write("")

        if st.button(
            "View all users  →",
            key="dashboard_view_all",
        ):
            _go_to("Users")

    # --------------------------------------------------------
    # QUICK ACTIONS
    # --------------------------------------------------------

    render_section_heading(
        "Quick Actions",
        "Common identity management operations.",
    )

    a1, a2, a3 = st.columns(
        3,
        gap="medium",
    )

    # --------------------------------------------------------
    # CREATE USER
    # --------------------------------------------------------

    with a1, st.container(
        border=True,
    ):

        html(
            """
                <div class="quick-action">

                    <div class="quick-action-icon">
                        +
                    </div>

                    <div class="quick-action-title">
                        Create User
                    </div>

                    <div class="quick-action-description">
                        Create a new identity in the Okta tenant.
                    </div>

                </div>
                """
        )

        if st.button(
            "Create User",
            key="dashboard_create",
            type="primary",
            use_container_width=True,
        ):

            _go_to("Create User")

    # --------------------------------------------------------
    # LIFECYCLE
    # --------------------------------------------------------

    with a2, st.container(
        border=True,
    ):

        html(
            """
                <div class="quick-action">

                    <div class="quick-action-icon">
                        ↻
                    </div>

                    <div class="quick-action-title">
                        Manage Lifecycle
                    </div>

                    <div class="quick-action-description">
                        Manage activation, suspension, deactivation, unlocking and deletion.
                    </div>

                </div>
                """
        )

        if st.button(
            "Manage Lifecycle",
            key="dashboard_lifecycle",
            use_container_width=True,
        ):

            _go_to("Lifecycle")

    # --------------------------------------------------------
    # EXPORT
    # --------------------------------------------------------

    with a3, st.container(
        border=True,
    ):

        html(
            """
                <div class="quick-action">

                    <div class="quick-action-icon">
                        ↓
                    </div>

                    <div class="quick-action-title">
                        Export Users
                    </div>

                    <div class="quick-action-description">
                        Export the current directory to CSV.
                    </div>

                </div>
                """
        )

        if st.button(
            "Export Users",
            key="dashboard_export",
            use_container_width=True,
        ):

            _go_to("Export")