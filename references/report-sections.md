# 报告章节定义

> 本文件定义了报工看板的 14 个章节内容。Agent 在 Step 4 生成 HTML 时读取此文件。
> 两种报告维度（区-团队 / 直接按团队）的差异在各章节中用 **🌍 区-团队** 和 **👥 按团队** 标注。

---

## ⚠️ HTML 生成强制规范（必须严格遵守）

### 1. CSS 内嵌方式（推荐）

**✅ 推荐做法**：将 CSS 内容内嵌到 `<style>` 标签中，确保 HTML 文件可独立分享。

```html
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>{报告标题}</title>
  <style>
    /* CSS 内容直接写入此处 */
  </style>
</head>
```

**内嵌顺序**：
1. 先写入 `default-design.css` 的完整内容（组件类定义）
2. 若使用其他风格，追加对应风格 CSS 内容（变量覆盖）

**注意事项**：
- 团队色变量 `--tc` 可作为行内 `style="--tc:#hex;"` 传入（动态数据值）
- 内嵌模式下无需 `<link>` 标签
- CSS 内嵌后 HTML 文件可独立使用，无需携带外部 CSS 文件

### 2. 必须使用 CSS 文件已定义的类名

`default-design.css` 是唯一提供完整组件类名的 CSS 文件，其他风格文件（ps/notion/figma/starbucks/anthropic）**只提供 CSS 变量覆盖**，不重复定义组件类。

**因此，无论使用哪种风格，HTML 结构类名必须与 `default-design.css` 保持一致。** 风格切换只需替换 CSS 文件路径，HTML 结构不变。

#### 必须使用的类名对照表

| 元素 | ✅ 正确类名 | ❌ 错误类名（禁止） |
|------|-----------|----------------|
| 页面容器 | `.container` | `.page-wrap`、`.wrapper` |
| Hero 区域 | `.hero` + `<h1>` | `.hero-title`、`.hero-wrap` |
| Hero 副标题 | `.hero-subtitle` | `.hero-sub`、`.hero-desc` |
| Hero 徽章行 | `.hero-badges` + `.badge` | `.hero-tags`、`.tag` |
| 章节容器 | `.section` | `.chapter`、`.block` |
| 章节标题 | `.section-title` | `.section-header`（有特殊用途，见下）、`.ch-title` |
| 子标题（团队/子节分割） | `.section-header` | `.sub-title`、`.sub-section-title` |
| 汇总统计卡片网格 | `.stat-grid` | `.card-grid`、`.kpi-grid` |
| 汇总统计卡片 | `.stat-card` | `.card`、`.kpi-card` |
| 汇总卡片 - 标签 | `.stat-label` | `.card-label`、`.kpi-label` |
| 汇总卡片 - 数值 | `.stat-value` | `.card-value`、`.kpi-value` |
| 汇总卡片 - 补充说明 | `.stat-sub` | `.card-sub`、`.kpi-sub` |
| 团队卡片网格 | `.team-cards` | `.team-grid` |
| 团队卡片 | `.team-card` | `.t-card`、`.team-item` |
| 团队卡片 - 标题 | `<h4>` | `.team-card-name`、`.tc-title` |
| 团队卡片 - 指标行 | `.team-stat` | `.team-row`、`.tc-row` |
| 团队卡片 - 数值 | `.value`（`.team-stat` 内） | `.team-stat-value`、`.val` |
| 成员卡片网格 | `.member-cards` | `.member-grid` |
| 成员卡片 | `.member-card` | `.m-card`、`.person-card` |
| 成员卡片 - 标题 | `<h5>` | `.member-card-name` |
| 成员卡片 - 指标行 | `.member-stat` | `.m-row` |
| 数据表格容器 | `.table-scroll` | `.table-wrap`、`.overflow-x` |
| 数据表格 | `.data-table` | 裸 `table`、`.table`、`.report-table` |
| 热力图容器 | `.heatmap` | `.heat-wrap` |
| 热力图标题 | `.heatmap-title` | `.heat-title` |
| 热力图网格 | `.heatmap-grid` | `.heat-grid` |
| 热力图行 | `.heatmap-row` | `.heat-row` |
| 热力图名称列 | `.heatmap-name` | `.heat-name` |
| 热力图单元格 | `.heatmap-cell` + `.hm-0~3` | `.heat-cell`、`.hm-cell` |
| 进度条 | `.progress-bar` + `.progress-fill` | `.prog-bar`、`.bar-fill` |
| 警告/提示框 | `.alert` + `.alert-warning/success/danger` | `.tip`、`.notice` |
| 排名高亮 | `.rank-1/2/3` | `.medal-1/2/3`、`.gold/silver/bronze` |
| 页脚 | `.footer` | `.page-footer`、`.report-footer` |

