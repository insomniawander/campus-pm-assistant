from datetime import date
from pathlib import Path

import pandas as pd
import streamlit as st

from database.db import import_tasks
from services.excel_parser import build_task_key, file_hash, list_sheets, parse_workbook
from styles import page_intro


def default_project_name(filename):
    return Path(filename).stem.strip()


def _edited_tasks(frame, project_name):
    tasks = frame.where(pd.notna(frame), None).to_dict("records")
    tasks = [task for task in tasks if str(task.get("task_name") or "").strip()]
    for task in tasks:
        task["task_name"] = str(task["task_name"]).strip()
        task["task_key"] = build_task_key(project_name, task)
    return tasks


def show():
    page_intro(
        "Smart import",
        "把排期表变成可执行任务。",
        "一次上传多个项目文件，检查识别结果后统一写入任务库。",
    )
    uploaded_files = st.file_uploader(
        "上传 Excel 排期表",
        type=["xlsx", "xlsm"],
        accept_multiple_files=True,
        key="batch_excel_upload",
    )
    if not uploaded_files:
        st.info(
            "可一次选择多个 Excel；系统会默认使用文件名作为项目名称。",
            icon=":material/upload_file:",
        )
        return

    defaults = pd.DataFrame({
        "文件名": [uploaded.name for uploaded in uploaded_files],
        "项目名称": [default_project_name(uploaded.name) for uploaded in uploaded_files],
        "排期年份": [date.today().year] * len(uploaded_files),
    })
    st.subheader("确认项目信息", anchor=False)
    project_settings = st.data_editor(
        defaults,
        key="batch_project_settings",
        width="stretch",
        hide_index=True,
        disabled=["文件名"],
        num_rows="fixed",
        column_config={
            "项目名称": st.column_config.TextColumn("项目名称", required=True),
            "排期年份": st.column_config.NumberColumn(
                "排期年份", min_value=2020, max_value=2100, step=1, format="%d", required=True
            ),
        },
    )

    strategy_label = st.segmented_control(
        "重复上传处理方式",
        ["跳过重复任务", "更新已有任务", "覆盖该项目全部任务"],
        default="跳过重复任务",
        key="batch_import_strategy",
    )
    strategy = {
        "跳过重复任务": "skip",
        "更新已有任务": "update",
        "覆盖该项目全部任务": "overwrite",
    }[strategy_label]

    batch = []
    failures = []
    for index, uploaded in enumerate(uploaded_files):
        project_value = project_settings.iloc[index]["项目名称"]
        year_value = project_settings.iloc[index]["排期年份"]
        project_name = "" if pd.isna(project_value) else str(project_value).strip()
        year = date.today().year if pd.isna(year_value) else int(year_value)
        content = uploaded.getvalue()
        digest = file_hash(content)
        with st.expander(
            f"{uploaded.name} → {project_name or '请填写项目名称'}",
            expanded=len(uploaded_files) == 1,
            icon=":material/table_view:",
        ):
            try:
                sheets = list_sheets(content)
                tasks = parse_workbook(content, project_name or "预览项目", year)
            except Exception as exc:
                st.error(f"解析失败：{exc}")
                failures.append(uploaded.name)
                continue
            st.caption("工作表：" + "、".join(sheets))
            if not tasks:
                st.warning("没有识别到任务。请检查表头，或在任务名称、日期等字段附近减少合并单元格。")
                failures.append(uploaded.name)
                continue
            st.success(f"识别到 {len(tasks)} 项任务")
            st.caption("可直接修改识别结果，也可以删除不需要导入的行。")
            preview = pd.DataFrame(tasks).drop(columns=["task_key"], errors="ignore")
            edited = st.data_editor(
                preview,
                key=f"preview_{digest[:12]}_{index}",
                width="stretch",
                hide_index=True,
                num_rows="dynamic",
            )
            batch.append({
                "uploaded": uploaded,
                "content": content,
                "digest": digest,
                "project_name": project_name,
                "tasks": _edited_tasks(edited, project_name),
            })

    invalid_names = [item["uploaded"].name for item in batch if not item["project_name"]]
    if invalid_names:
        st.error("请为这些文件填写项目名称：" + "、".join(invalid_names))
    if failures:
        st.warning("以下文件暂不能导入：" + "、".join(failures))

    ready = [item for item in batch if item["project_name"] and item["tasks"]]
    if st.button(
        f"确认导入全部文件（{len(ready)} 个）",
        type="primary",
        disabled=not ready or bool(invalid_names),
        icon=":material/database_upload:",
    ):
        total = 0
        results = []
        overwritten_projects = set()
        for item in ready:
            item_strategy = strategy
            if strategy == "overwrite" and item["project_name"] in overwritten_projects:
                item_strategy = "update"
            count = import_tasks(
                item["project_name"], item["tasks"], item["uploaded"].name,
                item["digest"], item_strategy,
            )
            overwritten_projects.add(item["project_name"])
            total += count
            results.append(f"{item['project_name']}：{count} 项")
        st.success(f"批量导入完成，共处理 {total} 项任务。")
        st.write("；".join(results))

