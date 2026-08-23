from datetime import date, timedelta


def classify_tasks(tasks, today=None):
    today = today or date.today()
    groups = {"today": [], "soon": [], "overdue": [], "week": [], "undated": []}
    week_end = today + timedelta(days=6 - today.weekday())
    for task in tasks:
        if task.get("status") == "已完成":
            continue
        try:
            start = date.fromisoformat(task["start_date"]) if task.get("start_date") else None
            end = date.fromisoformat(task["end_date"]) if task.get("end_date") else None
        except ValueError:
            groups["undated"].append(task)
            continue
        due = end or start
        if not due:
            groups["undated"].append(task)
        elif due < today:
            groups["overdue"].append(task)
        elif due == today or (start and start <= today <= due):
            groups["today"].append(task)
        elif today < due <= today + timedelta(days=3):
            groups["soon"].append(task)
        if due and today <= due <= week_end:
            groups["week"].append(task)
    return groups

