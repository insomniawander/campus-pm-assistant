import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "database", "campus_pm.db")


@contextmanager
def connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    with connection() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_name TEXT NOT NULL UNIQUE,
                company TEXT,
                owner TEXT,
                status TEXT DEFAULT '进行中',
                progress INTEGER DEFAULT 0,
                create_time TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                task_name TEXT NOT NULL,
                stage TEXT,
                owner TEXT,
                start_date TEXT,
                end_date TEXT,
                status TEXT DEFAULT '未开始',
                priority TEXT DEFAULT '普通',
                remark TEXT,
                source_file TEXT,
                source_sheet TEXT,
                task_key TEXT NOT NULL UNIQUE,
                original_start_date TEXT,
                original_end_date TEXT,
                update_time TEXT,
                FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
            );
            CREATE TABLE IF NOT EXISTS import_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_name TEXT,
                file_hash TEXT,
                project_name TEXT,
                import_time TEXT,
                task_count INTEGER,
                UNIQUE(file_hash, project_name)
            );
            CREATE TABLE IF NOT EXISTS task_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id INTEGER NOT NULL,
                action TEXT NOT NULL,
                old_value TEXT,
                new_value TEXT,
                reason TEXT,
                create_time TEXT NOT NULL,
                FOREIGN KEY(task_id) REFERENCES tasks(id) ON DELETE CASCADE
            );
            """
        )
        columns = {row[1] for row in conn.execute("PRAGMA table_info(tasks)")}
        for name, kind in [("source_file", "TEXT"), ("source_sheet", "TEXT"), ("task_key", "TEXT"),
                           ("original_start_date", "TEXT"), ("original_end_date", "TEXT"), ("update_time", "TEXT")]:
            if name not in columns:
                conn.execute(f"ALTER TABLE tasks ADD COLUMN {name} {kind}")
        conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_tasks_key ON tasks(task_key) WHERE task_key IS NOT NULL")


def get_or_create_project(project_name, company="", owner=""):
    with connection() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO projects(project_name, company, owner, create_time) VALUES (?, ?, ?, ?)",
            (project_name.strip(), company.strip(), owner.strip(), datetime.now().isoformat(timespec="seconds")),
        )
        row = conn.execute("SELECT id FROM projects WHERE project_name = ?", (project_name.strip(),)).fetchone()
        return row[0]


def import_tasks(project_name, tasks, file_name, file_hash, strategy="skip"):
    project_id = get_or_create_project(project_name)
    inserted = 0
    with connection() as conn:
        if strategy == "overwrite":
            conn.execute("DELETE FROM tasks WHERE project_id=?", (project_id,))
        for task in tasks:
            now = datetime.now().isoformat(timespec="seconds")
            values = (
                project_id, task["task_name"], task.get("stage", ""), task.get("owner", ""),
                task.get("start_date"), task.get("end_date"), task.get("status", "未开始"),
                task.get("priority", "普通"), task.get("remark", ""), file_name,
                task.get("source_sheet", ""), task["task_key"], task.get("start_date"),
                task.get("end_date"), now,
            )
            if strategy == "update":
                existing = conn.execute("SELECT id FROM tasks WHERE task_key=?", (task["task_key"],)).fetchone()
                if existing:
                    cur = conn.execute("""UPDATE tasks SET stage=?, owner=?, start_date=?, end_date=?,
                        status=?, priority=?, remark=?, source_file=?, source_sheet=?, update_time=? WHERE id=?""",
                        (task.get("stage", ""), task.get("owner", ""), task.get("start_date"), task.get("end_date"),
                         task.get("status", "未开始"), task.get("priority", "普通"), task.get("remark", ""),
                         file_name, task.get("source_sheet", ""), now, existing[0]))
                else:
                    cur = conn.execute("""INSERT INTO tasks
                        (project_id, task_name, stage, owner, start_date, end_date, status, priority,
                         remark, source_file, source_sheet, task_key, original_start_date, original_end_date, update_time)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", values)
            else:
                cur = conn.execute(
                """INSERT OR IGNORE INTO tasks
                (project_id, task_name, stage, owner, start_date, end_date, status, priority,
                 remark, source_file, source_sheet, task_key, original_start_date, original_end_date, update_time)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", values)
            inserted += cur.rowcount
        conn.execute(
            """INSERT INTO import_records(file_name, file_hash, project_name, import_time, task_count)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(file_hash, project_name) DO UPDATE SET
            import_time=excluded.import_time, task_count=excluded.task_count""",
            (file_name, file_hash, project_name, datetime.now().isoformat(timespec="seconds"), inserted),
        )
    return inserted


def query_tasks(project_id=None, status=None):
    sql = """SELECT t.*, p.project_name FROM tasks t
             JOIN projects p ON p.id=t.project_id WHERE 1=1"""
    args = []
    if project_id:
        sql += " AND t.project_id=?"
        args.append(project_id)
    if status:
        sql += " AND t.status=?"
        args.append(status)
    sql += " ORDER BY COALESCE(t.end_date, '9999-12-31'), t.id"
    with connection() as conn:
        return [dict(row) for row in conn.execute(sql, args).fetchall()]


def list_projects():
    with connection() as conn:
        return [dict(row) for row in conn.execute(
            """SELECT p.*, COUNT(t.id) task_count,
            SUM(CASE WHEN t.status='已完成' THEN 1 ELSE 0 END) completed_count
            FROM projects p LEFT JOIN tasks t ON t.project_id=p.id
            GROUP BY p.id ORDER BY p.create_time DESC"""
        ).fetchall()]


def update_task_status(task_id, status):
    with connection() as conn:
        old = conn.execute("SELECT status FROM tasks WHERE id=?", (task_id,)).fetchone()
        conn.execute("UPDATE tasks SET status=? WHERE id=?", (status, task_id))
        if old and old[0] != status:
            _add_history(conn, task_id, "修改状态", old[0], status, "")


def bulk_update_status(task_ids, status):
    for task_id in task_ids:
        update_task_status(task_id, status)


def _add_history(conn, task_id, action, old_value, new_value, reason=""):
    conn.execute("""INSERT INTO task_history(task_id, action, old_value, new_value, reason, create_time)
                    VALUES (?, ?, ?, ?, ?, ?)""",
                 (task_id, action, old_value, new_value, reason, datetime.now().isoformat(timespec="seconds")))


def create_task(project_id, task):
    now = datetime.now().isoformat(timespec="seconds")
    with connection() as conn:
        cur = conn.execute("""INSERT INTO tasks
            (project_id, task_name, stage, owner, start_date, end_date, status, priority, remark,
             source_file, source_sheet, task_key, original_start_date, original_end_date, update_time)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, '', '', ?, ?, ?, ?)""",
            (project_id, task["task_name"], task.get("stage", ""), task.get("owner", ""),
             task.get("start_date"), task.get("end_date"), task.get("status", "未开始"),
             task.get("priority", "普通"), task.get("remark", ""), task["task_key"],
             task.get("start_date"), task.get("end_date"), now))
        _add_history(conn, cur.lastrowid, "新增任务", "", task["task_name"], "")
        return cur.lastrowid


def update_task(task_id, task, reason=""):
    with connection() as conn:
        old = conn.execute("SELECT * FROM tasks WHERE id=?", (task_id,)).fetchone()
        if not old:
            return
        conn.execute("""UPDATE tasks SET task_name=?, stage=?, owner=?, start_date=?, end_date=?,
            status=?, priority=?, remark=?, task_key=?, update_time=? WHERE id=?""",
            (task["task_name"], task.get("stage", ""), task.get("owner", ""), task.get("start_date"),
             task.get("end_date"), task.get("status", "未开始"), task.get("priority", "普通"),
             task.get("remark", ""), task["task_key"], datetime.now().isoformat(timespec="seconds"), task_id))
        if old["start_date"] != task.get("start_date"):
            _add_history(conn, task_id, "修改开始日期", old["start_date"], task.get("start_date"), reason)
        if old["end_date"] != task.get("end_date"):
            action = "延长截止日期" if old["end_date"] and task.get("end_date") and task["end_date"] > old["end_date"] else "修改截止日期"
            _add_history(conn, task_id, action, old["end_date"], task.get("end_date"), reason)
        for field, label in [("task_name", "任务名称"), ("stage", "阶段"), ("owner", "负责人"), ("status", "状态"), ("priority", "优先级"), ("remark", "备注")]:
            if old[field] != task.get(field, ""):
                _add_history(conn, task_id, f"修改{label}", old[field], task.get(field, ""), reason)


def delete_task(task_id):
    with connection() as conn:
        conn.execute("DELETE FROM tasks WHERE id=?", (task_id,))


def task_history(task_id):
    with connection() as conn:
        return [dict(row) for row in conn.execute(
            "SELECT * FROM task_history WHERE task_id=? ORDER BY id DESC", (task_id,)).fetchall()]


def delete_project(project_id):
    with connection() as conn:
        conn.execute("DELETE FROM projects WHERE id=?", (project_id,))

