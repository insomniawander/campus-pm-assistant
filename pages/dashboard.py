from datetime import date

import pandas as pd
import streamlit as st

from database.db import query_tasks
from services.reminder import classify_tasks


def _frame(tasks):
    if not tasks:
        return pd.DataFrame(columns=["项目", "任务", "阶段", "负责人", "开始", "截止", "状态"])
    return pd.DataFrame([{
        "项目": t["project_name"], "任务": t["task_name"], "阶段": t.get("stage", ""),
        "负责人": t.get("owner", ""), "开始": t.get("start_date", ""),
        "截止": t.get("end_date", ""), "状态": t.get("status", ""),
    } for t in tasks])


def show():
    st.header(f"📅 {date.today():%Y年%m月%d日} 每日工作台")
    groups = classify_tasks(query_tasks())
    cols = st.columns(4)
    cols[0].metric("今日待办", len(groups["today"]))
    cols[1].metric("3天内截止", len(groups["soon"]))
    cols[2].metric("已逾期", len(groups["overdue"]))
    cols[3].metric("本周任务", len(groups["week"]))
    tabs = st.tabs(["今日待办", "3天内截止", "已逾期", "本周", "日期待定"])
    for tab, key in zip(tabs, ["today", "soon", "overdue", "week", "undated"]):
        with tab:
            st.dataframe(_frame(groups[key]), use_container_width=True, hide_index=True)