#### CSS 颜色变量（只用这些，禁止硬编码颜色值）

| 变量 | 用途 |
|------|------|
| `var(--accent)` | 强调色（cyan/品牌色） |
| `var(--red)` | 危险/不足/警示 |
| `var(--green)` | 成功/满勤/通过 |
| `var(--orange)` | 警告/待改进 |
| `var(--text)` | 主文字色 |
| `var(--muted)` | 次要文字/标签 |
| `var(--card)` | 卡片背景 |
| `var(--card-alt)` | 卡片深色背景（表头等） |
| `var(--bg)` | 页面背景 |
| `var(--border)` | 分割线/边框 |
| `var(--report-success/warning/danger)` | 语义状态色 |

> ⚠️ 其他风格文件（ps/notion/figma/starbucks/anthropic）会通过 `:root` 变量覆盖上述变量的值，HTML 只要使用变量名，风格切换自动生效。**如果 HTML 里硬编码了 `#1a1a2e`、`rgba(0,212,255,...)` 等颜色，换风格后颜色不会变。**

#### stat-value 状态修饰符

```html
<div class="stat-value">64</div>           <!-- 默认 accent 色 -->
<div class="stat-value success">3</div>    <!-- 绿色 -->
<div class="stat-value warning">7.7%</div> <!-- 橙色 -->
<div class="stat-value danger">0%</div>    <!-- 红色 -->
```

### 3. 风格切换需追加对应 CSS 内容

不同风格报告的 HTML 结构**完全相同**，区别在于 `<style>` 标签内的 CSS 内容：

- **默认风格**：只内嵌 `default-design.css`
- **其他风格**：内嵌 `default-design.css` + 对应风格 CSS（如 `apple-design.css`）

两段 CSS 合并时，风格 CSS 的变量会覆盖 default 的同名变量，实现风格切换。

**CSS 文件读取顺序**：

| 风格 | 需读取的 CSS 文件 |
|------|------------------|
| 默认 | `default-design.css` |
| Apple | `default-design.css` + `apple-design.css` |
| PlayStation | `default-design.css` + `ps-design.css` |
| Starbucks | `default-design.css` + `starbucks-design.css` |
| Notion | `default-design.css` + `notion-design.css` |
| Figma | `default-design.css` + `figma-design.css` |
| Anthropic | `default-design.css` + `anthropic-design.css` |

### 4. 自查清单（生成 HTML 后必须检查）

生成 HTML 后，在写入文件前按此清单自查：

- [ ] 文件中包含 `<style>` 标签，内嵌完整的 CSS 内容
- [ ] 使用其他风格时，CSS 内容包含 `default-design.css` + 对应风格 CSS
- [ ] 所有类名均在上方"必须使用的类名对照表"中存在
- [ ] 不包含 `var(--text-primary-dark)`、`var(--text-secondary-light)` 等 **default-design.css 未定义**的变量
- [ ] 不包含硬编码颜色（如 `#0f3460`、`rgba(0,212,255,0.2)` 等）
- [ ] 每张 `.team-card` 的左边框色通过行内 `style="--tc:#hex"` 传入

---

---

## 报告维度说明

| 维度 | 触发条件 | 典型请求 | 数据特征 |
|------|---------|---------|---------|
| **🌍 区-团队** | 请求包含大区名，且大区下有多个子团队 | "南北大区报工看板"、"东西大区周报" | 多个团队属于同一大区，需要大区汇总 + 各团队对比 |
| **👥 按团队** | 请求指定具体团队名，或多个不属同一大区的团队 | "东西大区4部看板"、"2部和4部的报告" | 单团队或独立多团队，无大区层级 |

**维度判定逻辑**：
- 用户说"东西大区" / "南北大区" → 检查是否拉取了该大区下的多个子团队 → 是 → 🌍 区-团队
- 用户说"4部" / "2部和5部" → 👥 按团队
- 用户说"东西大区4部" → 单团队 → 👥 按团队
- 用户说"东西大区2部和4部"（同一大区但非全团队）→ **默认 👥 按团队**（因为不是完整大区对比），但 Hero 标题可体现大区归属

**维度对报告的影响**：

| 报告元素 | 🌍 区-团队 | 👥 按团队 |
|---------|-----------|----------|
| Hero 标题 | "{大区名}报工统计" | "{团队名}报工统计"（多团队用顿号连接） |
| Hero 副标题 | "覆盖 {N} 个团队 · {M} 人" | "{N} 人 · {工作日}个工作日" |
| 第一章 | 大区汇总卡片（总人数/总工时/均分）+ 各团队卡片 | 各团队卡片（无大区汇总层） |
| 第二章 | 按团队分节，每节内按成员列表 | 同左 |
| 第六章 | **必须有**团队横向对比表（A 表）| 单团队时省略 A 表，多团队时保留 |
| 第十章 | 按团队聚合服务统计 | 同左 |
| 第十三章 | ~~已合并至第一章~~ | ~~各团队独立评价~~ |
| 报告文件名 | `{大区名}_报工看板_{日期}.html` | `{团队名}_报工看板_{日期}.html` |

