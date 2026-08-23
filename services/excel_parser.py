import hashlib
import re
from datetime import date, datetime
from io import BytesIO

import pandas as pd

from services.field_matcher import find_header_row, match_fields


def list_sheets(source):
    return pd.ExcelFile(BytesIO(source) if isinstance(source, bytes) else source, engine="openpyxl").sheet_names


def read_sheet(source, sheet_name, header=None):
    source = BytesIO(source) if isinstance(source, bytes) else source
    return pd.read_excel(source, sheet_name=sheet_name, header=header, engine="openpyxl")


def read_excel(source):
    for sheet in list_sheets(source):
        df = read_sheet(source, sheet, header=None)
        if not clean_dataframe(df).empty:
            return df, sheet
    return None, None


def clean_dataframe(df):
    return df.dropna(how="all").dropna(axis=1, how="all").reset_index(drop=True)


def sheet_summary(df):
    cleaned = clean_dataframe(df)
    return {"rows": int(cleaned.shape[0]), "columns": int(cleaned.shape[1]), "non_empty_cells": int(cleaned.notna().sum().sum())}


def file_hash(content):
    return hashlib.sha256(content).hexdigest()


def _date_text(value, year):
    if value is None or pd.isna(value) or str(value).strip() in {"", "待定", "nan", "NaT"}:
        return None, None
    if isinstance(value, (pd.Timestamp, datetime, date)):
        text = pd.Timestamp(value).date().isoformat()
        return text, text
    text = str(value).strip().replace("—", "-").replace("至", "-")
    parsed = pd.to_datetime(text, errors="coerce")
    if not pd.isna(parsed) and re.search(r"\d{4}", text):
        result = parsed.date().isoformat()
        return result, result
    match = re.search(r"(\d{1,2})月(\d{1,2})(?:日)?\s*-\s*(?:(\d{1,2})月)?(\d{1,2})日?", text)
    if match:
        month, day1, month2, day2 = map(lambda x: int(x) if x else None, match.groups())
        return date(year, month, day1).isoformat(), date(year, month2 or month, day2).isoformat()
    match = re.search(r"(\d{1,2})月(\d{1,2})日?", text)
    if match:
        result = date(year, int(match.group(1)), int(match.group(2))).isoformat()
        return result, result
    return None, None


def _status(value):
    text = str(value).strip()
    if text in {"已完成", "完成", "100%", "已结束"}:
        return "已完成"
    if text in {"进行中", "执行中", "处理中"}:
        return "进行中"
    if text in {"延期", "已延期"}:
        return "延期"
    return "未开始"


def build_task_key(project_name, task):
    raw = "|".join(str(task.get(k) or "").strip() for k in ["task_name", "stage", "owner", "start_date", "end_date"])
    return hashlib.sha256(f"{project_name}|{raw}".encode("utf-8")).hexdigest()


def _standard_sheet(df, sheet, project_name, year):
    cleaned = clean_dataframe(df)
    header_index, _ = find_header_row(cleaned)
    if header_index < 0:
        return []
    headers = [str(v).strip() for v in cleaned.iloc[header_index].tolist()]
    mapping = match_fields(headers)
    if "task_name" not in mapping.values():
        return []
    data = cleaned.iloc[header_index + 1:].copy()
    data.columns = headers
    tasks = []
    for _, row in data.iterrows():
        normalized = {system: row[original] for original, system in mapping.items()}
        name = str(normalized.get("task_name", "")).strip()
        if not name or name.lower() == "nan" or re.match(r"^共\s*\d+\s*项$", name):
            continue
        start1, start2 = _date_text(normalized.get("start_date"), year)
        end1, end2 = _date_text(normalized.get("end_date"), year)
        task = {
            "task_name": name, "stage": str(normalized.get("stage", "")).strip(),
            "owner": str(normalized.get("owner", "")).strip(), "start_date": start1 or end1,
            "end_date": end2 or end1 or start2, "status": _status(normalized.get("status")),
            "remark": str(normalized.get("remark", "")).strip(), "source_sheet": sheet,
        }
        for key in ["stage", "owner", "remark"]:
            if task[key].lower() == "nan": task[key] = ""
        task["task_key"] = build_task_key(project_name, task)
        tasks.append(task)
    return tasks


def _three_column_sheet(df, sheet, project_name, year):
    cleaned = clean_dataframe(df).ffill(axis=0, limit=20)
    tasks = []
    for _, row in cleaned.iterrows():
        values = [v for v in row.tolist() if not pd.isna(v)]
        if len(values) < 2:
            continue
        date_index = next((i for i, v in enumerate(values) if re.search(r"\d{1,2}月\d{1,2}", str(v))), None)
        if date_index is None:
            continue
        start, end = _date_text(values[date_index], year)
        following = values[date_index + 1:]
        if not following:
            continue
        name = str(following[-1]).strip()
        if not name or name in {"事项", "工作事项"}:
            continue
        task = {"task_name": name, "stage": str(following[0]).strip() if len(following) > 1 else "",
                "owner": "", "start_date": start, "end_date": end, "status": "未开始",
                "remark": "", "source_sheet": sheet}
        task["task_key"] = build_task_key(project_name, task)
        tasks.append(task)
    return tasks


def parse_workbook(content, project_name, year=None):
    year = year or date.today().year
    sheets = list_sheets(content)
    preferred = [s for s in sheets if "每日详情" in s]
    targets = preferred or [s for s in sheets if "排期" in s] or sheets
    tasks = []
    for sheet in targets:
        df = read_sheet(content, sheet, header=None)
        parsed = _standard_sheet(df, sheet, project_name, year)
        if not parsed and ("项目排期" in sheet or len(clean_dataframe(df).columns) <= 5):
            parsed = _three_column_sheet(df, sheet, project_name, year)
        tasks.extend(parsed)
    unique = {task["task_key"]: task for task in tasks}
    return list(unique.values())

