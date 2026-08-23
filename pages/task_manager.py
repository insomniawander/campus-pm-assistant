from datetime import date

import pandas as pd
import streamlit as st

from database.db import (bulk_update_status, create_task, delete_task, list_projects,
                         query_tasks, task_history, update_task)
from services.excel_parser import build_task_key

STATUSES = ["未开始", "进行中", "已完成", "延期"]
PRIORITIES = ["普通", "重要", "紧急"]


def _iso(value):
    return value.isoformat() if value else None


def _date_value(value):
    return date.fromisoformat(value) if value else None


def _task_form(prefix, project_name, task=None):
    task = task or {}
    name = st.text_input("任务名称", task.get("task_name", ""), key=f"{prefix}_name")
    col1, col2 = st.columns(2)
    stage = col1.text_input("阶段/模块", task.get("stage", ""), key=f"{prefix}_stage")
    owner = col2.text_input("负责人", task.get("owner", ""), key=f"{prefix}_owner")
    start = col1.date_input("开始日期", value=_date_value(task.get("start_date")), key=f"{prefix}_start")
    end = col2.date_input("截止日期", value=_date_value(task.get("end_date")), key=f"{prefix}_end")
    status = col1.selectbox("状态", STATUSES, index=STATUSES.index(task.get("status", "未开始")), key=f"{prefix}_status")
    priority = col2.selectbox("优先级", PRIORITIES, index=PRIORITIES.index(task.get("priority", "普通")), key=f"{prefix}_priority")
    remark = st.text_area("备注", task.get("remark", ""), key=f"{prefix}_remark")
    result = {"task_name": name.strip(), "stage": stage.strip(), "owner": owner.strip(),
              "start_date": _iso(start), "end_date": _iso(end), "status": status,
              "priority": priority, "remark": remark.strip()}
    result["task_key"] = build_task_key(project_name, result)
    return result


def show():
    st.header("✅ 任务管理")
    projects = list_projects()
    if not projects:
        st.info("暂无项目，请先导入 Excel。")
        return
    project_map = {p["project_name"]: p["id"] for p in projects}
    col1, col2, col3 = st.columns(3)
    project_filter = col1.selectbox("项目筛选", ["全部项目"] + list(project_map))
    owners = sorted({t.get("owner", "") for t in query_tasks() if t.get("owner")})
    owner_filter = col2.selectbox("负责人筛选", ["全部负责人"] + owners)
    status_filter = col3.selectbox("状态筛选", ["全部状态"] + STATUSES)
    tasks = query_tasks(project_map.get(project_filter), None if status_filter == "全部状态" else status_filter)
    if owner_filter != "全部负责人":
        tasks = [t for t in tasks if t.get("owner") == owner_filter]

    labels = {f"#{t['id']}｜{t['project_name']}｜{t['task_name']}": t for t in tasks}
    selected_labels = st.multiselect("选择任务（可批量修改状态）", list(labels))
    b1, b2 = st.columns([2, 1])
    bulk_status = b1.selectbox("批量设置状态", STATUSES, key="bulk_status")
    if b2.button("应用到选中任务", disabled=not selected_labels):
        bulk_update_status([labels[x]["id"] for x in selected_labels], bulk_status)
        st.success("批量状态已更新")
        st.rerun()

    if tasks:
        frame = pd.DataFrame(tasks)
        st.dataframe(frame[["id", "project_name", "task_name", "stage", "owner", "start_date", "end_date", "status", "priority"]],
                     use_container_width=True, hide_index=True)
    else:
        st.info("当前筛选条件下没有任务。")

    with st.expander("➕ 新增单个任务"):
        project_name = st.selectbox("所属项目", list(project_map), key="new_project")
        new_task = _task_form("new", project_name)
        if st.button("新增任务", disabled=not new_task["task_name"]):
            create_task(project_map[project_name], new_task)
            st.success("任务已新增")
            st.rerun()

    if labels:
        with st.expander("✏️ 编辑、延期或删除任务"):
            selected_label = st.selectbox("选择任务", list(labels), key="edit_select")
            selected = labels[selected_label]
            edited = _task_form("edit", selected["project_name"], selected)
            reason = st.text_input("修改/延期原因（修改日期时建议填写）")
            c1, c2 = st.columns(2)
            if c1.button("保存修改", type="primary", disabled=not edited["task_name"]):
                update_task(selected["id"], edited, reason)
                st.success("任务已更新，日期变更已记录到历史。")
                st.rerun()
            confirm = c2.checkbox("确认删除", key="delete_confirm")
            if c2.button("删除任务", disabled=not confirm):
                delete_task(selected["id"])
                st.success("任务已删除")
                st.rerun()
            history = task_history(selected["id"])
            st.subheader("变更与延期历史")
            if history:
                st.dataframe(pd.DataFrame(history)[["action", "old_value", "new_value", "reason", "create_time"]], hide_index=True, use_container_width=True)
            else:
                st.caption("暂无变更记录。")