---

## 第一章：团队核心指标对比

**数据来源**：`teams[*]` 顶层字段

**展示内容**：

> **⚠️ 第一章不使用数据卡片（stat-card / team-card），只使用对比表格。**

- **🌍 区-团队**：大区整体评价 + 各团队评价 + 综合对比表格
  - 大区整体评价：汇总所有团队数据生成一段文字
  - 各团队评价：每队一段文字（总体评价 + 亮点 + 待改进）
  - **综合对比表格**：所有团队横向对比，列为 团队/人数/总工时/人均工时/满勤率/售前/售后/内部/加班/文档/均分
- **👥 按团队**：各团队评价 + 对比表格（多团队时）
  - 单团队时：一段评价文字 + 该团队关键指标表格
  - 多团队时：各团队评价 + 综合对比表格

**每个团队评价卡片包含**：

1. **总体评价**：根据满勤率、人均工时、质量评分综合生成一句话评价
   - 满勤率 ≥ 90% 且均分 ≥ 90："表现优异，报工规范、工时饱满"
   - 满勤率 70%-90%："整体良好，个别成员需关注"
   - 满勤率 < 70%："需重点关注，报工不足人员较多"
2. **亮点**：团队内工时排名前 3 的成员 + 文档产出较多者
3. **待改进**：报工不足人员（shortage > 0）名单
4. **服务统计**（若 `serviceStats` 存在）：待处理咨询、待处理工单、未关闭工单等

| 字段 | 说明 |
|------|------|
| teamName | 团队名称 |
| memberCount | 团队真实人数 |
| reportedMemberCount | 已报工人数 |
| totalHours | 总工时 |
| avgHours | 人均工时（已报工人员） |
| fullCount / fullRate | 满勤人数 / 满勤率 |
| overtimeHours | 加班工时 |
| preHours / afterHours / internalHours | 售前/售后/内部工时 |
| docCount | 文档数 |
| avgScore | 平均报工质量分 |

**视觉**：
- **禁止使用 stat-card / team-card 等卡片组件**
- 使用文字段落展示大区/团队评价
- 使用 `.data-table` 对比表格横向对比所有团队

---

## 第二章：成员工时明细 & 每日工时

**数据来源**：`teams[*].members[]`

**展示内容**：每个团队一个子节，内含成员表格 + 每日工时热力图

**成员表格列**：
| 列 | 类名 | 说明 |
|----|------|------|
| 姓名 | `col-name` | name |
| 城市 | `col-city` | city |
| 总工时 | `col-num` | total |
| 售前/售后/内部 | `col-num` | pre / after / internal |
| 加班 | `col-num` | overtime |
| 报工条数 | `col-num` | recordCount |
| 评分 | `col-num` | score |
| 不足工时 | `col-num` | shortage（>0 时红色显示） |

> **列宽约束**：姓名、城市等文本列必须加 `col-name`/`col-city` 类名，数字列加 `col-num` 类名。禁止裸 `<th>`/`<td>` 不加列宽类名。

**每日工时热力图**：
- 列 = 工作日（`meta.workDates`）
- 行 = 成员（按总工时降序）
- 单元格颜色 = 工时热力图配色
- 悬停显示具体数值

**HTML 结构规范（必须严格遵守）**：

日期标题行和成员行必须包裹在同一级 `<div class="heatmap-row">` 内，否则 CSS `display: flex` 布局失效，导致日期竖排。

```html
<div class="heatmap-grid">
  <!-- 标题行：必须包裹在 .heatmap-row 内 -->
  <div class="heatmap-row">
    <div class="heatmap-name">姓名</div>
    <div class="heatmap-cell hm-0">04-21</div>
    <div class="heatmap-cell hm-0">04-22</div>
    <div class="heatmap-cell hm-0">04-23</div>
    <div class="heatmap-cell hm-0">04-24</div>
  </div>
  <!-- 成员行 -->
  <div class="heatmap-row">
    <div class="heatmap-name">张三</div>
    <div class="heatmap-cell hm-2">8</div>
    <div class="heatmap-cell hm-3">9</div>
    <div class="heatmap-cell hm-0"></div>
    <div class="heatmap-cell hm-1">4</div>
  </div>
</div>
```

