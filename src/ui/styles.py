"""Orbit UI design system and responsive styling."""

import streamlit as st


def load_styles():
    """Load the global Orbit design system."""

    st.html(
        """
        <style>

        /* =========================================================
           FONT
           IMPORTANT: @import must come before other CSS rules.
           ========================================================= */

        @import url(
            'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap'
        );


        /* =========================================================
           ORBIT DESIGN TOKENS
           ========================================================= */

        :root {

            --orbit-bg: #080D18;
            --orbit-sidebar: #0D1526;

            --orbit-surface: #101827;
            --orbit-surface-2: #141E30;
            --orbit-surface-hover: #18243A;

            --orbit-input: #0B1220;

            --orbit-border: #26344B;
            --orbit-border-hover: #3A4B66;

            --orbit-text: #F8FAFC;
            --orbit-text-soft: #CBD5E1;
            --orbit-muted: #94A3B8;
            --orbit-muted-dark: #64748B;

            --orbit-blue: #3B82F6;
            --orbit-blue-hover: #2563EB;
            --orbit-blue-soft: rgba(59, 130, 246, 0.12);

            --orbit-green: #22C55E;
            --orbit-green-soft: rgba(34, 197, 94, 0.12);

            --orbit-amber: #F59E0B;
            --orbit-amber-soft: rgba(245, 158, 11, 0.12);

            --orbit-red: #EF4444;
            --orbit-red-hover: #DC2626;
            --orbit-red-soft: rgba(239, 68, 68, 0.12);

            --orbit-radius-sm: 8px;
            --orbit-radius-md: 12px;
            --orbit-radius-lg: 16px;

            --orbit-shadow:
                0 12px 35px rgba(0, 0, 0, 0.20);
        }


        /* =========================================================
           GLOBAL
           ========================================================= */

        html,
        body,
        [class*="css"] {

            font-family:
                "Inter",
                "Segoe UI",
                -apple-system,
                BlinkMacSystemFont,
                sans-serif;
        }


        .stApp {

            background:
                var(--orbit-bg);

            color:
                var(--orbit-text);
        }


        .main {

            background:
                var(--orbit-bg);
        }


        /* Main content width */

        .block-container {

            width: 100%;

            max-width: 1480px;

            padding:
                2rem 2.5rem 3rem;

            margin:
                0 auto;
        }


        /* Remove Streamlit branding */

        #MainMenu,
        footer {

            visibility: hidden;
        }


        header {

            background:
                transparent !important;

            height:
                0 !important;
        }


        /* =========================================================
           SIDEBAR
           ========================================================= */

        section[data-testid="stSidebar"] {

            background:
                var(--orbit-sidebar);

            border-right:
                1px solid var(--orbit-border);
        }


        section[data-testid="stSidebar"] > div {

            padding:
                1.25rem 1rem;

            overflow-x:
                hidden;
        }


        /* ---------------------------------------------------------
           BRAND
           --------------------------------------------------------- */

        .brand {

            padding:
                0.45rem 0.4rem 1.35rem;
        }


        .brand-row {

            display:
                flex;

            align-items:
                center;

            gap:
                0.7rem;
        }


        .brand-mark {

            width:
                40px;

            height:
                40px;

            display:
                flex;

            align-items:
                center;

            justify-content:
                center;

            flex:
                0 0 40px;

            border-radius:
                11px;

            background:
                linear-gradient(
                    135deg,
                    #3B82F6,
                    #2563EB
                );

            color:
                #FFFFFF;

            font-size:
                1.05rem;

            font-weight:
                800;

            box-shadow:
                0 8px 20px rgba(37, 99, 235, 0.25);
        }


        .brand-name {

            color:
                var(--orbit-text);

            font-size:
                1.25rem;

            font-weight:
                800;

            letter-spacing:
                -0.04em;
        }


        .brand-subtitle {

            color:
                var(--orbit-muted-dark);

            font-size:
                0.72rem;

            line-height:
                1.5;

            margin-top:
                0.6rem;

            max-width:
                230px;
        }


        /* =========================================================
           SIDEBAR NAVIGATION
           ========================================================= */

        .nav-section {

            color:
                #71829B;

            font-size:
                0.65rem;

            font-weight:
                800;

            letter-spacing:
                0.13em;

            text-transform:
                uppercase;

            margin:
                1.25rem 0 0.55rem 0.25rem;
        }


        section[data-testid="stSidebar"] .stButton {

            margin-bottom:
                0.3rem;
        }


        section[data-testid="stSidebar"]
        .stButton > button {

            width:
                100% !important;

            min-height:
                42px !important;

            justify-content:
                flex-start !important;

            text-align:
                left !important;

            padding:
                0.65rem 0.8rem !important;

            background:
                transparent !important;

            border:
                1px solid transparent !important;

            border-radius:
                10px !important;

            color:
                var(--orbit-text-soft) !important;

            font-size:
                0.88rem !important;

            font-weight:
                600 !important;

            box-shadow:
                none !important;

            transition:
                background 0.18s ease,
                border-color 0.18s ease,
                color 0.18s ease;
        }


        section[data-testid="stSidebar"]
        .stButton > button:hover {

            background:
                var(--orbit-surface-hover) !important;

            border-color:
                var(--orbit-border) !important;

            color:
                #FFFFFF !important;

            transform:
                none !important;
        }


        /* Active navigation */

        section[data-testid="stSidebar"]
        .stButton > button[kind="primary"] {

            background:
                var(--orbit-blue-soft) !important;

            border-color:
                rgba(59, 130, 246, 0.42) !important;

            color:
                #FFFFFF !important;

            box-shadow:
                inset 3px 0 0 var(--orbit-blue) !important;
        }


        /* =========================================================
           ENVIRONMENT BOX
           ========================================================= */

        .environment-box {

            background:
                rgba(16, 24, 39, 0.78);

            border:
                1px solid var(--orbit-border);

            border-radius:
                var(--orbit-radius-md);

            padding:
                0.85rem;

            margin-top:
                0.65rem;
        }


        .environment-label {

            color:
                var(--orbit-muted-dark);

            font-size:
                0.63rem;

            font-weight:
                800;

            letter-spacing:
                0.1em;

            text-transform:
                uppercase;
        }


        .environment-value {

            display:
                flex;

            align-items:
                center;

            gap:
                0.5rem;

            color:
                var(--orbit-text-soft);

            font-size:
                0.78rem;

            font-weight:
                600;

            margin-top:
                0.55rem;
        }


        .environment-dot {

            width:
                7px;

            height:
                7px;

            flex:
                0 0 auto;

            border-radius:
                50%;

            background:
                var(--orbit-green);

            box-shadow:
                0 0 0 4px var(--orbit-green-soft);
        }


        /* =========================================================
           PAGE HEADER
           ========================================================= */

        .topbar {

            display:
                flex;

            align-items:
                flex-start;

            justify-content:
                space-between;

            gap:
                2rem;

            margin-bottom:
                2.2rem;

            position:
                relative;

            z-index:
                2;
        }


        .eyebrow {

            color:
                #60A5FA;

            font-size:
                0.7rem;

            font-weight:
                800;

            letter-spacing:
                0.13em;

            text-transform:
                uppercase;

            margin-bottom:
                0.55rem;
        }


        .page-title {

            color:
                var(--orbit-text);

            font-size:
                clamp(2rem, 3vw, 2.75rem);

            font-weight:
                800;

            letter-spacing:
                -0.045em;

            line-height:
                1.05;
        }


        .page-description {

            color:
                var(--orbit-muted);

            font-size:
                0.95rem;

            line-height:
                1.6;

            margin-top:
                0.7rem;

            max-width:
                680px;
        }


        /* =========================================================
           OKTA CONNECTION INDICATOR
           ========================================================= */

        .connection {

            display:
                inline-flex;

            align-items:
                center;

            justify-content:
                center;

            gap:
                0.55rem;

            background:
                rgba(16, 24, 39, 0.92);

            border:
                1px solid var(--orbit-border);

            border-radius:
                999px;

            padding:
                0.58rem 0.9rem;

            color:
                var(--orbit-text-soft);

            font-size:
                0.76rem;

            font-weight:
                650;

            white-space:
                nowrap;

            flex:
                0 0 auto;

            margin-top:
                0.05rem;
        }


        .connection-dot {

            width:
                8px;

            height:
                8px;

            border-radius:
                50%;

            background:
                var(--orbit-green);

            box-shadow:
                0 0 0 4px var(--orbit-green-soft);
        }


        /* =========================================================
           METRIC CARDS
           ========================================================= */

        .metric-card {

            position:
                relative;

            overflow:
                hidden;

            min-height:
                148px;

            padding:
                1.25rem;

            background:
                linear-gradient(
                    145deg,
                    #111B2B,
                    #0F1726
                );

            border:
                1px solid var(--orbit-border);

            border-radius:
                var(--orbit-radius-lg);

            transition:
                transform 0.2s ease,
                border-color 0.2s ease,
                box-shadow 0.2s ease;
        }


        .metric-card::before {

            content:
                "";

            position:
                absolute;

            top:
                0;

            left:
                0;

            width:
                100%;

            height:
                2px;

            background:
                linear-gradient(
                    90deg,
                    var(--orbit-blue),
                    transparent
                );

            opacity:
                0.8;
        }


        .metric-card:hover {

            transform:
                translateY(-2px);

            border-color:
                var(--orbit-border-hover);

            box-shadow:
                var(--orbit-shadow);
        }


        .metric-label {

            color:
                var(--orbit-muted);

            font-size:
                0.76rem;

            font-weight:
                650;
        }


        .metric-value {

            color:
                var(--orbit-text);

            font-size:
                2.25rem;

            font-weight:
                800;

            letter-spacing:
                -0.05em;

            line-height:
                1;

            margin-top:
                0.6rem;
        }


        .metric-note {

            color:
                var(--orbit-muted-dark);

            font-size:
                0.72rem;

            margin-top:
                0.35rem;
        }


        /* =========================================================
           SECTION HEADINGS
           ========================================================= */

        .section-title {

            color:
                var(--orbit-text);

            font-size:
                1.3rem;

            font-weight:
                750;

            letter-spacing:
                -0.025em;

            margin-top:
                1.8rem;
        }


        .section-description {

            color:
                var(--orbit-muted-dark);

            font-size:
                0.82rem;

            line-height:
                1.5;

            margin-top:
                0.25rem;

            margin-bottom:
                1rem;
        }


        /* =========================================================
           PANELS
           ========================================================= */

        .panel,
        .form-panel {

            background:
                var(--orbit-surface);

            border:
                1px solid var(--orbit-border);

            border-radius:
                var(--orbit-radius-lg);

            padding:
                1.4rem;
        }


        .panel-title,
        .form-title {

            color:
                var(--orbit-text);

            font-size:
                1.25rem;

            font-weight:
                750;
        }


        .panel-description,
        .form-description {

            color:
                var(--orbit-muted);

            font-size:
                0.84rem;

            line-height:
                1.6;

            margin-top:
                0.35rem;
        }


        /* =========================================================
           TABLE
           ========================================================= */

        .table-header {

            color:
                #71829B;

            font-size:
                0.66rem;

            font-weight:
                800;

            letter-spacing:
                0.08em;

            text-transform:
                uppercase;
        }


        .user-name {

            color:
                var(--orbit-text);

            font-size:
                0.88rem;

            font-weight:
                650;

            line-height:
                1.4;
        }


        .user-email {

            color:
                #AFC0D4;

            font-size:
                0.84rem;

            line-height:
                1.4;
        }


        .user-id {

            color:
                var(--orbit-muted-dark);

            font-family:
                "SFMono-Regular",
                Consolas,
                monospace;

            font-size:
                0.72rem;
        }


        /* =========================================================
           STATUS BADGES
           ========================================================= */

        .status-badge {

            display:
                inline-flex;

            align-items:
                center;

            gap:
                0.38rem;

            padding:
                0.3rem 0.62rem;

            border-radius:
                999px;

            font-size:
                0.7rem;

            font-weight:
                700;

            border:
                1px solid;
        }


        .status-active {

            color:
                #4ADE80;

            background:
                var(--orbit-green-soft);

            border-color:
                #166534;
        }


        .status-staged {

            color:
                #FBBF24;

            background:
                var(--orbit-amber-soft);

            border-color:
                #854D0E;
        }


        .status-deactivated {

            color:
                #F87171;

            background:
                var(--orbit-red-soft);

            border-color:
                #7F1D1D;
        }


        .status-suspended {

            color:
                #FB923C;

            background:
                rgba(249, 115, 22, 0.12);

            border-color:
                #9A3412;
        }


        .status-default {

            color:
                #CBD5E1;

            background:
                rgba(100, 116, 139, 0.12);

            border-color:
                #475569;
        }


        /* =========================================================
           INPUTS
           ========================================================= */

        input,
        textarea,
        [data-baseweb="select"] > div {

            background:
                var(--orbit-input) !important;

            color:
                var(--orbit-text) !important;

            border:
                1px solid #33445E !important;

            border-radius:
                9px !important;
        }


        input::placeholder,
        textarea::placeholder {

            color:
                #64748B !important;

            opacity:
                1 !important;
        }


        input:hover,
        textarea:hover,
        [data-baseweb="select"] > div:hover {

            border-color:
                #465A77 !important;
        }


        input:focus,
        textarea:focus {

            border-color:
                var(--orbit-blue) !important;

            box-shadow:
                0 0 0 1px var(--orbit-blue) !important;
        }


        label {

            color:
                var(--orbit-text-soft) !important;

            font-weight:
                600 !important;
        }


        /* =========================================================
           BUTTON SYSTEM
           ========================================================= */

        .stButton > button,
        .stDownloadButton > button,
        .stFormSubmitButton > button {

            min-height:
                42px !important;

            padding:
                0.55rem 1rem !important;

            border-radius:
                9px !important;

            border:
                1px solid var(--orbit-border-hover) !important;

            background:
                #111827 !important;

            color:
                var(--orbit-text-soft) !important;

            font-size:
                0.84rem !important;

            font-weight:
                650 !important;

            box-shadow:
                none !important;

            transition:
                transform 0.16s ease,
                background 0.16s ease,
                border-color 0.16s ease,
                box-shadow 0.16s ease;
        }


        .stButton > button:hover,
        .stDownloadButton > button:hover,
        .stFormSubmitButton > button:hover {

            transform:
                translateY(-1px);

            background:
                var(--orbit-surface-hover) !important;

            border-color:
                #526681 !important;

            color:
                #FFFFFF !important;
        }


        /* Primary */

        button[kind="primary"] {

            background:
                var(--orbit-blue) !important;

            border-color:
                var(--orbit-blue) !important;

            color:
                #FFFFFF !important;

            box-shadow:
                0 5px 16px
                rgba(37, 99, 235, 0.20);
        }


        button[kind="primary"]:hover {

            background:
                var(--orbit-blue-hover) !important;

            border-color:
                var(--orbit-blue-hover) !important;

            box-shadow:
                0 7px 20px
                rgba(37, 99, 235, 0.28);
        }


        /* Download button */

        .stDownloadButton > button {

            background:
                var(--orbit-blue) !important;

            border-color:
                var(--orbit-blue) !important;

            color:
                #FFFFFF !important;
        }


        /* =========================================================
           DANGER BUTTON
           ========================================================= */

        div.st-key-deactivate_user button {

            background:
                transparent !important;

            border-color:
                #7F1D1D !important;

            color:
                #F87171 !important;
        }


        div.st-key-deactivate_user button:hover {

            background:
                var(--orbit-red-soft) !important;

            border-color:
                var(--orbit-red) !important;

            color:
                #FCA5A5 !important;
        }


        /* =========================================================
           CHECKBOX
           ========================================================= */

        [data-testid="stCheckbox"] label {

            color:
                var(--orbit-text-soft) !important;
        }


        /* =========================================================
           SEARCH / FILTER TOOLBAR
           ========================================================= */

        .search-toolbar {

            display:
                flex;

            align-items:
                center;

            gap:
                0.65rem;

            margin:
                1rem 0;
        }


        /* =========================================================
           PAGINATION
           ========================================================= */

        .pagination-info {

            text-align:
                center;

            color:
                var(--orbit-muted);

            font-size:
                0.76rem;

            padding:
                0.55rem;
        }


        /* =========================================================
           EMPTY STATE
           ========================================================= */

        .empty-state {

            text-align:
                center;

            padding:
                2.5rem 1rem;
        }


        .empty-title {

            color:
                var(--orbit-text);

            font-size:
                1rem;

            font-weight:
                700;
        }


        .empty-description {

            color:
                var(--orbit-muted-dark);

            font-size:
                0.8rem;

            line-height:
                1.5;

            margin-top:
                0.35rem;
        }


        /* =========================================================
           FOOTER
           ========================================================= */

        .footer {

            border-top:
                1px solid var(--orbit-border);

            color:
                #52627A;

            font-size:
                0.7rem;

            text-align:
                center;

            margin-top:
                3rem;

            padding-top:
                1.25rem;
        }


        /* =========================================================
           STREAMLIT ALERTS
           ========================================================= */

        .stAlert {

            border-radius:
                10px !important;
        }


        /* =========================================================
           RESPONSIVE — TABLET
           ========================================================= */

        @media (max-width: 1100px) {

            .block-container {

                padding:
                    1.5rem 1.4rem 2.5rem;
            }


            .topbar {

                gap:
                    1rem;
            }


            .metric-card {

                min-height:
                    135px;
            }
        }


        /* =========================================================
           RESPONSIVE — SMALL LAPTOP / TABLET
           ========================================================= */

        @media (max-width: 800px) {

            .block-container {

                padding:
                    1.25rem 1rem 2rem;
            }


            .topbar {

                flex-direction:
                    column;

                gap:
                    1rem;

                margin-bottom:
                    1.5rem;
            }


            .connection {

                align-self:
                    flex-start;
            }


            .page-title {

                font-size:
                    2.25rem;
            }


            .metric-card {

                min-height:
                    120px;
            }


            .form-panel,
            .panel {

                padding:
                    1.1rem;
            }
        }


        /* =========================================================
           RESPONSIVE — MOBILE
           ========================================================= */

        @media (max-width: 600px) {

            .block-container {

                padding:
                    1rem 0.75rem 1.5rem;
            }


            .page-title {

                font-size:
                    1.9rem;
            }


            .page-description {

                font-size:
                    0.88rem;
            }


            .metric-value {

                font-size:
                    1.8rem;
            }


            .metric-card {

                min-height:
                    110px;

                padding:
                    1rem;
            }


            .form-panel,
            .panel {

                border-radius:
                    12px;

                padding:
                    1rem;
            }


            .stButton > button,
            .stDownloadButton > button,
            .stFormSubmitButton > button {

                width:
                    100%;
            }


            section[data-testid="stSidebar"] > div {

                padding:
                    1rem 0.75rem;
            }


            .connection {

                font-size:
                    0.72rem;
            }
        }


        /* =========================================================
           VERY SMALL MOBILE
           ========================================================= */

        @media (max-width: 420px) {

            .page-title {

                font-size:
                    1.7rem;
            }


            .page-description {

                font-size:
                    0.82rem;
            }


            .metric-value {

                font-size:
                    1.65rem;
            }


            .brand-subtitle {

                max-width:
                    180px;
            }


            .section-title {

                font-size:
                    1.15rem;
            }
        }


        /* =========================================================
           ACCESSIBILITY / REDUCED MOTION
           ========================================================= */

        @media (prefers-reduced-motion: reduce) {

            *,
            *::before,
            *::after {

                animation-duration:
                    0.01ms !important;

                animation-iteration-count:
                    1 !important;

                transition-duration:
                    0.01ms !important;

                scroll-behavior:
                    auto !important;
            }
        }

        </style>
        """
    )
    