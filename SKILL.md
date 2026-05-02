---
name: mes-work-report
description: >
  生成团队或大区的 MES 报工统计分析 HTML 可视化看板。
  当用户需要查看某个团队（如东西大区4部、东西大区2部）或某个大区（如东西大区、南北大区）的报工工时统计、满勤率、加班、不达标人员等汇总信息时触发，
  尤其是需要将结果以可视化报告或HTML看板形式输出时。

  触发关键词：报工统计报告、报工看板、工时报表、各团队报工对比、大区报工分析、
  周报统计、满勤率、工时不达标、加班统计、报工汇总HTML、生成报工报告、生成看板、
  报工周报、团队周报、大区周报、项目未报工、合同未报工、子项未报工、合同子项统计、
  每人每周工作总结、周报内容、周报详情、周报摘要、周报查看。

  plan-report 类型触发关键词：实施计划无报工、实施计划报工分析、计划报工看板、
  实施计划看板、计划无报工、实施计划分析、僵尸计划、计划报工报告。

  excel-export 类型触发关键词：零报工实施计划、极低报工实施计划、实施计划Excel、
  实施计划报表、实施计划零报工、实施计划极低报工、计划报工Excel、导出实施计划报表。

  风格选择关键词：默认风格、科技风格、暗色风格、Apple风格、苹果风格、PlayStation风格、PS风格、索尼风格、
  Starbucks风格、星巴克风格、绿色风格、Notion风格、笔记风格、简约风格、
  Figma风格、专业风格、黑白风格、Anthropic风格、温暖风格、羊皮纸。

  默认风格：用户未指定风格时，使用默认暗色科技风格（深蓝背景 + 青色强调色），即 default-design.css。
---

# MES 报工统计报告生成器

## 架构概述

> **`$SKILL_DIR`** = 本 Skill 的安装目录（即 `~/.workbuddy/skills/mes-work-report`）。Agent 执行命令时需将 `$SKILL_DIR` 替换为实际绝对路径。

本 Skill 采用 **混合方案**：

1. **`$SKILL_DIR/scripts/fetch_data.py`** — 纯数据拉取层，调用 `mes` CLI 拉取所有原始数据，输出 JSON
2. **Agent（本 SKILL.md）** — 报告编排层，读取 JSON 数据，按 14 章节结构生成完整 HTML

```
用户请求 → Agent 读 SKILL.md → 执行 fetch_data.py 拉取 JSON → Agent 读取 JSON → 生成 HTML
```

> Agent 负责全部 HTML 生成逻辑，不依赖硬编码模板。新增/修改章节只需改本文件或 references/ 下的章节定义文件。

## 预设风格系统

提供 7 种预设视觉风格，用户通过自然语言选择：

| 风格 | CSS 文件 | 特点 | 适用场景 |
|------|----------|------|----------|
| **默认** ⭐ | `default-design.css` | 深蓝背景 `#1a1a2e`，青色强调色 `#00d4ff`，红色警示色 `#e94560` | **默认风格**，通用场景 |
| **Apple** | `apple-design.css` | 蓝白渐变背景，SF Pro 字体，毛玻璃效果 | 正式汇报、演示展示 |
| **PlayStation** | `ps-design.css` | 深色科技风，蓝色主调，渐变卡片 | 技术团队、开发者 |
| **Starbucks** | `starbucks-design.css` | 温暖绿色主题，咖啡店氛围 | 轻松氛围、客户展示 |
| **Notion** | `notion-design.css` | 极简浅色，清晰层次 | 文档风格、办公协作 |
| **Figma** | `figma-design.css` | 黑白极简，专业工具感 | 专业工具、数据分析 |
| **Anthropic** | `anthropic-design.css` | 温暖羊皮纸质感，衬线字体 | 阅读体验、知识沉淀 |

> ⭐ **默认风格**：用户未指定风格时，自动使用默认暗色科技风格。

