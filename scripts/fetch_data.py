#!/usr/bin/env python3
"""
MES 报工数据拉取脚本 — 纯数据层，输出 JSON，不生成 HTML。
用法：
  python3 fetch_data.py \
    --team-ids 2,3,23,19 \
    --team-names "东西大区1部,东西大区2部,东西大区4部,东西大区5部" \
    --from 2026-04-21 \
    --to 2026-04-23 \
    --output /path/to/data.json
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import date, timedelta


def run_mes(cmd: list[str]) -> dict | list:
    """执行 mes 命令并返回 JSON 结果（dict 或 list）。"""
    full_cmd = ["mes", "-o", "json"] + cmd
    result = subprocess.run(full_cmd, capture_output=True, text=True)
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        print(f"[ERROR] mes 命令输出无法解析: {result.stdout[:200]}", file=sys.stderr)
        return []


def get_work_dates(from_date: str, to_date: str) -> list[str]:
    """返回日期范围内的工作日列表（排除周末）。"""
    start = date.fromisoformat(from_date)
    end = date.fromisoformat(to_date)
    result = []
    cur = start
    while cur <= end:
        if cur.weekday() < 5:
            result.append(cur.isoformat())
        cur += timedelta(days=1)
    return result


def fetch_team_members(team_id: int) -> list[dict]:
    """获取指定团队的成员列表（userId + employeeName）。"""
    data = run_mes(["util", "list-members", "--team-id", str(team_id)])
    return data if isinstance(data, list) else []


def fetch_summary(team_id: int, from_date: str, to_date: str) -> list[dict]:
    """获取指定团队在时间范围内的报工 summary（含成员明细）。"""
    data = run_mes(["statistics", "summary", "--team-id", str(team_id), "--from", from_date, "--to", to_date])
    if isinstance(data, dict):
        return data.get("operateCallBackObj", [])
    return []


def fetch_list_by_user(user_id: int, from_date: str, to_date: str) -> list[dict]:
    """通过 statistics list 获取某用户的报工记录列表（用于聚合每日工时和记录数）。"""
    all_records = []
    page = 1
    while True:
        data = run_mes([
            "statistics", "list",
            "--executor-id", str(user_id),
            "--from", from_date,
            "--to", to_date,
            "--page", str(page),
            "--page-size", "100",
        ])
        items = _extract_list(data)
        has_next = False
        if isinstance(data, dict):
            has_next = data.get("hasNextPage", False)
        if not items:
            break
        all_records.extend(items)
        if not has_next or len(items) < 100:
            break
        page += 1
    return all_records


def fetch_articles(team_id: int, from_date: str, to_date: str) -> list[dict]:
    """获取指定团队的文档列表。"""
    start_time = f"{from_date} 00:00:00"
    end_time = f"{to_date} 23:59:59"
    all_articles = []
    page = 1
    while True:
        data = run_mes([
            "article", "list",
            "--team-id", str(team_id),
            "--start-time", start_time,
            "--end-time", end_time,
            "--mode", "manage",
            "--page", str(page),
            "--page-size", "50",
        ])
        if isinstance(data, dict):
            items = data.get("list", data.get("operateCallBackObj", data.get("data", [])))
        elif isinstance(data, list):
            items = data
        else:
            break
        if not items:
            break
        all_articles.extend(items)
        if len(items) < 50:
            break
        page += 1
    return all_articles


def fetch_scores(team_id: int, month: str) -> list[dict]:
    """获取指定团队的报工质量评分。"""
    all_scores = []
    page = 1
    while True:
        data = run_mes([
            "dashboard", "score", "list",
            "--team-id", str(team_id),
            "--month", month,
            "--page", str(page),
            "--page-size", "50",
        ])
        if isinstance(data, dict):
            page_data = data.get("operateCallBackObj", {})
            if isinstance(page_data, dict):
                items = page_data.get("list", [])
                has_next = page_data.get("hasNextPage", False)
            elif isinstance(page_data, list):
                items = page_data
                has_next = False
            else:
                items = []
                has_next = False
        elif isinstance(data, list):
            items = data
            has_next = False
        else:
            break
        all_scores.extend(items)
        if not has_next or not items:
            break
        page += 1
    return all_scores


def _extract_list(data) -> list[dict]:
    """从各种 mes 返回格式中提取列表。"""
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        # 常见结构：{list: [...]} / {operateCallBackObj: {list: [...]}} / {operateCallBackObj: [...]} / {data: [...]}
        for key in ("list", "operateCallBackObj", "data"):
            val = data.get(key)
            if isinstance(val, list):
                return val
            if isinstance(val, dict):
                inner = val.get("list")
                if isinstance(inner, list):
                    return inner
    return []


def fetch_service_requests(person_ids: list[int], from_date: str, to_date: str) -> list[dict]:
    """获取指定人员在时间范围内的服务请求列表。person_ids 为空时拉全量。"""
    start_time = f"{from_date} 00:00:00"
    end_time = f"{to_date} 23:59:59"
    all_items = []
    # 按人员分批拉取（避免全量查询）
    if person_ids:
        for pid in person_ids:
            data = run_mes([
                "service", "request", "list",
                "--person-id", str(pid),
                "--start-time", start_time,
                "--end-time", end_time,
                "--page-size", "100",
            ])
            all_items.extend(_extract_list(data))
    else:
        data = run_mes([
            "service", "request", "list",
            "--start-time", start_time,
            "--end-time", end_time,
            "--page-size", "100",
        ])
        all_items.extend(_extract_list(data))
    return all_items


def fetch_service_stats() -> dict:
    """获取全局服务统计卡片（待处理咨询/工单/计划/未关闭工单数）。"""
    data = run_mes(["dashboard", "service"])
    return data if isinstance(data, dict) else {}


def fetch_task_table(from_date: str, to_date: str) -> list[dict]:
    """获取部门工时分布表。"""
    data = run_mes([
        "dashboard", "task-table",
        "--from", from_date,
        "--to", to_date,
    ])
    if isinstance(data, dict):
        return data.get("operateCallBackObj", data.get("data", []))
    return data if isinstance(data, list) else []


def fetch_weekly_reports(from_date: str, to_date: str, target_person_ids: set[int]) -> list[dict]:
    """获取指定人员范围内已提交的周报（含完整正文）。按人聚合，仅保留目标人员。"""
    all_reports = []
    page = 1
    while True:
        data = run_mes([
            "dashboard", "weeklyReport",
            "--period-from", from_date,
            "--period-to", to_date,
            "--type", "WEEKLY",
            "--page-size", "50",
            "--page", str(page),
        ])
        if isinstance(data, dict):
            items = data.get("list", [])
        elif isinstance(data, list):
            items = data
        else:
            break
        if not items:
            break
        for r in items:
            pid = r.get("createdBy")
            if pid and pid not in target_person_ids:
                continue
            # 拉取完整正文
            detail_data = run_mes(["dashboard", "weeklyReport", "view", str(r.get("id"))])
            if isinstance(detail_data, dict):
                obj = detail_data.get("operateCallBackObj", {})
            else:
                obj = {}
            all_reports.append({
                "id": r.get("id"),
                "employeeName": r.get("employeeName") or obj.get("employeeName") or "",
                "userId": pid,
                "teamName": r.get("adminTeamName") or obj.get("adminTeamName") or "",
                "periodStartDate": r.get("periodStartDate") or obj.get("periodStartDate") or "",
                "periodEndDate": r.get("periodEndDate") or obj.get("periodEndDate") or "",
                "createdTime": r.get("createdTime") or obj.get("createdTime") or "",
                "contentMd": obj.get("contentMd") or r.get("contentMd") or "",
                "content": obj.get("content") or r.get("content") or "",
            })
        if len(items) < 50:
            break
        page += 1
    return all_reports


def fetch_contracts_for_teams(team_ids: list[int]) -> dict[str, dict]:
    """按团队ID拉取合同列表，返回 {contractNum: contractInfo} 映射。"""
    result = {}
    page = 1
    while True:
        # 分页拉取合同，每页50条
        data = run_mes([
            "contract", "list",
            "--page", str(page),
            "--page-size", "50",
        ])
        items = _extract_list(data)
        if not items:
            break
        for c in items:
            # 匹配目标团队：serviceTeams 中包含目标 teamId
            service_teams = c.get("serviceTeams") or []
            matched = any(
                str(tid) in str(st.get("id", "")) or
                any(str(tid) in str(m) for m in (st.get("dutyIds") or []))
                for st in service_teams
                for tid in team_ids
            )
            if matched or not team_ids:
                cn = c.get("contractNum") or ""
                if cn:
                    result[cn] = {
                        "contractId": c.get("id"),
                        "contractName": c.get("name") or "",
                        "contractNum": cn,
                        "companyName": c.get("companyName") or "",
                        "contractOwner": c.get("contractOwner") or "",
                        "contractStartTime": c.get("contractStartTime") or "",
                        "contractEndTime": c.get("contractEndTime") or "",
                        "serviceTeams": [st.get("name", "") for st in service_teams],
                    }
        if len(items) < 50:
            break
        page += 1
    return result


def fetch_contract_items_by_range(
    start_date: str, end_date: str
) -> list[dict]:
    """按子项窗口日期范围拉取合同子项（分页，自动翻完）。"""
    all_items = []
    page = 1
    while True:
        data = run_mes([
            "contract", "list-items",
            "--date-range-start", start_date,
            "--date-range-end", end_date,
            "--page", str(page),
            "--page-size", "50",
        ])
        if isinstance(data, dict):
            obj = data.get("operateCallBackObj", {})
            if isinstance(obj, dict):
                items = obj.get("list", [])
                has_next = obj.get("hasNextPage", False)
            elif isinstance(obj, list):
                items = obj
                has_next = False
            else:
                break
        elif isinstance(data, list):
            items = data
            has_next = False
        else:
            break
        if not items:
            break
        all_items.extend(items)
        if not has_next or len(items) < 50:
            break
        page += 1
    return all_items


def weekday_cn(d: str) -> str:
    wds = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
    return wds[date.fromisoformat(d).weekday()]


def main():
    parser = argparse.ArgumentParser(description="拉取 MES 报工数据并输出 JSON")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--team-ids", help="多团队逗号分隔，如 2,3,23,19")
    group.add_argument("--team-id", type=int, help="单团队 ID")

    parser.add_argument("--team-names", help="对应团队名称，逗号分隔")
    parser.add_argument("--team-name", help="单团队名称")
    parser.add_argument("--from", dest="from_date", required=True, help="开始日期 YYYY-MM-DD")
    parser.add_argument("--to", dest="to_date", required=True, help="结束日期 YYYY-MM-DD")
    parser.add_argument("--std-hours-per-day", type=float, default=8.0, help="每日标准工时，默认 8")
    parser.add_argument("--output", required=True, help="输出 JSON 文件路径")
    parser.add_argument("--fetch-extra", action="store_true", default=True, help="是否拉取额外数据（文档、质量评分、服务请求、服务统计）；默认开启")
    parser.add_argument("--fetch-weekly-reports", action="store_true", default=True, help="是否拉取周报（含完整正文，按团队分组）；默认开启")
    parser.add_argument("--fetch-project-unreported", action="store_true", default=True, help="是否拉取项目未报工分析（合同子项维度）；默认开启")

    args = parser.parse_args()

    # 整理团队列表
    if args.team_id:
        team_ids = [args.team_id]
        team_names = [args.team_name or f"团队{args.team_id}"]
    else:
        team_ids = [int(x.strip()) for x in args.team_ids.split(",")]
        if args.team_names:
            team_names = [x.strip() for x in args.team_names.split(",")]
        else:
            team_names = [f"团队{tid}" for tid in team_ids]

    work_dates = get_work_dates(args.from_date, args.to_date)
    work_days = len(work_dates)
    std_per_day = args.std_hours_per_day
    std_total = work_days * std_per_day
    month_str = args.from_date[:7]  # YYYY-MM

    print(f"[INFO] 拉取数据：{team_names}，周期 {args.from_date} ~ {args.to_date}，{work_days} 个工作日")

    # ─── 主数据：各团队 summary + 成员每日工时 ───
    teams_data = []
    all_team_member_ids = set()  # 收集所有团队成员 userId，用于服务请求筛选

    for tid, tname in zip(team_ids, team_names):
        print(f"[INFO] 拉取 {tname}（team-id={tid}）成员列表...")
        team_member_list = fetch_team_members(tid)
        team_member_ids = {m["userId"] for m in team_member_list if m.get("userId")}
        all_team_member_ids.update(team_member_ids)
        print(f"       {len(team_member_list)} 名成员")

        print(f"[INFO] 拉取 {tname} summary...")
        members = fetch_summary(tid, args.from_date, args.to_date)
        print(f"       {len(members)} 名成员有报工记录，获取每日工时...")

        # 已报工成员 userId 集合
        reported_user_ids = {m.get("userId") for m in members if m.get("userId")}

        # 识别未报工人员
        unreported_members = [
            {"name": m.get("employeeName", ""), "userId": m.get("userId")}
            for m in team_member_list
            if m.get("userId") and m.get("userId") not in reported_user_ids
        ]

        member_stats = []
        team_projects = {}   # key: (accName, companyName), val: {hours, members:set}
        team_total = 0
        team_full_count = 0
        team_overtime = 0
        team_pre = 0
        team_after = 0
        team_internal = 0
        team_doc_count = 0
        team_score_sum = 0
        team_score_count = 0

        for m in members:
            total = round(m.get("totalTaskTime", 0) or 0, 1)
            pre = round(m.get("preTaskTime", 0) or 0, 1)
            after = round(m.get("afterTaskTime", 0) or 0, 1)
            internal = round(m.get("internalTaskTime", 0) or 0, 1)
            overtime = round(m.get("overTaskTime", 0) or 0, 1)
            doc = m.get("docCount", 0) or 0
            score = m.get("operationStandardScore", 0) or 0

            team_total += total
            team_overtime += overtime
            team_pre += pre
            team_after += after
            team_internal += internal
            team_doc_count += doc
            if score > 0:
                team_score_sum += score
                team_score_count += 1
            if total >= std_total:
                team_full_count += 1

            # 通过 statistics list 按日聚合（修复 calendar 无法查他人数据的问题）
            daily = {}
            record_count = 0
            if m.get("userId"):
                records = fetch_list_by_user(m["userId"], args.from_date, args.to_date)
                record_count = len(records)
                member_name = m.get("userName", "")
                for r in records:
                    # 日期优先从 start 字段取，兼容 taskDate
                    raw_date = r.get("taskDate") or r.get("start") or ""
                    d = raw_date[:10]
                    h = round(r.get("taskTime", 0) or 0, 1)
                    if d:
                        daily[d] = daily.get(d, 0) + h
                    # 按项目聚合（以 accName 为项目名，companyName 为公司名）
                    acc_key = (r.get("accName") or "其他项目", r.get("companyName") or "未知公司")
                    if acc_key not in team_projects:
                        team_projects[acc_key] = {"hours": 0.0, "members": set()}
                    team_projects[acc_key]["hours"] += h
                    team_projects[acc_key]["members"].add(member_name)

            member_stats.append({
                "name": m.get("userName", ""),
                "userId": m.get("userId"),
                "city": m.get("workCity") or "",
                "total": total,
                "pre": pre,
                "after": after,
                "internal": internal,
                "overtime": overtime,
                "doc": doc,
                "score": score,
                "recordCount": record_count,
                "daily": daily,
                "shortage": round(std_total - total, 1) if total < std_total else 0,
                "full": total >= std_total,
            })

        # 项目报工排名（TOP10）：按工时降序
        project_ranking = sorted(
            [{"name": k[0], "company": k[1],
              "hours": round(v["hours"], 1),
              "memberCount": len(v["members"]),
              "members": sorted(v["members"])}
             for k, v in team_projects.items()],
            key=lambda x: -x["hours"]
        )[:10]

        n = len(members)
        teams_data.append({
            "teamId": tid,
            "teamName": tname,
            "memberCount": len(team_member_list),
            "reportedMemberCount": n,
            "totalHours": round(team_total, 1),
            "avgHours": round(team_total / n, 2) if n > 0 else 0,
            "fullCount": team_full_count,
            "fullRate": round(team_full_count / n * 100, 1) if n > 0 else 0,
            "overtimeHours": round(team_overtime, 1),
            "preHours": round(team_pre, 1),
            "afterHours": round(team_after, 1),
            "internalHours": round(team_internal, 1),
            "docCount": team_doc_count,
            "avgScore": round(team_score_sum / team_score_count, 1) if team_score_count > 0 else 0,
            "members": sorted(member_stats, key=lambda x: -x["total"]),
            "unreportedMembers": sorted(unreported_members, key=lambda x: x["name"]),
            "projectRanking": project_ranking,
        })
        print(f"       完成：总工时 {team_total}h，人均 {team_total/max(n,1):.1f}h，TOP项目 {len(project_ranking)} 个")

    output = {
        "meta": {
            "fromDate": args.from_date,
            "toDate": args.to_date,
            "workDays": work_days,
            "workDates": work_dates,
            "stdHoursPerDay": std_per_day,
            "stdHoursTotal": std_total,
            "teamNames": team_names,
            "generatedAt": f"{args.from_date} {args.to_date}",
        },
        "teams": teams_data,
    }

    # ─── 额外数据：文档、质量评分、服务请求、服务统计、工时分布表 ───
    if args.fetch_extra:
        print("[INFO] 拉取额外数据...")

        # 文档统计
        articles_all = []
        for tid, tname in zip(team_ids, team_names):
            print(f"       文档: {tname}...")
            arts = fetch_articles(tid, args.from_date, args.to_date)
            for a in arts:
                articles_all.append({
                    "teamName": tname,
                    "teamId": tid,
                    "title": a.get("title", ""),
                    "author": a.get("employeeName", "") or a.get("createdByName", ""),
                    "authorId": a.get("createdBy"),
                    "createTime": a.get("createdTime", "") or a.get("createTime", ""),
                })
        output["articles"] = articles_all

        # 质量评分
        scores_all = []
        for tid, tname in zip(team_ids, team_names):
            print(f"       质量评分: {tname}...")
            scores = fetch_scores(tid, month_str)
            for s in scores:
                scores_all.append({
                    "teamName": tname,
                    "teamId": tid,
                    **s,
                })
        output["scores"] = scores_all

        # 服务请求（按团队成员范围筛选）
        print(f"       服务请求（筛选 {len(all_team_member_ids)} 名成员）...")
        services = fetch_service_requests(list(all_team_member_ids), args.from_date, args.to_date)
        output["serviceRequests"] = services

        # 服务请求统计：按客户和处理人聚合
        from collections import defaultdict
        by_company: dict[str, dict] = defaultdict(lambda: {"count": 0, "open": 0, "closed": 0})
        by_executor: dict[str, dict] = defaultdict(lambda: {"teamName": "", "count": 0, "open": 0, "closed": 0})
        for s in services:
            cn = s.get("companyName") or "未知客户"
            en = s.get("executorEmployeeName") or s.get("executorName") or "未分配"
            tn = s.get("teamName") or ""
            st = s.get("status", 0)
            is_open = st in (0, 1, 4)  # 已提交/处理中/待反馈 为开放
            by_company[cn]["count"] += 1
            if is_open:
                by_company[cn]["open"] += 1
            else:
                by_company[cn]["closed"] += 1
            if en not in by_executor or not by_executor[en]["teamName"]:
                by_executor[en]["teamName"] = tn
            by_executor[en]["count"] += 1
            if is_open:
                by_executor[en]["open"] += 1
            else:
                by_executor[en]["closed"] += 1

        output["serviceRequestStats"] = {
            "byCompany": sorted(
                [{"companyName": k, "count": v["count"], "open": v["open"], "closed": v["closed"]}
                 for k, v in by_company.items()],
                key=lambda x: -x["count"]
            ),
            "byExecutor": sorted(
                [{"executorName": k, "teamName": v["teamName"],
                  "count": v["count"], "open": v["open"], "closed": v["closed"]}
                 for k, v in by_executor.items()],
                key=lambda x: -x["count"]
            ),
        }
        print(f"       服务请求统计：{len(by_company)} 家客户，{len(by_executor)} 名处理人")

        # 全局服务统计
        print(f"       服务统计卡片...")
        svc_stats = fetch_service_stats()
        output["serviceStats"] = svc_stats

        # 部门工时分布表
        print(f"       工时分布表...")
        task_table = fetch_task_table(args.from_date, args.to_date)
        # 只保留目标团队的数据
        target_team_ids_set = set(team_ids)
        output["taskTable"] = [r for r in task_table if r.get("teamId") in target_team_ids_set]

        # 周报（含完整正文，按团队分组）
        if args.fetch_weekly_reports:
            print(f"       周报（筛选 {len(all_team_member_ids)} 名成员）...")
            raw_reports = fetch_weekly_reports(
                args.from_date, args.to_date, all_team_member_ids
            )
            # 按团队分组
            team_reports: dict[str, list[dict]] = {t: [] for t in team_names}
            for r in raw_reports:
                tn = r.get("teamName", "")
                # 尝试匹配团队名
                matched = next(
                    (t for t in team_names if t in tn or tn in t), None
                )
                if matched:
                    team_reports[matched].append(r)
            output["weeklyReports"] = [
                {"teamName": t, "reports": sorted(rs, key=lambda x: x.get("employeeName", ""))}
                for t, rs in team_reports.items()
            ]
            print(f"       周报：共 {len(raw_reports)} 份，分布 {sum(1 for v in team_reports.values() if v)} 个团队")

        # 项目未报工分析（合同子项维度）
        if args.fetch_project_unreported:
            print(f"       项目未报工分析...")
            from datetime import date, timedelta
            today = date.today()
            # 子项窗口：过去6个月 ~ 未来12个月（覆盖所有活跃子项）
            item_start = (today - timedelta(days=180)).isoformat()
            item_end = (today + timedelta(days=365)).isoformat()

            # 拉取目标团队合同
            contracts = fetch_contracts_for_teams(team_ids)
            print(f"       目标团队合同数：{len(contracts)}")

            # 拉取合同子项
            all_items = fetch_contract_items_by_range(item_start, item_end)
            print(f"       合同子项总数：{len(all_items)}")

            # 按合同号聚合子项
            from collections import defaultdict
            contract_items: dict[str, list[dict]] = defaultdict(list)
            for item in all_items:
                cn = item.get("contractNum") or ""
                if cn:
                    contract_items[cn].append(item)

            # 筛选在服务期内（合同 endDate >= today）的目标团队合同
            unreported_contracts = []
            reported_contracts = []  # 有子项已报工但也有未报工子项的合同
            zero_hour_total_plan = 0  # 未报工子项的计划工时合计

            for cn, items in contract_items.items():
                contract_info = contracts.get(cn, {})
                # 取合同主信息的结束时间
                end_time_str = contract_info.get("contractEndTime", "") or \
                    max((it.get("endTime", "") or "" for it in items), default="")
                # 判断是否仍在服务期（结束日期 >= today）
                try:
                    end_date = date.fromisoformat(end_time_str[:10]) if end_time_str else date.min
                except ValueError:
                    end_date = date.min
                if end_date < today:
                    continue  # 跳过已结束合同

                # 分类子项
                zero_items = [it for it in items if (it.get("actualHours") or 0) == 0]
                non_zero_items = [it for it in items if (it.get("actualHours") or 0) > 0]

                # 未报工子项汇总
                total_plan_zero = sum(it.get("planHour") or 0 for it in zero_items)
                total_actual_zero = sum(it.get("actualHours") or 0 for it in zero_items)
                zero_hour_total_plan += total_plan_zero

                if zero_items:
                    record = {
                        "contractNum": cn,
                        "contractName": contract_info.get("contractName") or items[0].get("companyName") or "",
                        "companyName": contract_info.get("companyName") or items[0].get("companyName") or "",
                        "contractOwner": contract_info.get("contractOwner") or items[0].get("ownerName") or "",
                        "contractStartTime": contract_info.get("contractStartTime") or "",
                        "contractEndTime": end_time_str[:10] if end_time_str else "",
                        "serviceTeams": contract_info.get("serviceTeams") or [],
                        "totalPlanHours": sum(it.get("planHour") or 0 for it in items),
                        "totalActualHours": sum(it.get("actualHours") or 0 for it in items),
                        "totalRemainingHours": sum(max((it.get("diffHours") or 0), 0) for it in items),
                        "itemCount": len(items),
                        "zeroItemCount": len(zero_items),
                        "nonZeroItemCount": len(non_zero_items),
                        "zeroItems": [
                            {
                                "itemName": it.get("itemName") or "",
                                "itemType": it.get("itemType") or "",
                                "planHour": it.get("planHour") or 0,
                                "actualHours": it.get("actualHours") or 0,
                                "remainingHours": max((it.get("diffHours") or 0), 0),
                                "startTime": it.get("startTime", "")[:10] if it.get("startTime") else "",
                                "endTime": it.get("endTime", "")[:10] if it.get("endTime") else "",
                                "ownerName": it.get("ownerName") or "",
                            }
                            for it in sorted(zero_items, key=lambda x: -(x.get("planHour") or 0))
                        ],
                        "nonZeroItems": [
                            {
                                "itemName": it.get("itemName") or "",
                                "itemType": it.get("itemType") or "",
                                "planHour": it.get("planHour") or 0,
                                "actualHours": it.get("actualHours") or 0,
                                "remainingHours": max((it.get("diffHours") or 0), 0),
                            }
                            for it in sorted(non_zero_items, key=lambda x: -(x.get("planHour") or 0))[:5]
                        ],
                    }
                    if non_zero_items:
                        reported_contracts.append(record)
                    else:
                        unreported_contracts.append(record)

            # 按未报工子项数降序排列
            unreported_contracts.sort(key=lambda x: -x["zeroItemCount"])
            reported_contracts.sort(key=lambda x: -x["zeroItemCount"])

            output["projectUnreported"] = {
                "summary": {
                    "totalContracts": len(unreported_contracts) + len(reported_contracts),
                    "zeroContracts": len(unreported_contracts),
                    "mixedContracts": len(reported_contracts),
                    "totalZeroItemPlanHours": zero_hour_total_plan,
                },
                "contracts": unreported_contracts + reported_contracts,
            }
            print(f"       未报工分析：{len(unreported_contracts)} 个纯未报工合同，{len(reported_contracts)} 个混合合同")

    # 写出 JSON
    output_path = os.path.expanduser(args.output)
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"[OK] 数据已输出：{output_path}")


if __name__ == "__main__":
    main()
