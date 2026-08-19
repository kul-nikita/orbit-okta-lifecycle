"""Reusable Orbit UI components and shared helpers."""

import textwrap
from html import escape

import streamlit as st

from src import lifecycle
from src.okta_client import OktaClient, OktaClientError, get_clients

# ============================================================
# HTML HELPER
# ============================================================

def html(content):
    """
    Render an HTML fragment using Streamlit's native HTML renderer.

    textwrap.dedent() prevents indentation inside multiline
    Python strings from causing unwanted formatting.
    """

    if not content:
        return

    st.html(
        textwrap.dedent(str(content)).strip()
    )


# ============================================================
# BACKEND HELPERS
# ============================================================

def get_client():
    """Create an Okta client from environment configuration (Tenant 1)."""
    return OktaClient()


def get_all_clients():
    """Return all configured tenant clients."""
    return get_clients()


def load_users():
    """Load all users from all tenants, tagged with _tenant."""
    clients = get_all_clients()
    all_users = []
    for client in clients:
        users = lifecycle.list_users(client)
        for user in users:
            user["_tenant"] = client.label
        all_users.extend(users)
    return all_users


# ============================================================
# USER HELPERS
# ============================================================

def get_user_profile(user):
    """Return an Okta user's profile dictionary."""

    if not isinstance(user, dict):
        return {}

    profile = user.get("profile")

    if not isinstance(profile, dict):
        return {}

    return profile


def get_user_name(user):
    """Return the most useful display name for an Okta user."""

    profile = get_user_profile(user)

    first = str(
        profile.get("firstName", "") or ""
    ).strip()

    last = str(
        profile.get("lastName", "") or ""
    ).strip()

    full_name = f"{first} {last}".strip()

    return (
        full_name
        or profile.get("displayName")
        or profile.get("login")
        or profile.get("email")
        or "Unknown user"
    )


def get_user_email(user):
    """Return the user's email address or login."""

    profile = get_user_profile(user)

    return (
        profile.get("email")
        or profile.get("login")
        or "—"
    )


def get_user_login(user):
    """Return the user's Okta login."""

    profile = get_user_profile(user)

    return (
        profile.get("login")
        or profile.get("email")
        or "—"
    )


def get_user_id(user):
    """Return the user's Okta ID."""

    if not isinstance(user, dict):
        return "—"

    return user.get("id") or "—"


def get_user_status(user):
    """Return the user's normalized Okta lifecycle status."""

    if not isinstance(user, dict):
        return "UNKNOWN"

    return normalize_status(
        user.get("status")
    )


def normalize_status(status):
    """
    Normalize an Okta status into a consistent uppercase value.

    This keeps filtering, badges, metrics, and lifecycle logic
    consistent across the application.
    """

    if status is None:
        return "UNKNOWN"

    value = str(status).strip().upper()

    if not value:
        return "UNKNOWN"

    # Treat common naming variations consistently.
    if value == "DEACTIVATED":
        return "DEPROVISIONED"

    return value


# ============================================================
# STATUS HELPERS
# ============================================================

def get_status_label(status):
    """Return the human-readable label for an Okta status."""

    normalized = normalize_status(status)

    labels = {
        "ACTIVE": "Active",
        "STAGED": "Staged",
        "PROVISIONED": "Provisioned",
        "SUSPENDED": "Suspended",
        "DEPROVISIONED": "Deactivated",
        "UNKNOWN": "Unknown",
    }

    return labels.get(
        normalized,
        normalized.title(),
    )