**风格关键词映射**：
- 未指定 / "默认风格" / "科技风格" / "暗色风格" → `default-design.css`
- "Apple 风格" / "苹果风格" → `apple-design.css`
- "PlayStation 风格" / "PS 风格" / "索尼风格" → `ps-design.css`
- "Starbucks 风格" / "星巴克风格" / "绿色风格" → `starbucks-design.css`
- "Notion 风格" / "笔记风格" / "简约风格" → `notion-design.css`
- "Figma 风格" / "专业风格" / "黑白风格" → `figma-design.css`
- "Anthropic 风格" / "温暖风格" / "羊皮纸" → `anthropic-design.css`

**CSS 内嵌方式**：将 CSS 文件内容直接写入 `<style>` 标签，确保 HTML 可独立分享。

**统一字体大小体系**：

| 元素 | 字号 | 字重 |
|------|------|------|
| Hero 主标题 | 32px | 700 |
| 章节标题 | 18px | 600 |
| 卡片标题 | 14px | 600 |
| 正文内容 | 13px | 400 |
| 表格/标签 | 12px | 400 |
| 辅助说明 | 11px | 400 |

---

## 报告维度

根据请求范围，报告分为两种维度，影响 Hero 标题、章节结构、汇总层级等：

| 维度 | 触发条件 | 典型请求 |
|------|---------|---------|
| **🌍 区-团队** | 请求包含大区名且拉取该大区下多个子团队 | "南北大区报工看板"、"东西大区周报" |
| **👥 按团队** | 请求指定具体团队名，或多个不属同一大区的团队 | "4部看板"、"2部和4部的报告" |

**判定逻辑**：
- "东西大区" / "南北大区" → 检查是否拉取了该大区下多个子团队 → 是 → 🌍
- "4部" / "2部和5部" → 👥
- "东西大区4部" → 单团队 → 👥
- "东西大区2部和4部"（同大区但非全团队）→ **默认 👥**（不是完整大区对比）

**维度对报告的影响**：

| 报告元素 | 🌍 区-团队 | 👥 按团队 |
|---------|-----------|----------|
| Hero 标题 | "{大区名}报工统计" | "{团队名}报工统计"（多团队顿号连接） |
| Hero 副标题 | "覆盖 {N} 个团队 · {M} 人" | "{N} 人 · {工作日}个工作日" |
| 第一章 | 大区汇总卡片 + 各团队卡片 + **综合评价**（总体/亮点/待改进/服务统计） | 各团队卡片（无大区汇总层） + **综合评价** |
| 第六章 A 表 | **必须有**团队横向对比表 | 单团队省略，多团队保留 |
| 第十三章 | ~~已合并至第一章~~ | ~~各团队独立评价~~ |
| 报告文件名 | `{大区名}_报工看板_{日期}.html` | `{团队名}_报工看板_{日期}.html` |

> 详细的章节定义和维度差异，见 `references/report-sections.md`。

---

## 团队 ID 查找

读取 `references/team_ids.md` 获取团队名称 → ID 的映射。

**常用 ID 速查：**
- 东西大区1部=2，东西大区2部=3，东西大区4部=23，东西大区5部=19
- 南北大区2部=25，南北大区4部=11，南北大区5部=22
- 东西大区（整体）=96，南北大区（整体）=94

未知团队 ID 时执行：`mes -o json util list-teams` 并搜索。

## 工作流

### Step 0：环境检查

确认 Python 和 mes CLI 可用：

```bash
which python 2>/dev/null && python --version 2>/dev/null || which python3 2>/dev/null && python3 --version 2>/dev/null
mes auth status
```

> **Python 命令选择**：若 `python` 可用则使用 `python`，否则使用 `python3`。后续所有脚本调用均使用检测到的命令，不要硬编码 `python3`。

若未登录，提示用户先执行 `mes auth login --web`。

### Step 1：解析请求

从用户请求中提取：
- **报告类型**：
  - `work-report`（默认）：报工统计看板（触发关键词见顶部）
  - `plan-report`：实施计划报工分析（触发关键词见顶部）