**❌ 错误结构（导致日期竖排）**：
```html
<div class="heatmap-grid">
  <div class="heatmap-row heatmap-name"></div>  <!-- 空行 -->
  <div class="heatmap-cell">04-21</div>        <!-- 日期在 .heatmap-row 外！ -->
  <div class="heatmap-cell">04-22</div>
  ...
</div>
```

---

## 第三章：报工不足人员分析

**数据来源**：`teams[*].members[]`（筛选 `full == false`）

**展示内容**：
- 汇总卡片：各团队不达标人数
- 详情表格：

| 列 | 类名 | 说明 |
|----|------|------|
| # | `col-rank` | 排名序号 |
| 姓名 | `col-name` | name |
| 团队 | `col-team` | teamName |
| 实际工时 | `col-num` | total |
| 标准工时 | `col-num` | stdHoursTotal |
| 不足工时 | `col-num` | shortage |
| 不足天数 | `col-num` | daily 中工时 < 8 的天数 |

> **列宽约束**：排名列用 `col-rank`，姓名列用 `col-name`，团队列用 `col-team`，数字列用 `col-num`。

---

## 第四章：文档编写统计

**数据来源**：`articles[]`

**展示内容**：
- 汇总卡片：总文档数、各团队文档数
- 表格：

| 列 | 说明 |
|----|------|
| 标题 | title |
| 作者 | `articles[]` 中的 `author`（映射自接口字段 `employeeName`） |
| 团队 | teamName |
| 创建时间 | `articles[]` 中的 `createTime`（映射自接口字段 `createdTime`） |

> ⚠️ `fetch_data.py` 中字段映射：`author` ← `employeeName`，`createTime` ← `createdTime`。直接读取 `articles[]` 时注意字段名差异。
> 若 `articles` 为空，显示"本周期内暂无文档产出"。

---

## 第五章：项目成本消耗分析（工时类型分布）

**数据来源**：`teams[*]` 的 `preHours` / `afterHours` / `internalHours`

**展示内容**：
- 各团队工时类型饼图或堆叠条形图
- 汇总表：团队 × 工时类型（售前POC / 售后服务 / 内部事项）
- 占比百分比

> Agent 可使用 CSS 实现简单条形图，或使用 Chart.js CDN 生成图表。

---

## 第六章：报工质量分析

**数据来源**：`scores[]` + `teams[*].members[]` + `teams[*]`

**展示内容**：

**A. 团队质量汇总对比表**

- **🌍 区-团队**：**必须**展示此表
- **👥 按团队**：多团队时展示，单团队时省略

| 团队 | 报工记录数 | 人均记录数 | 操作标准均分 | 零记录成员 | 质量评价 |
|------|-----------|-----------|------------|-----------|---------|

**列字段说明**：
| 列 | 数据来源 | 说明 |
|----|---------|------|
| 报工记录数 | `members[].recordCount` 汇总 | 该团队所有成员在本周期的报工条数之和 |
| 人均记录数 | `报工记录数 / memberCount`（取团队总人数，含未报工者） | 反映报工频率 |
| 操作标准均分 | `teams[].avgScore` | 直接取团队平均评分 |
| 零记录成员 | `teams[].unreportedMembers[]` | 本周期报工条数为 0 的成员名单，用顿号分隔；无则填"无" |
| 质量评价 | 人工判断 | 根据均分区间给出评价：≥95 优秀 / 85-94 良好 / 70-84 合格 / <70 待改进 |

**B. 个人评分明细表**

- 汇总卡片：各团队平均分
- 评分明细表：

| 列 | 说明 |
|----|------|
| 姓名 | executorName |
| 团队 | teamName |
| 评分 | score |
| 评级 | 根据 score 区间（≥95 优秀 / 85-94 良好 / 70-84 合格 / <70 待改进） |
| 建议 | suggestion（截断显示，hover 完整） |

> 若 `scores` 为空，显示"本周期暂无评分数据"。

---

## 第七章：项目报工排名（各团队 TOP10）

**数据来源**：`teams[*].projectRanking[]`（已在 `fetch_data.py` 中按 `accName` + `companyName` 聚合 `taskTime` 生成）

**数据生成逻辑**（在 `fetch_data.py` 中完成）：
1. 对每个成员，遍历其 `statistics list` 原始记录
2. 按 `accName`（项目名称）+ `companyName`（公司名称）聚合 `taskTime`
3. 记录参与该项目的成员名单
4. 每团队取工时排名前 10 的项目

**展示内容**：每个团队一张子节，内含项目排行表：

| 列 | 说明 |
|----|------|
| 排名 | 序号（1～10），`<th>` 需设 `style="width:30px"` 防止过宽 |
| 项目名称 | name（accName） |
| 客户公司 | company（companyName） |
| 总工时 | hours |
| 参与人数 | memberCount |
| 占团队比 | hours / team.totalHours（百分比） |
| 参与成员 | members（顿号分隔，超3人截断，hover 显示完整） |