def status_badge(status):
    """
    Return a professional Orbit status badge.

    Supported Okta states:
        ACTIVE
        STAGED
        PROVISIONED
        SUSPENDED
        DEPROVISIONED
        UNKNOWN
    """

    normalized = normalize_status(status)

    status_config = {
        "ACTIVE": (
            "status-active",
            "Active",
        ),

        "STAGED": (
            "status-staged",
            "Staged",
        ),

        "PROVISIONED": (
            "status-default",
            "Provisioned",
        ),

        "SUSPENDED": (
            "status-suspended",
            "Suspended",
        ),

        "DEPROVISIONED": (
            "status-deactivated",
            "Deactivated",
        ),

        "UNKNOWN": (
            "status-default",
            "Unknown",
        ),
    }

    css_class, label = status_config.get(
        normalized,
        (
            "status-default",
            normalized.title(),
        ),
    )

    return (
        f'<span class="status-badge {css_class}">'
        f'<span class="status-indicator">●</span>'
        f'{escape(label)}'
        f'</span>'
    )


# ============================================================
# CONNECTION INDICATOR
# ============================================================

def render_connection_badge(
    label="Okta Connected",
    connected=True,
):
    """Render the Orbit connection status indicator."""

    if connected:
        dot_class = "connection-dot"
        text = label
    else:
        dot_class = (
            "connection-dot connection-dot-error"
        )
        text = "Okta Disconnected"

    html(
        f"""
        <div class="connection">
            <span class="{dot_class}"></span>
            <span>{escape(str(text))}</span>
        </div>
        """
    )


# ============================================================
# PAGE HEADER
# ============================================================

def show_page_header(
    section,
    title,
    description,
    connection_label="Okta Connected",
    connected=True,
):
    """
    Render the standard Orbit page header.

    Every major page uses the same visual hierarchy:
        eyebrow
        title
        description
        connection status
    """

    connection_text = (
        connection_label
        if connected
        else "Okta Disconnected"
    )

    connection_class = (
        "connection-dot"
        if connected
        else "connection-dot connection-dot-error"
    )

    html(
        f"""
        <div class="topbar">

            <div class="page-heading">

                <div class="eyebrow">
                    {escape(str(section))}
                </div>

                <div class="page-title">
                    {escape(str(title))}
                </div>

                <div class="page-description">
                    {escape(str(description))}
                </div>

            </div>

            <div class="connection">
                <span class="{connection_class}"></span>
                <span>{escape(str(connection_text))}</span>
            </div>

        </div>
        """
    )


# ============================================================
# METRIC CARDS
# ============================================================

def render_metric_card(
    label,
    value,
    note,
    accent="blue",
):
    """
    Render a dashboard metric card.

    Supported accents:
        blue
        green
        amber
        red
    """

    allowed_accents = {
        "blue",
        "green",
        "amber",
        "red",
    }

    if accent not in allowed_accents:
        accent = "blue"

    html(
        f"""
        <div class="metric-card metric-{accent}">

            <div class="metric-label">
                {escape(str(label))}
            </div>

            <div class="metric-value">
                {escape(str(value))}
            </div>

            <div class="metric-note">
                {escape(str(note))}
            </div>

        </div>
        """
    )


# ============================================================
# SECTION HEADINGS
# ============================================================

def render_section_heading(
    title,
    description=None,
):
    """Render a consistent Orbit section heading."""

    description_html = ""

    if description:
        description_html = f"""
        <div class="section-description">
            {escape(str(description))}
        </div>
        """

    html(
        f"""
        <div class="section-heading">

            <div class="section-title">
                {escape(str(title))}
            </div>

            {description_html}

        </div>
        """
    )


# ============================================================
# USER SUMMARY
# ============================================================

def render_user_summary(user):
    """
    Render a compact identity summary.

    Used by:
        User Details
        Lifecycle
        Confirmation panels
    """

    name = escape(
        str(get_user_name(user))
    )

    email = escape(
        str(get_user_email(user))
    )

    user_id = escape(
        str(get_user_id(user))
    )

    status = status_badge(
        get_user_status(user)
    )

    html(
        f"""
        <div class="user-summary">

            <div class="user-summary-main">

                <div class="user-summary-name">
                    {name}
                </div>

                <div class="user-summary-email">
                    {email}
                </div>

            </div>

            <div class="user-summary-status">
                {status}
            </div>

        </div>

        <div class="user-summary-id">
            ID: {user_id}
        </div>
        """
    )


