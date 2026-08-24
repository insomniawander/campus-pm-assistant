import streamlit as st

from database.db import init_db
from pages.dashboard import show as show_dashboard
from pages.import_excel import show as show_import
from pages.gantt import show as show_gantt
from pages.project_manager import show as show_projects
from pages.task_manager import show as show_tasks
from styles import apply_app_style, sidebar_brand

st.set_page_config(
    page_title="Campus PM Assistant",
    page_icon=":material/calendar_month:",
    layout="wide",
    initial_sidebar_state="expanded",
)
apply_app_style()
init_db()

with st.sidebar:
    sidebar_brand()
    menu = st.radio(
        "功能导航",
        ["每日工作台", "Excel 智能导入", "任务管理", "项目甘特图", "多项目管理"],
        label_visibility="collapsed",
    )
    st.caption("Excel 排期 · 待办提醒 · 项目协同")

{"每日工作台": show_dashboard, "Excel智能导入": show_import, "任务管理": show_tasks,
 "Excel 智能导入": show_import, "项目甘特图": show_gantt,
 "多项目管理": show_projects}[menu]()

