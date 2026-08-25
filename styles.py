from html import escape

import streamlit as st


def apply_app_style():
    """Small, app-owned style layer inspired by Base's high-contrast visual system."""
    st.html(
        """
        <style>
        .block-container {
            padding-top: 2.25rem;
            padding-bottom: 4rem;
        }
        [data-testid="stSidebar"] {
            background: #0052ff;
        }
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
        [data-testid="stSidebar"] [data-testid="stCaptionContainer"] p,
        [data-testid="stSidebar"] label p {
            color: #ffffff;
        }
        [data-testid="stSidebar"] [role="radiogroup"] label {
            border-radius: 4px;
            padding: .35rem .55rem;
            transition: background .15s ease;
        }
        [data-testid="stSidebar"] [role="radiogroup"] label:hover {
            background: rgba(255,255,255,.12);
        }
        [data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) {
            background: #ffffff;
        }
        [data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) p {
            color: #0052ff;
            font-weight: 700;
        }
        [data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) span {
            border-color: #0052ff;
        }
        .cpma-page-intro {
            border-top: 4px solid #0052ff;
            padding: 1.1rem 0 1.55rem;
            margin-bottom: .35rem;
        }
        .cpma-page-intro__eyebrow {
            color: #0052ff;
            font-size: .78rem;
            font-weight: 700;
            letter-spacing: .12em;
            margin: 0 0 .7rem;
            text-transform: uppercase;
        }
        .cpma-page-intro h1 {
            font-size: clamp(2.15rem, 4vw, 4.6rem);
            line-height: .98;
            letter-spacing: -.055em;
            margin: 0;
            max-width: 900px;
        }
        .cpma-page-intro p {
            color: #5b616e;
            font-size: 1rem;
            line-height: 1.65;
            margin: 1rem 0 0;
            max-width: 760px;
        }
        .cpma-sidebar-brand {
            border-bottom: 1px solid rgba(255,255,255,.2);
            margin: .25rem 0 1.35rem;
            padding: .35rem 0 1.35rem;
        }
        .cpma-sidebar-brand__mark {
            align-items: center;
            background: #ffffff;
            color: #0052ff;
            display: inline-flex;
            font-size: 1rem;
            font-weight: 800;
            height: 2.4rem;
            justify-content: center;
            margin-bottom: .9rem;
            width: 2.4rem;
        }
        .cpma-sidebar-brand h2 {
            color: #ffffff;
            font-size: 1.35rem;
            letter-spacing: -.03em;
            line-height: 1.08;
            margin: 0;
        }
        .cpma-sidebar-brand p {
            color: rgba(255,255,255,.62);
            font-size: .76rem;
            letter-spacing: .08em;
            margin: .55rem 0 0;
            text-transform: uppercase;
        }
        @media (max-width: 768px) {
            .block-container {
                padding-top: 1.25rem;
            }
            .cpma-page-intro h1 {
                font-size: 2.35rem;
            }
            .cpma-page-intro p {
                font-size: .92rem;
            }
        }
        div[data-testid="stMetric"] {
            min-height: 132px;
            padding: 1.15rem 1.2rem;
        }
        div[data-testid="stMetric"] label {
            font-size: .8rem;
            font-weight: 650;
            letter-spacing: .04em;
        }
        div[data-testid="stMetricValue"] {
            letter-spacing: -.04em;
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: .4rem;
        }
        .stTabs [data-baseweb="tab"] {
            border-radius: 999px;
            padding-left: 1rem;
            padding-right: 1rem;
        }
        </style>
        """
    )


def sidebar_brand():
    st.html(
        """
        <div class="cpma-sidebar-brand">
            <div class="cpma-sidebar-brand__mark">C</div>
            <h2>Campus Project<br>Hub</h2>
            <p>Project operations</p>
        </div>
        """
    )


def page_intro(eyebrow, title, description):
    st.html(
        f"""
        <section class="cpma-page-intro">
            <div class="cpma-page-intro__eyebrow">{escape(eyebrow)}</div>
            <h1>{escape(title)}</h1>
            <p>{escape(description)}</p>
        </section>
        """
    )


