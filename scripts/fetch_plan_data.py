#!/usr/bin/env python3
"""
MES 实施计划报工分析数据拉取脚本。
用法：
  python fetch_plan_data.py \
    --team-id 23 \
    --team-name "东西大区4部" \
    --output /tmp/mes_plan_report_data.json
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import date, timedelta


def run_mes(cmd: list[str]) -> dict | list:
    full_cmd = ["mes", "-o", "json"] + cmd
    result = subprocess.run(full_cmd, capture_output=True, text=True)
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        print(f"[ERROR] mes 命令输出无法解析: {result.stdout[:200]}", file=sys.stderr)
        return {}


def _extract_list(data) -> list[dict]:
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        for key in ("list", "operateCallBackObj", "data"):
            val = data.get(key)
            if isinstance(val, list):
                return val
            if isinstance(val, dict):
                inner = val.get("list")
                if isinstance(inner, list):
                    return inner
    return []


def fetch_active_plans(team_id: int) -> list[dict]:
    """拉取指定团队所有进行中的实施计划（分页）。"""
    all_plans = []
    page = 1
    while True:
        data = run_mes([
            "plan", "list",
            "--team-id", str(team_id),
            "--status", "1",
            "--page", str(page),
            "--page-size", "100",
        ])
        items = _extract_list(data)
        if not items:
            break
        all_plans.extend(items)
        total = data.get("total", 0) if isinstance(data, dict) else len(items)
        if len(all_plans) >= total or len(items) < 100:
            break
        page += 1
    return all_plans


def fetch_team_statistics(team_id: int, from_date: str, to_date: str) -> list[dict]:
    """拉取指定团队在时间范围内的所有报工记录（分页）。"""
    all_records = []
    page = 1
    while True:
        data = run_mes([
            "statistics", "list",
            "--team-id", str(team_id),
            "--from", from_date,
            "--to", to_date,
            "--page", str(page),
            "--page-size", "200",
        ])
        items = _extract_list(data)
        if not items:
            break
        all_records.extend(items)
        has_next = False
        if isinstance(data, dict):
            has_next = data.get("hasNextPage", False)
        if not has_next or len(items) < 200:
            break
        page += 1
    return all_records


def format_date_short(s: str) -> str:
    """提取日期部分 YYYY-MM-DD。"""
    return s[:10] if s else ""


def main():
    parser = argparse.ArgumentParser(description="拉取 MES 实施计划报工分析数据")
    parser.add_argument("--team-id", type=int, required=True, help="团队 ID")
    parser.add_argument("--team-name", default="", help="团队名称")
    parser.add_argument("--reference-date", default="", help="基准日期 YYYY-MM-DD，默认今天")
    parser.add_argument("--output", required=True, help="输出 JSON 文件路径")

    args = parser.parse_args()

    ref_date = date.fromisoformat(args.reference_date) if args.reference_date else date.today()
    team_name = args.team_name or f"团队{args.team_id}"

    three_months_ago = (ref_date - timedelta(days=90))
    two_months_ago = (ref_date - timedelta(days=60))
    one_month_ago = (ref_date - timedelta(days=30))

    print(f"[INFO] 基准日期：{ref_date}，团队：{team_name}（id={args.team_id}）")
    print(f"[INFO] 时间窗口：3个月={three_months_ago}，2个月={two_months_ago}，1个月={one_month_ago}")

    # 1. 拉取进行中计划
    print("[INFO] 拉取进行中实施计划...")
    plans = fetch_active_plans(args.team_id)
    print(f"       共 {len(plans)} 个进行中计划")

    # 2. 拉取 3 个月内报工记录（覆盖所有时间窗口）
    print("[INFO] 拉取 3 个月内报工记录...")
    statistics = fetch_team_statistics(args.team_id, three_months_ago.isoformat(), ref_date.isoformat())
    print(f"       共 {len(statistics)} 条报工记录")

    # 3. 构建 accId → 最近报工日期 的映射
    acc_last_report: dict[str, str] = {}
    for r in statistics:
        acc_id = r.get("accId", "")
        if not acc_id:
            continue
        raw_date = r.get("taskDate") or r.get("start") or ""
        d = raw_date[:10]
        if not d:
            continue
        if acc_id not in acc_last_report or d > acc_last_report[acc_id]:
            acc_last_report[acc_id] = d

    print(f"       涉及 {len(acc_last_report)} 个不同合同子项（accId）")

    # 4. 分类计划
    three_month_plans = []
    two_month_plans = []
    one_month_plans = []

    for p in plans:
        acc_id = p.get("accId", "")
        last_report = acc_last_report.get(acc_id)

        # 提取关键字段
        plan_info = {
            "id": p.get("id"),
            "title": p.get("title", ""),
            "accId": acc_id,
            "accName": p.get("accName", ""),
            "companyName": p.get("companyName", ""),
            "contractName": p.get("contractName", ""),
            "contractNum": p.get("contractNum", ""),
            "status": p.get("status"),
            "statusDesc": p.get("statusDesc", ""),
            "startDate": format_date_short(p.get("startDate", "")),
            "endDate": format_date_short(p.get("endDate", "")),
            "executorList": [
                {
                    "executorId": e.get("executorId"),
                    "executorName": e.get("executorName", ""),
                }
                for e in (p.get("executorList") or [])
            ],
            "checkTypeDesc": p.get("checkTypeDesc", ""),
            "deliver": p.get("deliver") or "",
            "lastReportDate": last_report or None,
        }

        if last_report is None or last_report < three_months_ago.isoformat():
            three_month_plans.append(plan_info)
        elif last_report < two_months_ago.isoformat():
            two_month_plans.append(plan_info)
        elif last_report < one_month_ago.isoformat():
            one_month_plans.append(plan_info)

    # 按 accName 排序
    three_month_plans.sort(key=lambda x: x["accName"] or "")
    two_month_plans.sort(key=lambda x: x["accName"] or "")
    one_month_plans.sort(key=lambda x: x["accName"] or "")

    reported_count = sum(1 for p in plans if p.get("accId", "") in acc_last_report)

    # 5. 输出
    output = {
        "meta": {
            "teamId": args.team_id,
            "teamName": team_name,
            "referenceDate": ref_date.isoformat(),
            "threeMonthsAgo": three_months_ago.isoformat(),
            "twoMonthsAgo": two_months_ago.isoformat(),
            "oneMonthAgo": one_month_ago.isoformat(),
            "totalActivePlans": len(plans),
            "reportedAccIds": reported_count,
        },
        "noReportGroups": {
            "threeMonths": {
                "label": "3个月无报工",
                "description": f"自 {three_months_ago.isoformat()} 起无任何报工记录",
                "count": len(three_month_plans),
                "plans": three_month_plans,
            },
            "twoMonths": {
                "label": "2个月无报工（排除3个月组）",
                "description": f"最后报工在 {three_months_ago.isoformat()} ~ {two_months_ago.isoformat()} 之间",
                "count": len(two_month_plans),
                "plans": two_month_plans,
            },
            "oneMonth": {
                "label": "1个月无报工（排除更长周期组）",
                "description": f"最后报工在 {two_months_ago.isoformat()} ~ {one_month_ago.isoformat()} 之间",
                "count": len(one_month_plans),
                "plans": one_month_plans,
            },
        },
    }

    output_path = os.path.expanduser(args.output)
    out_dir = os.path.dirname(output_path)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\n[结果汇总]")
    print(f"  进行中计划总数：{len(plans)}")
    print(f"  3个月无报工：{len(three_month_plans)} 个")
    print(f"  仅2个月无报工：{len(two_month_plans)} 个")
    print(f"  仅1个月无报工：{len(one_month_plans)} 个")
    print(f"  近期有报工：{len(plans) - len(three_month_plans) - len(two_month_plans) - len(one_month_plans)} 个")
    print(f"\n[OK] 数据已输出：{output_path}")


if __name__ == "__main__":
    main()
