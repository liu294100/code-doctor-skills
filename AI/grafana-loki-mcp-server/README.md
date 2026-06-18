# Grafana Loki MCP Server v2

通过 Grafana API 查询 Loki 日志的 MCP Server，专为 Kiro AI 设计。

## 特性

- **自动登录**：配置账号密码后自动获取 session，无需手动粘贴 cookie
- **自动刷新**：session 过期时自动重新登录，无需人工干预
- **高效查询**：支持关键词搜索、时间范围、Pod/Level 过滤
- **6 个工具**：日志查询、上下文、日志量统计、服务列表、Label 查询、LogQL 高级查询

## 快速安装（30秒）

### 方法一：直接下载（推荐）

**1. 下载 server.py：**

`powershell
# Windows PowerShell
mkdir D:\dev\AI\grafana-loki-mcp-server
curl -o D:\dev\AI\grafana-loki-mcp-server\server.py https://raw.githubusercontent.com/liu294100/code-doctor-skills/refs/heads/main/AI/grafana-loki-mcp-server/server.py
`

`ash
# Mac/Linux
mkdir -p ~/dev/AI/grafana-loki-mcp-server
curl -o ~/dev/AI/grafana-loki-mcp-server/server.py https://raw.githubusercontent.com/liu294100/code-doctor-skills/refs/heads/main/AI/grafana-loki-mcp-server/server.py
`

下载地址：
> https://raw.githubusercontent.com/liu294100/code-doctor-skills/refs/heads/main/AI/grafana-loki-mcp-server/server.py

**2. 安装依赖：**

`ash
pip install mcp httpx
`

**3. 安装 Skill 文件（可选，让 AI 更聪明地使用工具）：**

`powershell
# Windows
mkdir %USERPROFILE%\.kiro\skills\grafana-loki-logs
# 将 SKILL.md 复制到上面的目录
`

**4. 配置全局 MCP：**

编辑 ~/.kiro/settings/mcp.json，在 mcpServers 中添加：

`json
"grafana-loki": {
  "command": "python",
  "args": ["D:/dev/AI/grafana-loki-mcp-server/server.py"],
  "env": {
    "GRAFANA_URL": "https://grafana.xxx.com",
    "GRAFANA_USERNAME": "你的Grafana账号",
    "GRAFANA_PASSWORD": "你的Grafana密码",
    "GRAFANA_ORG_ID": "5",
    "LOKI_DATASOURCE_UID": "ffkfi6twwk6wwf",
    "LOKI_DATASOURCE_ID": "6"
  },
  "disabled": false,
  "autoApprove": [
    "query_logs", "query_logs_volume", "query_log_context",
    "list_services", "list_label_values", "query_logs_by_logql"
  ]
}
`

> **注意**：rgs 路径改为你实际保存 server.py 的位置

**5. 重启 MCP：** Kiro 命令面板 → 搜索 "MCP" → 重连

### 方法二：运行安装脚本

`ash
# Windows - 双击运行
install.bat
`

---

## 环境变量说明

| 变量 | 必填 | 说明 |
|------|------|------|
| GRAFANA_URL | ✅ | Grafana 地址 |
| GRAFANA_USERNAME | ✅* | 登录账号（与 PASSWORD 配对使用） |
| GRAFANA_PASSWORD | ✅* | 登录密码 |
| GRAFANA_ORG_ID | ✅ | 组织 ID |
| LOKI_DATASOURCE_UID | ✅ | Loki 数据源 UID |
| LOKI_DATASOURCE_ID | ✅ | Loki 数据源 ID |
| GRAFANA_SESSION | ❌ | 手动 session（配置了账号密码后不需要） |
| GRAFANA_TOKEN | ❌ | API Token（优先级最高，配置后不走 session） |

> *配置 USERNAME/PASSWORD 后系统自动登录和刷新，无需手动维护 session

## 获取配置参数

1. **GRAFANA_URL**: 你的 Grafana 访问地址
2. **GRAFANA_ORG_ID**: 登录 Grafana → 左下角齿轮 → Organization → 看 URL 中的 orgId
3. **LOKI_DATASOURCE_UID / ID**:
   - 登录 Grafana → Explore 页面 → F12 打开 DevTools
   - 随便查一次日志，在 Network 中找 ds/query 请求
   - 看请求体中的 datasource.uid 和 datasourceId

## 使用示例

在 Kiro Chat 中直接说：

- "查一下 chief-toptrader-ae 最近的 error 日志"
- "看看 chief-ipo-server 最近1小时有没有 exception"
- "这个服务最近什么时候重启的"
- "查一下 chief-toptrader-ae 最近24小时的日志量"

## 团队默认值（已预置）

| 配置项 | 值 |
|--------|-----|
| GRAFANA_URL | https://grafana.xxx.com |
| GRAFANA_ORG_ID | 5 |
| LOKI_DATASOURCE_UID | ffkfi6twwk6wwf |
| LOKI_DATASOURCE_ID | 6 |

团队成员只需要提供自己的 **Grafana 账号和密码** 即可完成配置。