# ============================================================
# USER TABLE ROW
# ============================================================

def render_user_row(user):
    """
    Render reusable user information.

    The actual Streamlit action button is intentionally kept
    outside this helper so button clicks remain interactive.
    """

    name = escape(
        str(get_user_name(user))
    )

    email = escape(
        str(get_user_email(user))
    )

    status = status_badge(
        get_user_status(user)
    )

    html(
        f"""
        <div class="user-row">

            <div class="user-row-name">
                {name}
            </div>

            <div class="user-row-email">
                {email}
            </div>

            <div class="user-row-status">
                {status}
            </div>

        </div>
        """
    )


# ============================================================
# INFO PANEL
# ============================================================

def render_info_panel(
    title,
    description=None,
):
    """Render a reusable Orbit information panel."""

    description_html = ""

    if description:
        description_html = f"""
        <div class="panel-description">
            {escape(str(description))}
        </div>
        """

    html(
        f"""
        <div class="panel">

            <div class="panel-title">
                {escape(str(title))}
            </div>

            {description_html}

        </div>
        """
    )


# ============================================================
# EMPTY STATE
# ============================================================

def render_empty_state(
    title,
    description=None,
):
    """Render a professional empty state."""

    description_html = ""

    if description:
        description_html = f"""
        <div class="empty-description">
            {escape(str(description))}
        </div>
        """

    html(
        f"""
        <div class="empty-state">

            <div class="empty-title">
                {escape(str(title))}
            </div>

            {description_html}

        </div>
        """
    )


# ============================================================
# LOADING STATE
# ============================================================

def render_loading_state(
    message="Loading...",
):
    """Render a reusable loading indicator."""

    html(
        f"""
        <div class="loading-state">

            <span class="loading-spinner"></span>

            <span>
                {escape(str(message))}
            </span>

        </div>
        """
    )


# ============================================================
# RESULT MESSAGES
# ============================================================

def render_success(message):
    """Render a professional success message."""

    html(
        f"""
        <div class="orbit-message orbit-success">

            <span class="message-icon">✓</span>

            <span>
                {escape(str(message))}
            </span>

        </div>
        """
    )


def render_warning(message):
    """Render a professional warning message."""

    html(
        f"""
        <div class="orbit-message orbit-warning">

            <span class="message-icon">!</span>

            <span>
                {escape(str(message))}
            </span>

        </div>
        """
    )


def render_error(message):
    """Render a professional error message."""

    html(
        f"""
        <div class="orbit-message orbit-error">

            <span class="message-icon">×</span>

            <span>
                {escape(str(message))}
            </span>

        </div>
        """
    )


# ============================================================
# FOOTER
# ============================================================

def render_footer():
    """Render the application footer."""

    html(
        """
        <div class="footer">
            Orbit · Okta User Lifecycle Orchestrator
        </div>
        """
    )


# ============================================================
# ERROR HANDLING
# ============================================================



def friendly_error(exc):
    """Format an exception into a user-friendly error message."""
    if isinstance(exc, OktaClientError):
        return (
            f"{exc}\n\n"
            f"Status: {exc.status_code}\n"
            f"Response: {exc.response_body}"
        )

    return str(exc)


# ============================================================
# SESSION STATE
# ============================================================

def clear_selected_user():
    """Clear user-specific session state."""

    st.session_state.selected_user = None
    st.session_state.confirm_deactivate = False
    st.session_state.confirm_delete = False
    st.session_state.lifecycle_confirm_deactivate = False
    st.session_state.lifecycle_confirm_delete = False


def get_selected_user():
    """Return the currently selected user."""

    return st.session_state.get(
        "selected_user"
    )


def set_selected_user(user):
    """Store a selected user in session state."""

    st.session_state.selected_user = user
    st.session_state.confirm_deactivate = False