"""Orbit sidebar navigation."""

import streamlit as st

from src.ui.components import html

# ============================================================
# NAVIGATION
# ============================================================

def _navigate(page):
    """Update the active page and clear page-specific state."""

    st.session_state.page = page

    st.session_state.selected_user = None
    st.session_state.confirm_deactivate = False

    if page == "Users":
        st.session_state.user_page = 0


def _nav_button(label, page):
    """
    Render one Orbit navigation button.

    The active page uses Streamlit's primary button style.
    Other pages use the secondary style.
    """

    current_page = st.session_state.get(
        "page",
        "Dashboard",
    )

    is_active = current_page == page

    clicked = st.button(
        label,
        key=f"nav_{page.lower().replace(' ', '_')}",
        type="primary" if is_active else "secondary",
        use_container_width=True,
    )

    if clicked:
        _navigate(page)
        st.rerun()


# ============================================================
# SIDEBAR
# ============================================================

def render_sidebar():
    """
    Render the complete Orbit sidebar.

    Returns:
        str: currently selected page.
    """

    with st.sidebar:

        # ====================================================
        # BRAND
        # ====================================================

        html(
            """
            <div class="brand">

                <div class="brand-row">

                    <div class="brand-mark">
                        ◉
                    </div>

                    <div class="brand-name">
                        ORBIT
                    </div>

                </div>

                <div class="brand-subtitle">
                    Okta User Lifecycle Orchestrator
                </div>

            </div>
            """
        )


        # ====================================================
        # OVERVIEW
        # ====================================================

        html(
            """
            <div class="nav-section">
                Overview
            </div>
            """
        )

        _nav_button(
            "▣  Dashboard",
            "Dashboard",
        )


        # ====================================================
        # DIRECTORY
        # ====================================================

        html(
            """
            <div class="nav-section">
                Directory
            </div>
            """
        )

        _nav_button(
            "◎  Users",
            "Users",
        )

        _nav_button(
            "＋  Create User",
            "Create User",
        )


        # ====================================================
        # LIFECYCLE
        # ====================================================

        html(
            """
            <div class="nav-section">
                Lifecycle
            </div>
            """
        )

        _nav_button(
            "↻  Lifecycle",
            "Lifecycle",
        )


        # ====================================================
        # OPERATIONS
        # ====================================================

        html(
            """
            <div class="nav-section">
                Operations
            </div>
            """
        )

        _nav_button(
            "↓  Export",
            "Export",
        )


        # ====================================================
        # SIDEBAR SPACER
        # ====================================================

        html(
            """
            <div style="
                height: 1.25rem;
            "></div>
            """
        )


        # ====================================================
        # ENVIRONMENT
        # ====================================================

        html(
            """
            <div class="environment-box">

                <div class="environment-label">
                    Environment
                </div>

                <div class="environment-value">

                    <span class="environment-dot"></span>

                    <span>
                        Okta Connected
                    </span>

                </div>

            </div>
            """
        )


    return st.session_state.get(
        "page",
        "Dashboard",
    )