- **目标范围**：单团队 or 多团队 or 整个大区（多个团队对比）
- **时间范围**：本周/上周/本月/具体日期，转换为 `--from YYYY-MM-DD --to YYYY-MM-DD`
- **报告维度**：🌍 区-团队 or 👥 按团队（见上方「报告维度」章节，仅 work-report 使用）
- **预设风格**：识别用户指定的视觉风格

**日期推算规则：**
- "本周"：本周一 ~ 今天（或本周五）
- "上周"：上周一 ~ 上周五
- "本月"：本月1日 ~ 今天
- 直接说"4.14到4.17"：转换为 2026-04-14 ~ 2026-04-17

**注意：** 若用户要求"整个东西大区"对比，分别用 team-id=2,3,23,19（四个服务团队），而**不是** team-id=96（大区整体，无法分团队对比）。

### Step 2：执行数据拉取

**work-report 类型**，调用 `fetch_data.py` 拉取全部数据（JSON 输出）：

```bash
python $SKILL_DIR/scripts/fetch_data.py \
  --team-ids 2,3,23,19 \
  --team-names "东西大区1部,东西大区2部,东西大区4部,东西大区5部" \
  --from 2026-04-21 \
  --to 2026-04-23 \
  --fetch-extra \
  --output /tmp/mes_report_data.json
```

**参数说明：**
- `--team-id` / `--team-ids`：目标团队 ID（必填二选一）
- `--team-name` / `--team-names`：对应团队名称
- `--from` / `--to`：日期范围（必填）
- `--std-hours-per-day`：每日标准工时，默认 8
- `--fetch-extra`：拉取额外数据（文档、评分、服务请求、服务统计、工时分布表），默认开启
- `--fetch-weekly-reports`：拉取周报（含完整正文，按团队分组），默认开启
- `--fetch-project-unreported`：拉取项目未报工分析（合同子项维度），默认开启
- `--output`：输出 JSON 文件路径

**JSON 输出结构（顶层）**：
```
meta: { fromDate, toDate, workDays, workDates, stdHoursPerDay, stdHoursTotal, teamNames }
teams: [{ teamId, teamName, memberCount, reportedMemberCount, totalHours, avgHours,
          fullCount, fullRate, overtimeHours, preHours, afterHours, internalHours,
          docCount, avgScore, members[], unreportedMembers[], projectRanking[] }]
articles: [...]
scores: [...]
serviceRequests: [...]
serviceStats: {...}
taskTable: [...]
weeklyReports: [...]      # 默认拉取
projectUnreported: {...}  # 默认拉取
```

**plan-report 类型**，调用 `fetch_plan_data.py` 拉取数据：

```bash
python $SKILL_DIR/scripts/fetch_plan_data.py \
  --team-id 23 \
  --team-name "东西大区4部" \
  --output /tmp/mes_plan_report_data.json
```

**参数说明：**
- `--team-id`：目标团队 ID（必填）
- `--team-name`：团队名称
- `--reference-date`：基准日期，默认今天（可选）
- `--output`：输出 JSON 文件路径

**JSON 输出结构（顶层）**：
```
meta: { teamId, teamName, referenceDate, threeMonthsAgo, twoMonthsAgo, oneMonthAgo, totalActivePlans, reportedAccIds }
noReportGroups: {
  threeMonths: { label, description, count, plans: [{ id, title, accId, accName, companyName, contractName, contractNum, status, statusDesc, startDate, endDate, executorList, checkTypeDesc, deliver, lastReportDate }] }
  twoMonths: { ... }
  oneMonth: { ... }
}
```

**excel-export 类型**，调用 `generate_plan_excel.py` 直接生成两个 Excel 文件（无需 Agent 生成 HTML）：

```bash
python $SKILL_DIR/scripts/generate_plan_excel.py \
  --months 3 \
  --threshold 20 \
  --output-dir .
```

**参数说明：**
- `--months N`：回溯月数（默认 3），与 `--from/--to` 互斥
- `--from YYYY-MM-DD`：起始日期
- `--to YYYY-MM-DD`：截止日期（默认今天）
- `--threshold N`：极低报工工时阈值，默认 20 小时
- `--filter field=keyword`：过滤条件，可多次指定（OR 逻辑）。支持字段：`checkType`（计划类型）、`title`（计划名称）、`companyName`（客户名称）、`executor`（执行人）、`contractNum`（合同编号）等。示例：`--filter checkType=巡检`
- `--output-dir PATH`：输出目录（默认当前目录）

