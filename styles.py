from html import escape

import streamlit as st


def apply_app_style():
    """Small, app-owned style layer inspired by Base's high-contrast visual system."""
    st.html(
        """
        <style>
        [data-testid="stAppViewContainer"] {
            background:
                radial-gradient(circle at 88% 0%, rgba(154, 153, 248, .24) 0, rgba(194, 193, 251, .12) 18rem, transparent 36rem),
                linear-gradient(180deg, #f7f7fe 0, #ffffff 22rem);
        }
        .block-container {
            padding-top: 2.25rem;
            padding-bottom: 4rem;
        }
        [data-testid="stSidebar"] {
            background: linear-gradient(
                180deg,
                #070628 0%,
                #0d0c52 14%,
                #1b1894 34%,
                #3a38d6 68%,
                #5552ea 100%
            );
        }
        [data-testid="stSidebar"]::before {
            background:
                radial-gradient(circle at 18% 8%, rgba(154, 153, 248, .42), transparent 11rem),
                radial-gradient(circle at 95% 92%, rgba(111, 109, 245, .35), transparent 13rem);
            content: "";
            inset: 0;
            pointer-events: none;
            position: absolute;
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
            background: rgba(255,255,255,.14);
        }
        [data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) {
            background: linear-gradient(105deg, #ffffff 0%, #e3e3fd 100%);
            box-shadow: 0 10px 26px rgba(7, 6, 40, .2);
        }
        [data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) p {
            color: #3a38d6;
            font-weight: 700;
        }
        [data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) span {
            border-color: #3a38d6;
        }
        .cpma-page-intro {
            border-top: 0;
            padding: 1.1rem 0 1.55rem;
            margin-bottom: .35rem;
            position: relative;
        }
        .cpma-page-intro::before {
            background: linear-gradient(90deg, #2623b8 0%, #5552ea 46%, #9a99f8 76%, transparent 100%);
            content: "";
            height: 4px;
            left: 0;
            position: absolute;
            right: 0;
            top: 0;
        }
        .cpma-page-intro__eyebrow {
            color: #3a38d6;
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
            background: linear-gradient(145deg, #ffffff 0%, #c2c1fb 100%);
            box-shadow: 0 10px 28px rgba(7, 6, 40, .28);
            color: #1b1894;
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
            background: linear-gradient(145deg, rgba(255,255,255,.96) 0%, rgba(227,227,253,.72) 100%);
            border-color: rgba(111, 109, 245, .28);
            box-shadow: 0 14px 38px rgba(38, 35, 184, .08);
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
        .stButton > button[kind="primary"] {
            background: linear-gradient(105deg, #2623b8 0%, #5552ea 58%, #6f6df5 100%);
            border-color: #3a38d6;
            box-shadow: 0 10px 24px rgba(58, 56, 214, .2);
            color: #ffffff;
        }
        .stButton > button[kind="primary"]:hover {
            background: linear-gradient(105deg, #1b1894 0%, #3a38d6 56%, #5552ea 100%);
            border-color: #2623b8;
        }
        [data-testid="stSidebar"] .stDownloadButton > button {
            background: linear-gradient(105deg, rgba(255,255,255,.96) 0%, #c2c1fb 100%);
            border-color: rgba(255,255,255,.42);
            box-shadow: 0 10px 26px rgba(7, 6, 40, .2);
            color: #141173;
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


