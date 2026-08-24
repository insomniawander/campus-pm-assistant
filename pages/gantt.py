import pandas as pd
import streamlit as st

from database.db import list_projects, query_tasks


def gantt_rows(tasks):
    rows = []
    for task in tasks:
        start = pd.to_datetime(task.get("start_date"), errors="coerce")
        end = pd.to_datetime(task.get("end_date"), errors="coerce")
        if pd.isna(start) and pd.isna(end):
            continue
        if pd.isna(start):
            start = end
        if pd.isna(end):
            end = start
        if end < start:
            start, end = end, start
        rows.append({
            "项目": task["project_name"],
            "任务": task["task_name"],
            "阶段": task.get("stage") or "未分类",
            "负责人": task.get("owner") or "未指定",
            "状态": task.get("status") or "未开始",
            "开始日期": start,
            "截止日期": end + pd.Timedelta(days=1),
            "显示截止日期": end.strftime("%Y-%m-%d"),
        })
    return pd.DataFrame(rows)


def show():
    st.header("📊 项目甘特图")
    projects = list_projects()
    project_options = {"全部项目": None, **{p["project_name"]: p["id"] for p in projects}}
    project_name = st.selectbox("项目筛选", list(project_options), key="gantt_project")
    tasks = query_tasks(project_options[project_name])
    owners = sorted({task.get("owner") for task in tasks if task.get("owner")})
    owner = st.selectbox("负责人筛选", ["全部负责人"] + owners, key="gantt_owner")
    if owner != "全部负责人":
        tasks = [task for task in tasks if task.get("owner") == owner]

    frame = gantt_rows(tasks)
    if frame.empty:
        st.info("暂无带日期的任务，请先导入排期或为任务设置开始、截止日期。")
        return

    st.vega_lite_chart(
        frame,
        {
            "height": {"step": 30},
            "mark": {"type": "bar", "cornerRadius": 4, "tooltip": True},
            "encoding": {
                "y": {"field": "任务", "type": "nominal", "sort": {"field": "开始日期"}, "title": None},
                "x": {"field": "开始日期", "type": "temporal", "title": "日期", "axis": {"format": "%m-%d"}},
                "x2": {"field": "截止日期"},
                "color": {"field": "项目", "type": "nominal", "title": "项目"},
                "opacity": {"condition": {"test": "datum['状态'] === '已完成'", "value": 0.45}, "value": 0.9},
                "tooltip": [
                    {"field": "项目", "type": "nominal"}, {"field": "任务", "type": "nominal"},
                    {"field": "阶段", "type": "nominal"}, {"field": "负责人", "type": "nominal"},
                    {"field": "状态", "type": "nominal"},
                    {"field": "开始日期", "type": "temporal", "format": "%Y-%m-%d"},
                    {"field": "显示截止日期", "type": "nominal", "title": "截止日期"},
                ],
            },
        },
        width="stretch",
    )

    st.dataframe(
        frame[["项目", "任务", "阶段", "负责人", "状态", "开始日期", "显示截止日期"]],
        width="stretch",
        hide_index=True,
    )

