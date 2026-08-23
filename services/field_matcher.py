FIELD_RULES = {
    "task_name": ["任务", "任务名称", "工作事项", "事项", "工作内容", "招聘事项", "明细", "环节"],
    "stage": ["阶段", "模块", "任务模块", "项目模块"],
    "owner": ["负责人", "执行人", "责任人", "owner", "人员", "执行方"],
    "start_date": ["开始", "开始时间", "启动日期", "开始日期", "起始时间", "计划开始"],
    "end_date": ["截止", "结束时间", "截止时间", "完成日期", "结束日期", "计划完成", "时间节点", "日期"],
    "status": ["状态", "进度", "完成情况"],
    "remark": ["备注", "说明"],
}


def _normalized(value):
    return str(value).strip().lower().replace("\n", "")


def match_fields(columns):
    result = {}
    for col in columns:
        normalized = _normalized(col)
        for standard, names in FIELD_RULES.items():
            if normalized in {_normalized(name) for name in names}:
                result[str(col)] = standard
                break
    return result


def find_header_row(df, max_rows=20):
    best = (-1, {}, 0)
    for index in range(min(max_rows, len(df))):
        values = [str(v).strip() for v in df.iloc[index].tolist()]
        matches = match_fields(values)
        score = len(matches) + (2 if "task_name" in matches.values() else 0)
        if score > best[2]:
            best = (index, matches, score)
    return best[0], best[1]

