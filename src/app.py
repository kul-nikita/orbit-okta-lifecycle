"""Orbit — Streamlit Okta User Lifecycle UI."""

import streamlit as st

from src.ui.components import render_footer
from src.ui.create_user import render_create_user
from src.ui.dashboard import render_dashboard
from src.ui.export_view import render_export
from src.ui.lifecycle_view import render_lifecycle
from src.ui.sidebar import render_sidebar
from src.ui.styles import load_styles
from src.ui.user_details import render_user_details
from src.ui.users import render_users

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Orbit | Okta Lifecycle",
    page_icon="◉",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# GLOBAL UI
# ============================================================

load_styles()


# ============================================================
# SESSION STATE
# ============================================================

defaults = {
    "page": "Dashboard",
    "selected_user": None,
    "user_page": 0,
    "confirm_deactivate": False,
    "confirm_delete": False,
    "lifecycle_confirm_deactivate": False,
    "lifecycle_confirm_delete": False,
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ============================================================
# SIDEBAR NAVIGATION
# ============================================================

page = render_sidebar()


# ============================================================
# PAGE ROUTING
# ============================================================

if page == "Dashboard":
    render_dashboard()

elif page == "Users":
    render_users()

elif page == "User Details":
    render_user_details()

elif page == "Create User":
    render_create_user()

elif page == "Lifecycle":
    render_lifecycle()

elif page == "Export":
    render_export()

else:
    st.session_state.page = "Dashboard"
    st.rerun()


# ============================================================
# FOOTER
# ============================================================

render_footer()