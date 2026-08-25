import streamlit as st
from datetime import date

from database.db import init_db, list_projects, query_tasks
from pages.dashboard import show as show_dashboard
from pages.import_excel import show as show_import
from pages.project_manager import show as show_projects
from pages.task_manager import show as show_tasks
from services.exporter import build_export_workbook
from styles import apply_app_style, sidebar_brand


NAV_ITEMS = ("Daily Work", "Task Management", "Project Management")


def navigate(page):
    st.session_state.current_page = page


def sync_sidebar_navigation():
    navigate(st.session_state.sidebar_navigation)


st.set_page_config(
    page_title="Campus PM Assistant",
    page_icon=":material/calendar_month:",
    layout="wide",
    initial_sidebar_state="expanded",
)
apply_app_style()
init_db()

if "current_page" not in st.session_state:
    st.session_state.current_page = NAV_ITEMS[0]
if "sidebar_navigation" not in st.session_state:
    st.session_state.sidebar_navigation = NAV_ITEMS[0]

with st.sidebar:
    sidebar_brand()
    st.radio(
        "Navigation",
        NAV_ITEMS,
        label_visibility="collapsed",
        key="sidebar_navigation",
        on_change=sync_sidebar_navigation,
    )
    st.download_button(
        "Export Data",
        data=build_export_workbook(list_projects(), query_tasks()),
        file_name=f"campus-projects-{date.today().isoformat()}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        icon=":material/download:",
        width="stretch",
    )

page = st.session_state.current_page
if page == "Excel Import":
    if st.button(
        "Back to Project Management",
        icon=":material/arrow_back:",
        on_click=navigate,
        args=("Project Management",),
    ):
        pass
    show_import()
elif page == "Task Management":
    show_tasks()
elif page == "Project Management":
    show_projects(on_import=lambda: navigate("Excel Import"))
else:
    show_dashboard()

# Deployment refresh: 2026-08-25 16:15 CST
