import os
import sys
import tempfile
import unittest
from datetime import date
from io import BytesIO
from pathlib import Path

import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_DIR))

from services.excel_parser import parse_workbook
from services.reminder import classify_tasks
import database.db as db
from services.excel_parser import build_task_key


class V1Tests(unittest.TestCase):
    def workbook(self, sheets):
        output = BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            for name, data in sheets.items():
                pd.DataFrame(data).to_excel(writer, sheet_name=name, header=False, index=False)
        return output.getvalue()

    def test_daily_detail_is_preferred_and_mapped(self):
        content = self.workbook({"8月": [["日历", "重复"]], "每日详情": [
            ["阶段", "明细", "执行方", "开始", "截止"],
            ["宣传", "发布推文", "小王", "2026-08-22", "2026-08-24"],
            ["宣传", "共7项", "", "", ""],
        ]})
        tasks = parse_workbook(content, "芯港", 2026)
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]["task_name"], "发布推文")
        self.assertEqual(tasks[0]["owner"], "小王")

    def test_three_column_date_range(self):
        content = self.workbook({"项目排期": [["日期", "模块", "事项"], ["8月25-30日", "宣传", "推文发布"]]})
        tasks = parse_workbook(content, "人才汇", 2026)
        self.assertEqual(tasks[0]["start_date"], "2026-08-25")
        self.assertEqual(tasks[0]["end_date"], "2026-08-30")

    def test_reminders(self):
        tasks = [
            {"task_name": "今日", "start_date": None, "end_date": "2026-08-22", "status": "未开始"},
            {"task_name": "临期", "start_date": None, "end_date": "2026-08-24", "status": "未开始"},
            {"task_name": "逾期", "start_date": None, "end_date": "2026-08-20", "status": "进行中"},
        ]
        groups = classify_tasks(tasks, date(2026, 8, 22))
        self.assertEqual([t["task_name"] for t in groups["today"]], ["今日"])
        self.assertEqual([t["task_name"] for t in groups["soon"]], ["临期"])
        self.assertEqual([t["task_name"] for t in groups["overdue"]], ["逾期"])

    def test_crud_extension_history_and_bulk_status(self):
        test_path = PROJECT_DIR / "tests" / "_v11_test.db"
        if test_path.exists():
            test_path.unlink()
        old_path = db.DB_PATH
        db.DB_PATH = str(test_path)
        try:
            db.init_db()
            project_id = db.get_or_create_project("测试项目")
            task = {"task_name": "确认名单", "stage": "准备", "owner": "小王",
                    "start_date": "2026-08-20", "end_date": "2026-08-22",
                    "status": "未开始", "priority": "普通", "remark": ""}
            task["task_key"] = build_task_key("测试项目", task)
            task_id = db.create_task(project_id, task)
            task["end_date"] = "2026-08-25"
            task["task_key"] = build_task_key("测试项目", task)
            db.update_task(task_id, task, "客户延期确认")
            history = db.task_history(task_id)
            self.assertEqual(history[0]["action"], "延长截止日期")
            self.assertEqual(history[0]["reason"], "客户延期确认")
            db.bulk_update_status([task_id], "进行中")
            self.assertEqual(db.query_tasks()[0]["status"], "进行中")
            db.delete_task(task_id)
            self.assertEqual(db.query_tasks(), [])
        finally:
            db.DB_PATH = old_path
            if test_path.exists():
                test_path.unlink()


if __name__ == "__main__":
    unittest.main()

