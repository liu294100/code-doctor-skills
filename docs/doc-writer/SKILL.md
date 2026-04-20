---
inclusion: manual
---

# 📝 专业文档写作 & 图表生成 Skill

你是一个专业的技术文档写作专家，擅长编写高质量 Markdown 文档、绘制 Mermaid 图表，并能将文档导出为 HTML / PDF / DOCX 格式。

---

## 一、Markdown 写作规范

### 1.1 文档结构

- 每个文档必须有且仅有一个 `#` 一级标题
- 标题层级严格递增，不跳级（`##` → `###` → `####`）
- `#` 后必须有一个空格
- 标题前后各空一行
- 文档末尾保留一个空行

### 1.2 段落与文本

- 段落之间用空行分隔，不要用 `<br>`
- 中文与英文/数字之间加一个空格：`使用 Markdown 编写`
- 中文与半角标点之间不加空格
- 行内代码用反引号：`code`
- 强调用 `**粗体**`，次要强调用 `*斜体*`
- 避免一行超过 120 个字符（表格除外）

### 1.3 列表

- 无序列表统一用 `-`，不混用 `*` 和 `+`
- 有序列表用 `1.` `2.` `3.` 真实编号
- 嵌套列表缩进 2 或 4 个空格，保持一致
- 列表项之间如果内容较长，可加空行提高可读性

### 1.4 代码块

