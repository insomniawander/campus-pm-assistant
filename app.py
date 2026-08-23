import streamlit as st

from database.db import init_db
from pages.dashboard import show as show_dashboard
from pages.import_excel import show as show_import
from pages.project_manager import show as show_projects
from pages.task_manager import show as show_tasks

st.set_page_config(page_title="Campus Recruitment PM Assistant", page_icon="📅", layout="wide")
init_db()
st.title("Campus Recruitment PM Assistant")
st.caption("不同项目 Excel → 统一任务库 → 每日待办与截止提醒")

menu = st.sidebar.radio("功能导航", ["每日工作台", "Excel智能导入", "任务管理", "多项目管理"])
{"每日工作台": show_dashboard, "Excel智能导入": show_import, "任务管理": show_tasks, "多项目管理": show_projects}[menu]()