**视觉**：
- 按总工时降序排列
- 前3名用 🥇🥈🥉 或颜色区分（🥇 #FFD700 / 🥈 #C0C0C0 / 🥉 #CD7F32）
- 第4名及之后用普通表格行
- 表格内成员名单超出3人时截断显示，hover 显示完整
- 若某团队无报工记录，显示"本周期暂无项目报工数据"

**🆕 重要澄清**：
- ❌ 本章**不是**个人工时排名（那是第四章的内容）
- ✅ 本章是**团队在项目/客户上的报工工时**排名

---

## 第八章：每人每周工作总结

**数据来源**：`weeklyReports[]`（默认拉取）

**数据拉取方式**（`fetch_data.py` 内部完成）：
1. 调用 `mes -o json dashboard weeklyReport --period-from {from} --period-to {to} --type WEEKLY --page-size 50` 枚举周报列表
2. 对每条周报，调用 `mes -o json dashboard weeklyReport view {id}` 获取完整正文（`contentMd`）
3. 按 `createdBy`（userId）筛选目标团队成员后，按 `adminTeamName` 分组
4. 输出结构：

```json
"weeklyReports": [
  {
    "teamName": "南北大区4部",
    "reports": [
      {
        "id": 362,
        "employeeName": "周瑞斌",
        "userId": 6536,
        "teamName": "南北大区4部",
        "periodStartDate": "2026-04-13",
        "periodEndDate": "2026-04-19",
        "createdTime": "2026-04-20 09:10:18",
        "contentMd": "# 重点项目进度\n1.新疆农信...",
        "content": "<h1>重点项目进度</h1>..."
      }
    ]
  }
]
```

**展示内容**：
- **🌍 区-团队**：按团队分节，每个团队下按人员分组，每人一张卡片
- **👥 按团队**：直接按人员分组，每人一张卡片
- 每人卡片包含：姓名、汇报周期、提交时间、周报正文摘要（截取前 300 字，用 `…` 结尾）
- 点击卡片展开完整周报正文（支持 Markdown 渲染）

**展示逻辑**：
| 报告类型 | 展示范围 |
|---------|---------|
| 大区（多团队） | 只展示有周报的团队（无周报的团队不占章节） |
| 单团队 | 展示该团队所有有周报的成员 |

---

## 第九章：服务请求列表

**数据来源**：`serviceRequests[]`（已按团队成员范围筛选）

**展示内容**：
- 汇总卡片：总服务请求数、各团队服务请求数
- 表格：

| 列 | 说明 |
|----|------|
| ID | id，`<th>` 需设 `style="width:50px"` 防止过宽 |
| 标题 | title |
| 状态 | status（中文） |
| 等级 | type（P0-P5） |
| 负责人 | executorEmployeeName |
| 申报时间 | createdTime |
| 公司 | companyName |

> 状态映射：0=已提交, 1=处理中, 2=已关闭, 3=已归档, 4=待反馈, 5=业务已恢复

---


## 第十章：服务请求统计


**聚合逻辑**：

- 对 `serviceRequests[]` 按 `companyName` 聚合：统计每家客户的总请求数、开放数、关闭数
- 对 `serviceRequests[]` 按 `executorEmployeeName` 聚合：统计每人处理的总请求数、开放数、关闭数
- 开放状态：`status` 为 0（已提交）/1（处理中）/4（待反馈）；其余为已关闭

**输出 JSON 结构**：

```json
"serviceRequestStats": {
  "byCompany": [
    {"companyName": "永辉超市", "count": 5, "open": 1, "closed": 4}
  ],
  "byExecutor": [
    {"executorName": "肖杰", "teamName": "南北大区5部", "count": 3, "open": 0, "closed": 3}
  ]
}
```

**展示内容**：两个并排表格

**A. 按客户统计**

| 列       | 说明                                         |
| -------- | -------------------------------------------- |
| 排名     | 序号（按 count 降序），`<th>` 需设 `style="width:30px"` |
| 客户名称 | companyName                                  |
| 请求总数 | count                                        |
| 开放数   | open（已提交/处理中/待反馈）                |
| 已关闭数 | closed                                       |
| 关闭率   | closed / count（百分比）                     |

**B. 按处理人统计**

| 列       | 说明                                         |
| -------- | -------------------------------------------- |
| 排名     | 序号（按 count 降序），`<th>` 需设 `style="width:30px"` |
| 处理人   | executorName                                 |
| 所属团队 | teamName                 |
| 请求总数 | count                    |
| 开放数   | open                     |
| 已关闭数 | closed                   |
| 关闭率   | closed / count（百分比） |

