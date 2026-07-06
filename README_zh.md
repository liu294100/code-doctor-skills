# Code Doctor Check — Kiro Skills 套件集合

[🇬🇧 English](./README.md)

面向开发的 Kiro AI Skills 集合，覆盖 Java、Python、文档处理、视频生成、APM 可观测性等多个领域，提供代码审查、开发指导、架构设计、性能分析、打包部署等全方位 AI 辅助能力。

## 项目结构

```
code-doctor-check/
├── java-doctor-check/          # Java 技术栈 Skills
│   ├── .kiro/skills/
│   │   ├── 01-code-quality/    # 代码质量审查（Java/SQL/Spring Boot/MR）
│   │   ├── 02-architecture/    # 架构设计审查（金融/券商）
│   │   ├── 03-brokerage-business/  # 券商业务系统专项（交易/资金）
│   │   └── 04-techspec-templates/  # 技术方案文档生成模板
│   ├── java-jprofiler-analyzer/    # JProfiler 性能深度分析
│   ├── java-memory-analyzer/       # Java 内存分析（MAT/jmap/jcmd）
│   ├── javadecompiler/             # JAR 反编译（CFR）
│   ├── jadx-decompile/             # JADX 反编译（APK/DEX/JAR）
│   └── gitlab-ci/                  # GitLab CI/CD 配置模板
│
├── python-doctor-check/        # Python 技术栈 Skills
│   └── .kiro/skills/
│       ├── 01-python-sdk/      # Python SDK（开发/审查/打包）
│       ├── 02-flask/           # Flask Web 应用（开发/审查/部署）
│       └── 03-gui-toolkit/     # GUI 桌面小工具（开发/审查/打包）
│
├── docs/                       # 文档处理 Skills
│   ├── docs-readers/           # 文档阅读器（PDF/PPT/Excel/Word/图片/JAR/APK）
│   ├── ui-diagram-designer/    # UI 图表设计
│   ├── drawio-designer/        # DrawIO 图表设计
│   ├── drawio-xml-guide/       # DrawIO XML 编写指南
│   ├── read-drawio/            # DrawIO 文件读取
│   ├── doc-writer/             # 技术文档写作
│   ├── doc-writing-workflow/   # 高效文档写作工作流
│   └── Java_Version_Features_JDK1_to_JDK25.md  # Java 版本特性全景总览
│
├── video/                      # 视频生成 Skills
│   ├── html2video/             # HTML 模板驱动视频生成
│   └── browser-use-video/      # 浏览器自动化视频生成
│
└── AI/                         # AI 工具配置
    ├── mcp/                    # MCP 服务器配置
    │   ├── setup-mcp/          # MCP 通用安装指南
    │   ├── setup-nacos2-mcp/   # Nacos 2.x MCP 安装配置
    │   └── nacos2-mcp-server/  # Nacos 2.x MCP Server 实现
    ├── skywalking/             # SkyWalking APM 集成
    │   ├── skywalking-mcp-server/    # SkyWalking MCP Server（Python）
    │   └── skywalking-apm-mcp-go/    # SkyWalking MCP（Go，基于官方开源）
    └── grafana-loki-mcp-server/      # Grafana Loki 日志查询 MCP Server
```

## 技术栈覆盖

### Java（java-doctor-check）

面向 Java 开发全链路 Skills，覆盖代码审查、架构设计、业务系统、性能分析和技术方案文档生成。

| 分类 | Skills 数量 | 覆盖范围 |
|------|-----------|---------|
| 代码质量审查 | 5 | Java 代码规范、SQL 审查、Spring Boot SQL、MR 审查、GitLab 报告 |
| 架构设计 | 2 | 互联网金融通用架构、券商整体架构 |
| 业务系统 | 2 | 交易系统（港/美/A 股）、资金系统（保证金/融资/清算） |
| 技术方案模板 | 3 | 港美股交易、期货期权衍生品、基金 IPO 债券 |
| 性能分析 | 2 | JProfiler 全栈性能分析、Eclipse MAT 内存分析 |
| 反编译工具 | 2 | CFR 反编译 JAR、JADX 反编译 APK/DEX/JAR |
| CI/CD | 1 | GitLab CI/CD 配置模板 |

