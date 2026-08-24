from datetime import date

import pandas as pd
import streamlit as st

from database.db import import_tasks
from services.excel_parser import build_task_key, file_hash, list_sheets, parse_workbook


def show():
    st.header("📥 Excel 智能导入")
    project_name = st.text_input("项目名称（必填）")
    year = st.number_input("排期年份", min_value=2020, max_value=2100, value=date.today().year)
    uploaded = st.file_uploader("上传 Excel 排期表", type=["xlsx", "xlsm"])
    if not uploaded:
        return
    content = uploaded.getvalue()
    try:
        st.write("工作表：", "、".join(list_sheets(content)))
        tasks = parse_workbook(content, project_name.strip() or "预览项目", int(year))
    except Exception as exc:
        st.error(f"解析失败：{exc}")
        return
    if not tasks:
        st.warning("没有识别到任务。请检查表头，或在任务名称、日期等字段附近减少合并单元格。")
        return
    preview = pd.DataFrame(tasks).drop(columns=["task_key"], errors="ignore")
    st.success(f"识别到 {len(tasks)} 项任务")
    st.caption("可直接修改识别结果，也可以删除不需要导入的行。")
    edited = st.data_editor(preview, width="stretch", hide_index=True, num_rows="dynamic")
    strategy_label = st.radio("重复上传处理方式", ["跳过重复任务", "更新已有任务", "覆盖该项目全部任务"], horizontal=True)
    strategy = {"跳过重复任务": "skip", "更新已有任务": "update", "覆盖该项目全部任务": "overwrite"}[strategy_label]
    if st.button("确认导入数据库", type="primary", disabled=not project_name.strip()):
        edited_tasks = edited.where(pd.notna(edited), None).to_dict("records")
        edited_tasks = [t for t in edited_tasks if str(t.get("task_name") or "").strip()]
        for task in edited_tasks:
            task["task_name"] = str(task["task_name"]).strip()
            task["task_key"] = build_task_key(project_name.strip(), task)
        count = import_tasks(project_name.strip(), edited_tasks, uploaded.name, file_hash(content), strategy)
        if count:
            st.success(f"成功处理 {count} 项任务。")
        else:
            st.info("没有新增任务，该项目中的这些任务可能已经导入。")

