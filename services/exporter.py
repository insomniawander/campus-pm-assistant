from io import BytesIO

import pandas as pd


PROJECT_COLUMNS = {
    "id": "Project ID",
    "project_name": "Project Name",
    "company": "Company",
    "owner": "Owner",
    "status": "Status",
    "progress": "Progress",
    "task_count": "Task Count",
    "completed_count": "Completed Count",
    "create_time": "Created At",
}

TASK_COLUMNS = {
    "id": "Task ID",
    "project_name": "Project Name",
    "task_name": "Task Name",
    "stage": "Stage",
    "owner": "Owner",
    "start_date": "Start Date",
    "end_date": "End Date",
    "status": "Status",
    "priority": "Priority",
    "remark": "Remark",
    "source_file": "Source File",
    "source_sheet": "Source Sheet",
    "update_time": "Updated At",
}


def _export_frame(records, columns):
    frame = pd.DataFrame(records)
    return frame.reindex(columns=columns).rename(columns=columns)


def build_export_workbook(projects, tasks):
    """Return an Excel workbook containing user-facing project and task data."""
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        _export_frame(projects, PROJECT_COLUMNS).to_excel(
            writer, sheet_name="Projects", index=False
        )
        _export_frame(tasks, TASK_COLUMNS).to_excel(
            writer, sheet_name="Tasks", index=False
        )
    return output.getvalue()