### Python（python-doctor-check）

面向 Python 开发者的三大场景 Skills，每个场景均包含开发、审查、打包三个维度。

| 分类 | Skills 数量 | 覆盖范围 |
|------|-----------|---------|
| Python SDK | 3 | 开发规范、代码审查、PyPI 打包发布 |
| Flask Web | 3 | 开发指导、安全审查、Docker 部署 |
| GUI 小工具 | 3 | 框架选型与开发、跨平台审查、PyInstaller 打包 |

### 文档处理（docs）

面向文档阅读、设计、写作的多功能 Skills 集合。

| 分类 | Skills 数量 | 覆盖范围 |
|------|-----------|---------|
| 文档阅读器 | 7 | PDF、PPT、Excel、Word、图片、JAR 反编译、APK 反编译 |
| 设计工具 | 4 | UI 图表设计、DrawIO 设计与读取、DrawIO XML 编写指南 |
| 文档写作 | 2 | 技术文档写作、高效文档写作工作流 |
| 参考资料 | 1 | Java 版本特性全景总览（JDK 1.0 ~ JDK 25） |

### 视频生成（video）

基于浏览器自动化和 HTML 渲染的视频生成 Skills。

| 分类 | Skills 数量 | 覆盖范围 |
|------|-----------|---------|
| 视频生成 | 2 | HTML 模板视频、浏览器自动化视频 |

### AI 工具与可观测性（AI）

AI 开发工具配置及 APM/日志 MCP Server 集成。

| 分类 | Skills 数量 | 覆盖范围 |
|------|-----------|---------|
| MCP 配置 | 3 | MCP 通用安装、Nacos 2.x MCP 安装配置、Nacos MCP Server |
| SkyWalking APM | 2 | Python MCP Server（自研）、Go MCP（基于 Apache 官方开源） |
| Grafana Loki | 1 | 日志查询 MCP Server（按服务名/关键词搜索、上下文日志） |

## 快速开始

1. 将对应技术栈的文件夹复制到你的项目根目录
2. 确保 `.kiro/skills/` 目录结构完整
3. 在 Kiro 中打开项目，自动触发的 Skills 会在打开对应文件时生效
4. 手动触发的 Skills 在聊天中使用 `#skill-name` 引用即可

### MCP Server 配置

对于 AI 目录下的 MCP Server（SkyWalking、Loki、Nacos），参考各自目录下的 SKILL.md 或 README.md 完成安装配置后，在 Kiro 的 MCP 设置中添加对应 Server 即可使用。

## 许可证

MIT License

🛑 **Additional Restriction:**

The Software may **NOT** be used, either directly or indirectly, by the following entities or individuals:

1. Any official, employee, or representative of the **Islamic Republic of Iran's government**
2. Any individual, entity, or affiliated institution **controlled or directly influenced by the Iranian Islamic religious authorities**, including but not limited to Shiite clerics, religious foundations, religious councils, and their affiliated organizations in the Islamic Republic of Iran
3. Any organization or person acting on behalf of the **North Korean government**
4. Members of or individuals affiliated with the following listed organizations, including but not limited to:
   - **Hamas**
   - **Houthi Movement (Ansar Allah)**
   - **Fraud syndicates and criminal organizations** operating in **Myanmar, Cambodia**, and other regions, including but not limited to telecom fraud groups, online gambling operations, human trafficking organizations, and their affiliated companies or entities
   - Any entity designated as a **terrorist organization** by the **United Nations**, **European Union**, **United States**, **People's Republic of China**, **Republic of Korea**, **Singapore**
   - Any organization, individual, or affiliated institution **controlled by the former Maduro and Chávez Venezuelan government** (due to rampant drug trafficking)
   - Any **Afghan Islamic cult personnel**, and any **Afghan government** or its **affiliated entities**

Any use by the aforementioned individuals or entities shall be deemed **unauthorized and in violation** of this license. We reserve the right to take legal action to the fullest extent permitted by applicable law.