**视觉**：

- 两个表格并排展示（左右各一，或上下分节）
- 关闭率 ≥ 80% 绿色，50%-80% 橙色，< 50% 红色
- 前3名高亮（金/银/铜色）
- 若服务请求为空，显示"本周期暂无服务请求数据"

---

## 第十一章：项目未报工分析

**数据来源**：`projectUnreported`（默认拉取）

**数据拉取方式**（`fetch_data.py` 内部完成）：

1. 调用 `contract list` 获取目标团队的合同列表（含 `contractNum`、`serviceTeams`）
2. 调用 `contract list-items` 按宽日期窗口（过去6个月～未来12个月）拉取所有子项
3. 按 `contractNum` 聚合子项，筛选**合同未结束**（`contractEndTime >= today`）的合同
4. 对每个合同，按 `actualHours == 0` 区分"未报工子项"与"已报工子项"

**在服合同判定**：合同主表 `contractEndTime`（或子项中最大 `endTime`）≥ 今日

**输出 JSON 结构**：

```json
"projectUnreported": {
  "summary": {
    "totalContracts": 27,
    "zeroContracts": 12,
    "mixedContracts": 15,
    "totalZeroItemPlanHours": 53468
  },
  "contracts": [
    {
      "contractNum": "00031855",
      "contractName": "2025年百瑞信托数据库运维服务项目",
      "companyName": "百瑞信托",
      "contractOwner": "丁向辉",
      "contractStartTime": "2025-12-15",
      "contractEndTime": "2026-12-30",
      "serviceTeams": ["南北大区维保项目服务团队"],
      "totalPlanHours": 4800,
      "totalActualHours": 0,
      "totalRemainingHours": 4800,
      "itemCount": 8,
      "zeroItemCount": 8,
      "nonZeroItemCount": 0,
      "zeroItems": [
        {
          "itemName": "oracle常规巡检",
          "itemType": "巡检服务",
          "planHour": 64,
          "actualHours": 0,
          "remainingHours": 64,
          "startTime": "2026-01-01",
          "endTime": "2026-12-31",
          "ownerName": "丁向辉"
        }
      ],
      "nonZeroItems": []
    }
  ]
}
```

**展示内容**：

**A. 汇总卡片**（顶部）

| 卡片                     | 说明                                       |
| ------------------------ | ------------------------------------------ |
| 有未报工子项的合同       | `zeroContracts + mixedContracts`           |
| 未报工子项               | 所有 `zeroItemCount` 之和                  |
| 已报工子项（合同在交付） | 所有 `nonZeroItemCount` 之和（仅混合合同） |
| 未报工剩余工时           | `summary.totalZeroItemPlanHours`（h）      |

**B. 合同列表**（按未报工子项数降序）

每个合同一张卡片，包含：

| 字段         | 说明                                   |
| ------------ | -------------------------------------- |
| 合同名称     | contractName（来自合同主表）           |
| 客户公司     | companyName                            |
| 负责人       | contractOwner                          |
| 合同周期     | contractStartTime ~ contractEndTime    |
| 未报工计划   | 该合同下所有未报工子项的 planHour 之和 |
| 剩余         | 同上（因实际为0即等于计划）            |
| 未报工子项数 | zeroItemCount                          |

**C. 子项明细表**（合同卡片内折叠展开）

| 列       | 说明                                        |
| -------- | ------------------------------------------- |
| 子项名称 | itemName                                    |
| 类型     | itemType（人天服务/巡检服务/一般维保/软件） |
| 计划工时 | planHour                                    |
| 实际工时 | actualHours（0时红色高亮）                  |
| 剩余工时 | remainingHours（含进度条）                  |

**视觉**：

- 合同卡片分两类：纯未报工合同（全部子项 actualHours=0）和混合合同（有部分已报工）
- 汇总卡片：合同数和未报工子项数用红色，剩余工时用橙色，已报工子项数用绿色
- 子项明细表：actualHours=0 的行用淡红色背景高亮
- 默认折叠子项明细表，点击合同卡片展开
- 合同按未报工子项数降序排列

> 若目标团队无合同数据，显示"本周期目标团队暂无合同数据"。

---

## 第十二章：未报工人员名单（附属于第三章展示）

**数据来源**：`teams[*].unreportedMembers[]`

**展示内容**：

- 汇总卡片：各团队未报工人数
- 表格：

| 列     | 说明     |
| ------ | -------- |
| 姓名   | name     |
| 团队   | teamName |
| userId | userId   |

> 若所有团队均无未报工人员，显示"本周期所有团队成员已完成报工 ✅"。

---

## 附录：MES CLI 命令参考

