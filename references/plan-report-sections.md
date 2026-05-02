# 实施计划报工分析 — 章节定义

> 本文件定义了实施计划报工分析报告的章节内容。Agent 在 Step 4（plan-report 类型）生成 HTML 时读取此文件。

---

## HTML 生成规范

与报工看板共用同一套 CSS 类名和变量系统，详见 `report-sections.md` 的「必须使用的类名对照表」和 `color-rules.md`。

---

## 报告结构

### Hero 区域

```
标题：{teamName} 实施计划报工分析
副标题：基准日期 {referenceDate} · {totalActivePlans} 个进行中计划 · {reportedAccIds} 个近期有报工
徽章行：
  - "3个月无报工 {count}"  (danger 色调)
  - "2个月无报工 {count}"  (warning 色调)
  - "1个月无报工 {count}"  (orange 色调)
```

### 第一章：总览

**3 个统计卡片（`.stat-grid` 内）**：

| 卡片 | 数值变量 | 说明 |
|------|---------|------|
| 3个月无报工 | `noReportGroups.threeMonths.count` | 最严重，自 {threeMonthsAgo} 起无任何报工 |
| 2个月无报工 | `noReportGroups.twoMonths.count` | 排除 3 个月组，最后报工在 3~2 个月前 |
| 1个月无报工 | `noReportGroups.oneMonth.count` | 排除更长周期组，最后报工在 2~1 个月前 |

- 3 个月无报工卡片数值使用 `var(--red)` 色
- 2 个月无报工卡片数值使用 `var(--orange)` 色
- 1 个月无报工卡片数值使用 `var(--accent)` 色
- # 每张卡片 `.stat-sub` 显示描述文本

### 第二章：3 个月无报工明细

**条件**：`noReportGroups.threeMonths.count > 0` 时显示，否则显示 `.alert.alert-success` 提示"所有进行中计划在近 3 个月内均有报工记录"。

**表格（`.data-table`）列定义**：

| # | 列名 | 字段 | 宽度 | 说明 |
|---|------|------|------|------|
| 1 | # | 序号 | 40px | 自增 |
| 2 | 实施计划 | title | — | 主标识列，加粗 |
| 3 | 合同子项 | accName | — | |
| 4 | 客户 | companyName | — | |
| 5 | 合同编号 | contractNum | 120px | |
| 6 | 负责人 | executorList | 120px | 多人用 `、` 分隔，显示 executorName |
| 7 | 类型 | checkTypeDesc | 70px | 居中 |
| 8 | 计划起止 | startDate ~ endDate | 200px | 格式 `MM/DD ~ MM/DD` |
| 9 | 最后报工 | lastReportDate | 100px | 无则显示 "—" 用 `var(--muted)` 色；有则显示日期 |

**表格行样式**：
- 奇数行 `rgba(255,255,255,0.03)` 斑马纹
- hover 高亮

### 第三章：2 个月无报工明细

结构与第二章相同，数据源为 `noReportGroups.twoMonths.plans`。

章节标题旁加描述：`最后报工在 {threeMonthsAgo} ~ {twoMonthsAgo} 之间`。

### 第四章：1 个月无报工明细

结构与第二章相同，数据源为 `noReportGroups.oneMonth.plans`。

章节标题旁加描述：`最后报工在 {twoMonthsAgo} ~ {oneMonthAgo} 之间`。

### 页脚

```
{teamName} 实施计划报工分析 · 基准日期 {referenceDate} · 数据来源：MES
```

---

## 空数据展示规则

| 场景 | 展示方式 |
|------|---------|
| 某分组为空（count=0） | 显示 `.alert.alert-success`："该时间段内无未报工计划" |
| 所有分组都为空 | Hero 副标题改为"所有进行中计划近期均有报工"，第一章显示成功提示 |
| 无进行中计划 | Hero 显示"当前无进行中的实施计划"，跳过所有章节 |