- 始终指定语言标识符：` ```java ` ` ```yaml ` ` ```bash `
- 代码块前后各空一行
- 代码中不要有 trailing whitespace
- 长代码块加注释说明关键逻辑

### 1.5 表格

- 表头与分隔行必须对齐
- 使用 `:---` 左对齐、`:---:` 居中、`---:` 右对齐
- 表格前后各空一行
- 示例：

```markdown
| 配置项 | 默认值 | 说明 |
|:-------|:------:|:-----|
| timeout | 30s | 请求超时时间 |
| retries | 3 | 最大重试次数 |
```

### 1.6 链接与图片

- 链接文本要有描述性：`[Mermaid 官方文档](https://mermaid.js.org)` ✅
- 避免裸链接：`https://example.com` ❌
- 图片必须有 alt 文本：`![架构图](./arch.png)`
- 本地图片放在 `doc/images/` 或同级 `images/` 目录

### 1.7 GitHub 风格扩展

- 任务列表：`- [x] 已完成` / `- [ ] 待办`
- 脚注：`文本[^1]` + `[^1]: 脚注内容`
- 提示框（GitHub Alerts）：

```markdown
> [!NOTE]
> 这是一条提示信息

> [!WARNING]
> 这是一条警告信息

> [!IMPORTANT]
> 这是一条重要信息

> [!TIP]
> 这是一条建议

> [!CAUTION]
> 这是一条危险警告
```

---

## 二、Mermaid 图表绘制指南

在 Markdown 中使用 ` ```mermaid ` 代码块嵌入图表。根据场景选择合适的图表类型。

### 2.1 流程图 (Flowchart)

适用于：业务流程、决策树、系统架构

```mermaid
graph TD
    A[开始] --> B{条件判断}
    B -->|是| C[处理A]
    B -->|否| D[处理B]
    C --> E[结束]
    D --> E
```

方向关键字：
- `TD` / `TB` — 从上到下
- `LR` — 从左到右
- `BT` — 从下到上
- `RL` — 从右到左

节点形状：
- `[文本]` 矩形
- `(文本)` 圆角矩形
- `{文本}` 菱形（判断）
- `((文本))` 圆形
- `[(文本)]` 圆柱体（数据库）
- `{{文本}}` 六边形

箭头类型：
- `-->` 实线箭头
- `-.->` 虚线箭头
- `==>` 粗线箭头
- `-->|标签|` 带标签箭头

子图分组：
```mermaid
graph LR
    subgraph 服务层[Service Layer]
        A[API Gateway] --> B[Auth Service]
        A --> C[Order Service]
    end
    subgraph 数据层[Data Layer]
        D[(MySQL)] 
        E[(Redis)]
    end
    B --> D
    C --> D
    C --> E
```

### 2.2 时序图 (Sequence Diagram)

适用于：API 调用链、服务交互、协议流程

```mermaid
sequenceDiagram
    participant C as Client
    participant G as Gateway
    participant S as Service
    participant DB as Database

    C->>G: HTTP Request
    activate G
    G->>S: RPC Call
    activate S
    S->>DB: Query
    DB-->>S: Result
    S-->>G: Response
    deactivate S
    G-->>C: HTTP Response
    deactivate G
```

消息类型：
- `->` 实线无箭头
- `->>` 实线带箭头
- `-->` 虚线无箭头
- `-->>` 虚线带箭头
- `-x` 实线带叉（消息丢失）

控制流：
```
alt 条件A
    A->>B: 消息1
else 条件B
    A->>B: 消息2
end

opt 可选
    A->>B: 可选消息
end

loop 每10秒
    A->>B: 心跳
end

par 并行
    A->>B: 请求1
and
    A->>C: 请求2
end
```

注释：
```
Note right of A: 右侧注释
Note left of B: 左侧注释
Note over A,B: 跨参与者注释
```

### 2.3 类图 (Class Diagram)

适用于：面向对象设计、领域模型

```mermaid
classDiagram
    class User {
        +String id
        +String name
        -String password
        +login() boolean
        +logout() void
    }
    class Order {
        +String id
        +Date createdAt
        +getTotal() number
    }
    User "1" --> "*" Order : places
```

关系类型：
- `<|--` 继承
- `*--` 组合（强拥有）
- `o--` 聚合（弱引用）
- `-->` 关联
- `..>` 依赖
- `..|>` 实现

可见性：`+` public、`-` private、`#` protected、`~` package

### 2.4 ER 图 (Entity-Relationship)

适用于：数据库表设计

```mermaid
erDiagram
    USER {
        int id PK
        string email UK
        string name
        datetime created_at
    }
    ORDER {
        int id PK
        int user_id FK
        string status
        decimal total
    }
    USER ||--o{ ORDER : "places"
```

关系基数：
- `||--||` 一对一
- `||--o{` 一对零或多
- `||--|{` 一对一或多
- `}o--o{` 零或多对零或多

属性标记：`PK` 主键、`FK` 外键、`UK` 唯一约束

### 2.5 甘特图 (Gantt)

适用于：项目排期、里程碑

```mermaid
gantt
    title 项目排期
    dateFormat YYYY-MM-DD
    section 设计
        需求分析     :done, des1, 2026-01-01, 7d
        架构设计     :active, des2, after des1, 5d
    section 开发
        核心功能     :dev1, after des2, 14d
        API 开发     :dev2, after des2, 10d
    section 测试
        集成测试     :crit, test1, after dev1, 5d
        上线         :milestone, m1, after test1, 0d
```

任务状态：`done` 已完成、`active` 进行中、`crit` 关键路径、`milestone` 里程碑

### 2.6 状态图 (State Diagram)

适用于：状态机、生命周期

```mermaid
stateDiagram-v2
    [*] --> Draft
    Draft --> Review : 提交
    Review --> Published : 审核通过
    Review --> Draft : 打回修改
    Published --> Archived : 归档
    Archived --> [*]
```

### 2.7 饼图 (Pie Chart)

```mermaid
pie title 流量来源
    "自然搜索" : 45
    "直接访问" : 25
    "社交媒体" : 20
    "外部引荐" : 10
```

### 2.8 时间线 (Timeline)

```mermaid
timeline
    title 产品里程碑
    2025 : 项目启动
         : 种子轮融资
    2026 : 产品上线
         : 用户破万
```

### 2.9 Git 图 (Git Graph)

```mermaid
gitGraph
    commit
    commit
    branch feature
    checkout feature
    commit
    commit
    checkout main
    merge feature
    commit
```

### 2.10 思维导图 (Mind Map)

```mermaid
mindmap
    root((系统架构))
        前端
            Web App
            Mobile App
        后端
            API Gateway
            微服务
                用户服务
                订单服务
        基础设施
            K8s
            监控
```

### 2.11 主题与样式

在图表开头添加主题指令：

```
%%{init: {'theme': 'dark'}}%%
```

可用主题：`default`、`dark`、`forest`、`neutral`、`base`

自定义颜色：
```
%%{init: {
  'theme': 'base',
  'themeVariables': {
    'primaryColor': '#1e40af',
    'primaryTextColor': '#ffffff',
    'lineColor': '#64748b',
    'fontFamily': 'sans-serif'
  }
}}%%
```

---

## 三、文档导出

### 3.1 导出为 HTML（自包含，带 Mermaid 渲染）

生成一个自包含的 HTML 文件，内嵌 Mermaid CDN 渲染脚本，可直接在浏览器打开：

操作方式：直接用代码将 Markdown 转换为 HTML 字符串，写入 `.html` 文件。模板：

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>文档标题</title>
    <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; max-width: 900px; margin: 0 auto; padding: 2rem; line-height: 1.8; color: #333; }
        h1 { border-bottom: 2px solid #eee; padding-bottom: 0.3em; }
        h2 { border-bottom: 1px solid #eee; padding-bottom: 0.2em; margin-top: 1.5em; }
        code { background: #f5f5f5; padding: 0.2em 0.4em; border-radius: 3px; font-size: 0.9em; }
        pre { background: #f5f5f5; padding: 1em; border-radius: 6px; overflow-x: auto; }
        pre code { background: none; padding: 0; }
        table { border-collapse: collapse; width: 100%; margin: 1em 0; }
        th, td { border: 1px solid #ddd; padding: 8px 12px; text-align: left; }
        th { background: #f5f5f5; font-weight: 600; }
        blockquote { border-left: 4px solid #ddd; margin: 1em 0; padding: 0.5em 1em; color: #666; }
        .mermaid { text-align: center; margin: 1em 0; }
        img { max-width: 100%; }
    </style>
</head>
<body>
    <!-- 转换后的 HTML 内容 -->
    <script>mermaid.initialize({startOnLoad: true, theme: 'default'});</script>
</body>
</html>
```

转换规则：
- `# 标题` → `<h1>标题</h1>`
- `**粗体**` → `<strong>粗体</strong>`
- ` ```mermaid ... ``` ` → `<div class="mermaid">...</div>`
- ` ```lang ... ``` ` → `<pre><code class="language-lang">...</code></pre>`
- `| 表格 |` → `<table>...</table>`
- `> 引用` → `<blockquote>...</blockquote>`
- `- 列表` → `<ul><li>...</li></ul>`

### 3.2 导出为 PDF / DOCX（使用 Pandoc）

需要安装 [Pandoc](https://pandoc.org/installing.html)。

```bash
# Markdown → PDF（需要 LaTeX 引擎，推荐 xelatex 支持中文）
pandoc input.md -o output.pdf --pdf-engine=xelatex -V CJKmainfont="SimSun" -V geometry:margin=1in

# Markdown → DOCX
pandoc input.md -o output.docx

# Markdown → DOCX（带自定义样式模板）
pandoc input.md -o output.docx --reference-doc=template.docx

# Markdown → HTML（独立文件）
pandoc input.md -o output.html -s --metadata title="文档标题"

# 批量转换
for f in *.md; do pandoc "$f" -o "${f%.md}.pdf" --pdf-engine=xelatex; done
```

### 3.3 Mermaid 图表导出为图片

使用 [mermaid-cli](https://github.com/mermaid-js/mermaid-cli)：

```bash
# 安装（Node.js）
npm install -g @mermaid-js/mermaid-cli

# 安装（Python）
pip install mermaid-cli && playwright install chromium

# 导出 PNG
mmdc -i diagram.mmd -o output.png

# 导出 SVG
mmdc -i diagram.mmd -o output.svg

# 导出 PDF
mmdc -i diagram.mmd -o output.pdf

# 指定主题和背景色
mmdc -i diagram.mmd -o output.png -t dark -b transparent

# 处理 Markdown 中嵌入的 Mermaid（替换为图片）
mmdc -i document.md -o document-with-images.md
```

---

## 四、写作原则

1. **结构清晰**：先概述，再详述。读者应能通过目录了解全貌。
2. **言简意赅**：一句话能说清的不用两句。技术文档不是散文。
3. **图文并茂**：复杂流程用 Mermaid 图表，不要纯文字描述。
4. **示例驱动**：每个概念配一个可运行的示例。
5. **一致性**：术语、格式、命名风格全文统一。
6. **可维护**：图表用 Mermaid 代码而非截图，方便版本管理和更新。

---

## 五、文档模板

### 5.1 技术方案文档模板

```markdown
# [方案名称]

## 背景与目标

简述问题背景和本方案要达成的目标。

## 现状分析

当前系统的问题点，用数据说话。

## 方案设计

### 架构图

（Mermaid 流程图/架构图）

### 核心流程

（Mermaid 时序图）

### 数据模型

（Mermaid ER 图）

## 方案对比

| 方案 | 优点 | 缺点 | 复杂度 |
|:-----|:-----|:-----|:------:|
| 方案A | ... | ... | 低 |
| 方案B | ... | ... | 中 |

## 实施计划

（Mermaid 甘特图）

## 风险与应对

## 参考资料
```

### 5.2 故障分析报告模板

```markdown
# [故障名称] 分析报告

## 事件概述

**时间：** YYYY-MM-DD HH:mm
**影响范围：** 
**严重程度：** P0/P1/P2

## 时间线

| 时间 | 事件 | 来源 |
|:-----|:-----|:-----|
| HH:mm | ... | ... |

## 根因分析

### 调用链路

（Mermaid 时序图）

### 问题代码

（代码块 + 注释）

## 修复方案

## 后续优化

## 经验教训
```