**输出文件**：
- `零报工实施计划_{起始日期}至{截止日期}.xlsx` — 合计工时为 0
- `极低报工实施计划_{起始日期}至{截止日期}.xlsx` — 合计工时 > 0 且 < threshold
- 若指定 `--filter`，额外生成过滤子集文件（如 `巡检零报工实施计划_*.xlsx`）

**Agent 从用户请求中提取参数的映射规则**：
- "最近 N 个月" → `--months N`
- "1月到3月" → `--from 2026-01-01 --to 2026-03-31`
- "低于 10 小时" / "阈值 10" → `--threshold 10`
- "巡检" / "巡检类计划" → `--filter checkType=巡检`
- "维保计划" → `--filter checkType=维保`
- "某个客户" → `--filter companyName=客户名`
- "某个执行人" → `--filter executor=人名`

### Step 3：读取 JSON 数据

用 `read_file` 读取输出的 JSON 文件，解析数据结构。

### Step 4：生成 HTML 报告

Agent 根据 JSON 数据，按章节生成完整 HTML 文件。**所有 HTML 由 Agent 在本步骤中生成，不依赖预编码模板。**

**生成前必须读取**：
1. **`references/color-rules.md`** — 配色对比度规范、CSS 变量选择规则
2. **CSS 文件内容**（内嵌到 `<style>` 标签）：
   - 使用默认风格时：读取 `$SKILL_DIR/styles/default-design.css`
   - 使用其他风格时：读取 `default-design.css` + 对应风格 CSS（如 `apple-design.css`）

**按报告类型分支**：

#### work-report（默认）

读取 **`references/report-sections.md`** — 14 个章节的内容定义、字段映射、视觉规范、维度差异

#### plan-report（实施计划报工分析）

读取 **`references/plan-report-sections.md`** — 4 个章节（总览 + 3 个时间窗口明细表）的内容定义

**plan-report 不需要 `--from/--to` 时间范围**，自动以当天为基准往前推 3/2/1 个月。

#### excel-export（实施计划 Excel 报表）

**无需 Agent 生成 HTML**，`generate_plan_excel.py` 脚本已包含完整的 Excel 生成逻辑。执行完 Step 2 后直接进入 Step 5 输出文件。

支持的可选参数配置（从用户请求中提取）：
- 时间范围："最近 3 个月" → `--months 3`；"1月到4月" → `--from 2026-01-01 --to 2026-04-30`
- 阈值："低于 10 小时" → `--threshold 10`；未指定则默认 `--threshold 20`

**HTML 整体结构**（内嵌 CSS）：

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>{报告标题}</title>
  <style>
    /* 内嵌 CSS 内容 */
    /* default-design.css 内容... */
    /* 若使用其他风格，追加风格 CSS 内容... */
  </style>
</head>
<body>
  <!-- 报告内容 -->