> **重要**：所有命令均使用 `mes -o json` 输出 JSON 格式。本附录列出每个章节对应的 mes 命令，包括参数格式、返回结构解析、分页处理方式。

### A. 通用参数约定

| 参数 | 格式 | 说明 |
|------|------|------|
| 日期范围 | `--from YYYY-MM-DD --to YYYY-MM-DD` | 用于 statistics / article 等接口 |
| 团队 ID | `--team-id {id}` | 每次查一个团队，多团队循环调用 |
| 分页 | `--page {n} --page-size 50` | 大多数列表接口支持 |
| 时间戳范围 | `--start-time "YYYY-MM-DD HH:MM:SS" --end-time "YYYY-MM-DD HH:MM:SS"` | 用于 service request / article 等 |

### B. 各章节对应的 mes 命令

#### 第一章 / 第二章 / 第三章 / 第五章（核心报工数据）

```bash
# 1. 获取团队成员列表（用于计算 memberCount 和识别未报工人员）
mes -o json util list-members --team-id {team-id}

# 2. 获取团队报工汇总（含每个成员的 totalTaskTime / preTaskTime / afterTaskTime / internalHours / overTaskTime / docCount / operationStandardScore）
mes -o json statistics summary --team-id {team-id} --from {from} --to {to}

# 3. 获取成员每日工时详情（用于热力图和 recordCount）
mes -o json statistics list --executor-id {user-id} --from {from} --to {to} --page {n} --page-size 100
# 分页：返回 {list: [...], hasNextPage: bool}，翻完为止
# 日期字段：返回记录中无 taskDate，日期在 start 字段（如 "2026-04-23 08:00:00"），取 raw_date[:10] 得 "2026-04-23"
# 项目聚合：按 accName + companyName 聚合 taskTime，得 projectRanking
```

**第一章展示字段计算逻辑**：
```
teamTotalHours = sum(m.totalTaskTime)
teamFullCount = count(m.totalTaskTime >= stdTotalHours)
teamFullRate = teamFullCount / len(members) * 100
```

---

#### 第四章（文档统计）

```bash
mes -o json article list \
  --team-id {team-id} \
  --start-time "{from} 00:00:00" \
  --end-time "{to} 23:59:59" \
  --mode manage \
  --page {n} --page-size 50
# 返回 {list: [...], total: N}，翻完为止
# 关键字段：title, employeeName（作者）, createdTime
```

---

#### 第六章（报工质量评分）

```bash
mes -o json dashboard score list \
  --team-id {team-id} \
  --month {YYYY-MM} \
  --page {n} --page-size 50
# 返回 {operateCallBackObj: {list: [...], hasNextPage: bool}}
# 关键字段：executorName, score, suggestion
```

---

#### 第七章（项目报工排名 TOP10）

数据来自第二章的 `statistics list` 原始记录，在 `fetch_data.py` 中按 `accName + companyName` 聚合 `taskTime` 生成，无需额外命令。

**聚合 SQL 逻辑（Python）**：
```python
team_projects = {}  # key: (accName, companyName), val: {hours: float, members: set}
for r in records:
    acc_key = (r.get("accName") or "其他项目", r.get("companyName") or "未知公司")
    if acc_key not in team_projects:
        team_projects[acc_key] = {"hours": 0.0, "members": set()}
    team_projects[acc_key]["hours"] += r.get("taskTime", 0)
    team_projects[acc_key]["members"].add(r.get("userName", ""))
# 排序取 TOP10
project_ranking = sorted([...], key=lambda x: -x["hours"])[:10]
```

---

#### 第八章（每人每周工作总结）

```bash
# 枚举周报列表
mes -o json dashboard weeklyReport \
  --period-from {from} \
  --period-to {to} \
  --type WEEKLY \
  --page {n} --page-size 50
# 返回 {list: [{id, employeeName, adminTeamName, periodStartDate, periodEndDate, createdBy, ...}]}

# 拉取单条周报正文
mes -o json dashboard weeklyReport view {report-id}
# 返回 {operateCallBackObj: {contentMd, content, employeeName, adminTeamName, ...}}
# 需解一层：obj = data.get("operateCallBackObj", {})
```

---

#### 第九章 / 第十章（服务请求）

```bash
# 拉取指定人员的服务请求
mes -o json service request list \
  --person-id {user-id} \
  --start-time "{from} 00:00:00" \
  --end-time "{to} 23:59:59" \
  --page-size 100
# 返回 {list: [...], total: N}
# 关键字段：id, title, status, type, executorEmployeeName, companyName, createdTime
# 状态映射：0=已提交, 1=处理中, 2=已关闭, 3=已归档, 4=待反馈, 5=业务已恢复
# 开放状态：status in (0, 1, 4)
```

