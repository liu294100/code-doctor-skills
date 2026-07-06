# Code Doctor Check — Kiro Skills Collection

[zh 中文版](./README_zh.md)

A developer-focused collection of Kiro AI Skills covering Java, Python, document processing, video generation, APM observability, and more. Provides comprehensive AI-assisted capabilities including code review, development guidance, architecture design, performance analysis, and packaging/deployment.

## Project Structure

```
code-doctor-check/
├── java-doctor-check/          # Java Tech Stack Skills
│   ├── .kiro/skills/
│   │   ├── 01-code-quality/    # Code Quality Review (Java/SQL/Spring Boot/MR)
│   │   ├── 02-architecture/    # Architecture Design Review (FinTech/Brokerage)
│   │   ├── 03-brokerage-business/  # Brokerage Business Systems (Trading/Capital)
│   │   └── 04-techspec-templates/  # Technical Spec Document Templates
│   ├── java-jprofiler-analyzer/    # JProfiler Deep Performance Analysis
│   ├── java-memory-analyzer/       # Java Memory Analysis (MAT/jmap/jcmd)
│   ├── javadecompiler/             # JAR Decompilation (CFR)
│   ├── jadx-decompile/             # JADX Decompilation (APK/DEX/JAR)
│   └── gitlab-ci/                  # GitLab CI/CD Config Templates
│
├── python-doctor-check/        # Python Tech Stack Skills
│   └── .kiro/skills/
│       ├── 01-python-sdk/      # Python SDK (Dev/Review/Package)
│       ├── 02-flask/           # Flask Web App (Dev/Review/Deploy)
│       └── 03-gui-toolkit/     # GUI Desktop Tools (Dev/Review/Package)
│
├── docs/                       # Document Processing Skills
│   ├── docs-readers/           # Document Readers (PDF/PPT/Excel/Word/Image/JAR/APK)
│   ├── ui-diagram-designer/    # UI Diagram Design
│   ├── drawio-designer/        # DrawIO Diagram Design
│   ├── drawio-xml-guide/       # DrawIO XML Writing Guide
│   ├── read-drawio/            # DrawIO File Reader
│   ├── doc-writer/             # Technical Document Writing
│   ├── doc-writing-workflow/   # Efficient Document Writing Workflow
│   └── Java_Version_Features_JDK1_to_JDK25.md  # Java Version Features Overview
│
├── video/                      # Video Generation Skills
│   ├── html2video/             # HTML Template-Driven Video Generation
│   └── browser-use-video/      # Browser Automation Video Generation
│
└── AI/                         # AI Tools & Configuration
    ├── mcp/                    # MCP Server Configuration
    │   ├── setup-mcp/          # MCP General Setup Guide
    │   ├── setup-nacos2-mcp/   # Nacos 2.x MCP Setup
    │   └── nacos2-mcp-server/  # Nacos 2.x MCP Server Implementation
    ├── skywalking/             # SkyWalking APM Integration
    │   ├── skywalking-mcp-server/    # SkyWalking MCP Server (Python)
    │   └── skywalking-apm-mcp-go/    # SkyWalking MCP (Go, based on Apache OSS)
    └── grafana-loki-mcp-server/      # Grafana Loki Log Query MCP Server
```

## Tech Stack Coverage

### Java (java-doctor-check)

Full-chain Java development Skills covering code review, architecture design, business systems, performance analysis, and technical spec generation.

| Category | Skills Count | Coverage |
|----------|-------------|----------|
| Code Quality Review | 5 | Java coding standards, SQL review, Spring Boot SQL, MR review, GitLab report |
| Architecture Design | 2 | FinTech general architecture, Brokerage overall architecture |
| Business Systems | 2 | Trading system (HK/US/A-share), Capital system (margin/financing/clearing) |
| Tech Spec Templates | 3 | HK & US stock trading, futures & options derivatives, fund IPO bonds |
| Performance Analysis | 2 | JProfiler full-stack profiling, Eclipse MAT memory analysis |
| Decompilation Tools | 2 | CFR decompile JAR, JADX decompile APK/DEX/JAR |
| CI/CD | 1 | GitLab CI/CD config templates |

### Python (python-doctor-check)

Three scenario-based Skills for Python developers, each covering development, review, and packaging.

| Category | Skills Count | Coverage |
|----------|-------------|----------|
| Python SDK | 3 | Development standards, code review, PyPI packaging |
| Flask Web | 3 | Development guidance, security review, Docker deployment |
| GUI Tools | 3 | Framework selection & dev, cross-platform review, PyInstaller packaging |

### Document Processing (docs)

Multi-purpose Skills for document reading, design, and writing.

| Category | Skills Count | Coverage |
|----------|-------------|----------|
| Document Readers | 7 | PDF, PPT, Excel, Word, Image, JAR decompile, APK decompile |
| Design Tools | 4 | UI diagram design, DrawIO design & reading, DrawIO XML writing guide |
| Document Writing | 2 | Technical document writing, efficient writing workflow |
| Reference | 1 | Java version features overview (JDK 1.0 ~ JDK 25) |

### Video Generation (video)

Browser automation and HTML rendering-based video generation Skills.

| Category | Skills Count | Coverage |
|----------|-------------|----------|
| Video Generation | 2 | HTML template video, browser automation video |

### AI Tools & Observability (AI)

AI development tool configuration and APM/log MCP Server integration.

| Category | Skills Count | Coverage |
|----------|-------------|----------|
| MCP Configuration | 3 | MCP general setup, Nacos 2.x MCP setup, Nacos MCP Server |
| SkyWalking APM | 2 | Python MCP Server (custom), Go MCP (based on Apache OSS) |
| Grafana Loki | 1 | Log query MCP Server (search by service/keyword, context logs) |

## Quick Start

1. Copy the corresponding tech stack folder to your project root
2. Ensure the `.kiro/skills/` directory structure is intact
3. Open the project in Kiro — auto-triggered Skills activate when opening relevant files
4. Manually triggered Skills can be invoked in chat using `#skill-name`

### MCP Server Setup

For MCP Servers under the AI directory (SkyWalking, Loki, Nacos), refer to the SKILL.md or README.md in each directory for installation instructions, then add the corresponding Server in Kiro's MCP settings.

## License

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