</body>
</html>
```

**CSS 内嵌逻辑**：
- 默认风格：直接内嵌 `default-design.css` 全部内容
- 其他风格（如 Apple）：内嵌 `default-design.css` + `apple-design.css`（追加）
- 两段 CSS 合并时，风格 CSS 的变量会覆盖 default 的同名变量

**章节列表（1~14）**：

| 章 | 标题 | 核心数据源 |
|----|------|-----------|
| 1 | 团队核心指标对比 | `teams[*]` 顶层字段 |
| 2 | 成员工时明细 & 每日工时 | `teams[*].members[]` |
| 3 | 报工不足人员分析 | `teams[*].members[]`（full==false） |
| 4 | 文档编写统计 | `articles[]` |
| 5 | 项目成本消耗分析 | `teams[*].preHours/afterHours/internalHours` |
| 6 | 报工质量分析 | `scores[]` + `teams[*]` |
| 7 | 项目报工排名（TOP10） | `teams[*].projectRanking[]`（按accName+companyName聚合hours降序，取TOP10） |
| 8 | 每人每周工作总结 | `weeklyReports[]` |
| 9 | 服务请求列表 | `serviceRequests[]` |
| 10 | 服务请求统计 | `serviceRequestStats` |
| 11 | 项目未报工分析 | `projectUnreported` |
| 12 | 未报工人员名单（附属性） | `teams[*].unreportedMembers[]` |
| 13 | ~~综合评价~~ → **已合并至第一章** | 综合评价内容现于第一章展示 |

> 每个章节的详细字段映射、展示规则、维度差异，见 `references/report-sections.md`。

### Step 5：输出文件

**文件命名**：
- work-report：`{大区或团队}_报工看板_{日期区间}.html`
  - 🌍 区-团队示例：`东西大区报工看板_2026-04-21至04-23.html`
  - 👥 按团队示例：`东西大区4部报工看板_2026-04-21至04-23.html`
- plan-report：`{团队名}_实施计划报工分析_{基准日期}.html`
  - 示例：`东西大区4部_实施计划报工分析_2026-04-25.html`
- excel-export：由 `generate_plan_excel.py` 自动生成
  - `零报工实施计划_{起始日期}至{截止日期}.xlsx`
  - `极低报工实施计划_{起始日期}至{截止日期}.xlsx`

**输出路径**：默认输出到当前工作空间。

### Step 6：展示结果

使用 `preview_url` 工具以 `file://` 路径打开 HTML 预览。

---

## 关键注意事项

1. **数据安全**：`fetch_data.py` 产出的临时 JSON 文件（`/tmp/mes_report_data.json`、`/tmp/weekly_reports.json`）在报告生成完成后**必须删除**。
2. **JSON 读取**：mes CLI 返回值可能是 dict 或 list，`fetch_data.py` 已做 `isinstance` 防御，Agent 处理时也需注意。
3. **大区报告**：用户说"东西大区"时，查 4 个子团队（2,3,23,19），而非整体大区 ID（96）。
4. **标准工时**：默认 8h/天，可通过 `--std-hours-per-day` 调整。
5. **依赖**：Python 3.10+、已登录的 `mes` CLI。
6. **周报拉取**（第八章）：已默认开启，每条周报需单独调用 `view` 接口获取正文，调用量较大。

---

## 踩坑经验

- `statistics list` / 日期字段名：返回记录中没有 `taskDate`，日期在 `start` 字段（如 "2026-04-23 08:00:00"），需取 `[:10]`
- `statistics list` / 分页结构：返回 `{list:[], hasNextPage, endRow, ...}`，不是 `{operateCallBackObj:...}`
- `article list` / 分页结构：返回 `{list:[], total}`，作者字段是 `employeeName`（非 `createdByName`），时间字段是 `createdTime`（非 `createTime`）
- `dashboard score list` / 分页结构：返回 `{operateCallBackObj:{list:[], hasNextPage}}`，需要两层解包
- `service request list` / 日期参数：用 `--start-time` / `--end-time`（非 `--from` / `--to`），且需指定 `--person-id` 筛选范围
- `service request list` / 返回结构：返回 `{list:[], total}`
- `dashboard weeklyReport` / 周报正文：列表接口只返回简短摘要，完整正文需额外调用 `view {id}` 接口
- `dashboard weeklyReport` / view 接口返回结构：`{operateCallBackObj: {contentMd, content, employeeName, adminTeamName, ...}}`，需解一层
- `dashboard weeklyReport` / 周期字段：列表中有 `periodStartDate`/`periodEndDate`，`createdTime` 是提交时间，与报告周期不同
- `report-sections.md` 热力图 HTML 结构：日期标题行必须包裹在 `<div class="heatmap-row">` 内，否则 CSS `display: flex` 失效导致日期竖排
- 表格 `#`/`ID` 排名列：需显式设置 `style="width:30px"`（#列）或 `style="width:50px"`（ID列），否则浏览器默认列宽过大导致换行