**第十章聚合逻辑**：
```python
by_company = defaultdict(lambda: {"count": 0, "open": 0, "closed": 0})
by_executor = defaultdict(lambda: {"teamName": "", "count": 0, "open": 0, "closed": 0})
for s in service_requests:
    is_open = s.get("status", 0) in (0, 1, 4)
    by_company[s.companyName]["count"] += 1
    by_company[s.companyName]["open" if is_open else "closed"] += 1
    # 同理按 executorEmployeeName 聚合
```

---

#### 第十一章（项目未报工分析）

```bash
# 1. 拉取合同列表（匹配目标团队）
mes -o json contract list --page {n} --page-size 50
# 返回 {list: [...]} 或 {operateCallBackObj: {list: [...]}}
# 关键字段：id, contractNum, name, companyName, contractOwner, contractStartTime, contractEndTime, serviceTeams

# 2. 拉取合同子项（宽窗口：过去6个月～未来12个月）
mes -o json contract list-items \
  --date-range-start {6个月前} \
  --date-range-end {12个月后} \
  --page {n} --page-size 50
# 返回 {operateCallBackObj: {list: [...], hasNextPage: bool}}
# 关键字段：contractNum, itemName, itemType, planHour, actualHours, diffHours, startTime, endTime, ownerName
# 筛选条件：actualHours == 0 → 未报工子项
# 在服合同判定：contractEndTime >= today
```

---

#### 第一章·综合评价（附录）

> 本节补充综合评价所需数据（已并入第一章）。不独立拉取，数据来自前序各章节的聚合。

```bash
# 全局服务统计（用于第一章综合评价中的服务统计卡片）
mes -o json dashboard service
# 返回 {pendingConsultCount, pendingWorkOrderCount, planCount, unclosedWorkOrderCount, ...}

# 部门工时分布表（用于第一章大区整体评价的工时对比）
mes -o json dashboard task-table --from {from} --to {to}
# 返回 {operateCallBackObj: [{teamId, teamName, totalHours, ...}]}
```

**第一章·综合评价数据来源一览**：

| 数据 | 来源章节 | 说明 |
|------|---------|------|
| 满勤率 / 人均工时 | 第一章（statistics summary） | 各团队汇总 |
| 质量评分 | 第六章（dashboard score list） | 团队均分 |
| 服务统计 | `dashboard service` | 待处理咨询、工单数 |
| 服务请求 | 第九章/第十章（service request list） | 按客户/处理人聚合 |

---

### C. 常用团队 ID 速查

| 团队名称 | team-id | 备注 |
|---------|---------|------|
| 东西大区1部 | 2 | |
| 东西大区2部 | 3 | |
| 东西大区4部 | 23 | |
| 东西大区5部 | 19 | |
| 东西大区（整体） | 96 | 含所有子部门，不区分团队 |
| 南北大区2部 | 25 | |
| 南北大区4部 | 11 | |
| 南北大区5部 | 22 | |
| 南北大区（整体） | 94 | 含所有子部门，不区分团队 |
| 东西大区4个服务团队 | `[2, 3, 23, 19]` | 区-团队报告用 |
| 南北大区3个服务团队 | `[25, 11, 22]` | 区-团队报告用 |

**注意**：大区整体 ID（96/94）无法区分子团队，对比报告需逐一调用各子团队。

---

### D. 数据解析规范

**分页结构一览表**：

| 接口 | 分页字段 | 解包路径 |
|------|---------|---------|
| `statistics summary` | 无 | `{operateCallBackObj: [...]}` |
| `statistics list` | `hasNextPage` | `{list: [...], hasNextPage}` |
| `article list` | `total` | `{list: [...], total}` |
| `dashboard score list` | `hasNextPage` | `{operateCallBackObj: {list, hasNextPage}}` |
| `service request list` | `total` | `{list: [...], total}` |
| `dashboard weeklyReport` | 无 | `{list: [...]}` |
| `dashboard weeklyReport view` | 无 | `{operateCallBackObj: {...}}` |
| `contract list` | 无 | `{list: [...]}` 或 `{operateCallBackObj: {list: [...]}}` |
| `contract list-items` | `hasNextPage` | `{operateCallBackObj: {list, hasNextPage}}` |
| `dashboard task-table` | 无 | `{operateCallBackObj: [...]}` |

**通用提取函数**（已在 `fetch_data.py` 中实现）：
```python
def _extract_list(data):
    if isinstance(data, list): return data
    if isinstance(data, dict):
        for key in ("list", "operateCallBackObj", "data"):
            val = data.get(key)
            if isinstance(val, list): return val
            if isinstance(val, dict):
                inner = val.get("list")
                if isinstance(inner, list): return inner
    return []
```

