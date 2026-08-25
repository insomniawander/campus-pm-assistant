import pandas as pd
import streamlit as st

from database.db import delete_project, list_projects
from styles import page_intro


def show(on_import=None):
    page_intro(
        "Portfolio",
        "从一个视角管理全部项目。",
        "查看每个项目的任务规模、完成情况，并维护不再需要的项目。",
    )
    projects = list_projects()
    if not projects:
        st.info("暂无项目，请先导入排期表。")
    else:
        frame = pd.DataFrame(projects)
        frame["完成率"] = frame.apply(lambda r: f"{int(100*r.completed_count/r.task_count)}%" if r.task_count else "0%", axis=1)
        st.dataframe(frame[["project_name", "status", "task_count", "completed_count", "完成率", "create_time"]], width="stretch", hide_index=True)
        names = {p["project_name"]: p["id"] for p in projects}
        with st.expander("删除项目", icon=":material/delete:"):
            selected = st.selectbox("选择项目", list(names))
            confirm = st.checkbox("我确认删除该项目及其全部任务")
            if st.button("删除项目", disabled=not confirm, icon=":material/delete:"):
                delete_project(names[selected])
                st.success("项目已删除")
                st.rerun()

    _, action = st.columns([5, 1])
    with action:
        st.button(
            "Import Excel",
            type="primary",
            icon=":material/upload_file:",
            width="stretch",
            on_click=on_import,
            disabled=on_import is None,
        )


