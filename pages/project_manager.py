import pandas as pd
import streamlit as st

from database.db import delete_project, list_projects


def show():
    st.header("📁 多项目管理")
    projects = list_projects()
    if not projects:
        st.info("暂无项目，请先导入排期表。")
        return
    frame = pd.DataFrame(projects)
    frame["完成率"] = frame.apply(lambda r: f"{int(100*r.completed_count/r.task_count)}%" if r.task_count else "0%", axis=1)
    st.dataframe(frame[["project_name", "status", "task_count", "completed_count", "完成率", "create_time"]], use_container_width=True, hide_index=True)
    names = {p["project_name"]: p["id"] for p in projects}
    with st.expander("删除项目"):
        selected = st.selectbox("选择项目", list(names))
        confirm = st.checkbox("我确认删除该项目及其全部任务")
        if st.button("删除项目", disabled=not confirm):
            delete_project(names[selected])
            st.success("项目已删除")
            st.rerun()

