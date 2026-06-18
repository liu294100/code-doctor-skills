# Grafana Loki MCP Server v2

通过 Grafana API 查询 Loki 日志的 MCP Server，专为 Kiro AI 设计。

## 特性

* **自动登录**：配置账号密码后自动获取 Session，无需手动粘贴 Cookie
* **自动刷新**：Session 过期时自动重新登录，无需人工干预
* **高效查询**：支持关键词搜索、时间范围、Pod/Level 过滤
* **6 个工具**：日志查询、上下文查询、日志量统计、服务列表、Label 查询、LogQL 高级查询

---

## 快速安装（30 秒）

### 方法一：直接下载（推荐）

### 1. 下载 `server.py`

#### Windows PowerShell

```powershell
mkdir D:\dev\AI\grafana-loki-mcp-server

curl -o D:\dev\AI\grafana-loki-mcp-server\server.py `
  https://raw.githubusercontent.com/liu294100/code-doctor-skills/refs/heads/main/AI/grafana-loki-mcp-server/server.py
```

#### macOS / Linux

```bash
mkdir -p ~/dev/AI/grafana-loki-mcp-server

curl -o ~/dev/AI/grafana-loki-mcp-server/server.py \
  https://raw.githubusercontent.com/liu294100/code-doctor-skills/refs/heads/main/AI/grafana-loki-mcp-server/server.py
```

下载地址：

```text
https://raw.githubusercontent.com/liu294100/code-doctor-skills/refs/heads/main/AI/grafana-loki-mcp-server/server.py
```

### 2. 安装依赖

```bash
pip install mcp httpx
```

### 3. 安装 Skill 文件（可选）

让 Kiro 更智能地使用日志工具。

#### Windows

```powershell
mkdir %USERPROFILE%\.kiro\skills\grafana-loki-logs
```

将 `SKILL.md` 复制到上述目录。

### 4. 配置全局 MCP

编辑：

```text
~/.kiro/settings/mcp.json
```

在 `mcpServers` 中添加：

```json
{
  "grafana-loki": {
    "command": "python",
    "args": [
      "D:/dev/AI/grafana-loki-mcp-server/server.py"
    ],
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
      "query_logs",
      "query_logs_volume",
      "query_log_context",
      "list_services",
      "list_label_values",
      "query_logs_by_logql"
    ]
  }
}
```

> **注意：** `args` 中的路径请修改为你实际保存 `server.py` 的位置。

### 5. 重启 MCP

打开 Kiro 命令面板：

```text
MCP → Reconnect
```

---

### 方法二：运行安装脚本

#### Windows

直接双击运行：

```bash
install.bat
```

---

## 环境变量说明

| 变量名                   | 必填 | 说明                                  |
| --------------------- | -- | ----------------------------------- |
| `GRAFANA_URL`         | ✅  | Grafana 地址                          |
| `GRAFANA_USERNAME`    | ✅* | 登录账号（需与 `PASSWORD` 配对使用）            |
| `GRAFANA_PASSWORD`    | ✅* | 登录密码                                |
| `GRAFANA_ORG_ID`      | ✅  | 组织 ID                               |
| `LOKI_DATASOURCE_UID` | ✅  | Loki 数据源 UID                        |
| `LOKI_DATASOURCE_ID`  | ✅  | Loki 数据源 ID                         |
| `GRAFANA_SESSION`     | ❌  | 手动指定 Session（配置账号密码后通常不需要）          |
| `GRAFANA_TOKEN`       | ❌  | API Token（优先级最高，配置后不走 Session 登录流程） |

> * 配置 `GRAFANA_USERNAME` 和 `GRAFANA_PASSWORD` 后，系统会自动登录并自动刷新 Session。

---

## 获取配置参数

### GRAFANA_URL

你的 Grafana 访问地址。

### GRAFANA_ORG_ID

登录 Grafana：

```text
左下角齿轮 → Organization → 查看 URL 中的 orgId
```

### LOKI_DATASOURCE_UID / LOKI_DATASOURCE_ID

1. 登录 Grafana
2. 进入 Explore 页面
3. 按 `F12` 打开开发者工具
4. 随意执行一次日志查询
5. 在 Network 面板找到 `ds/query` 请求
6. 查看请求体中的：

```json
{
  "datasource": {
    "uid": "xxx"
  },
  "datasourceId": 6
}
```

---

## 使用示例

在 Kiro Chat 中直接输入：

* 查一下 `xxx` 最近的 error 日志
* 看看 `xxx2` 最近 1 小时有没有 exception
* 这个服务最近什么时候重启的
* 查一下 `xxx` 最近 24 小时的日志量

---

## 团队默认值（已预置）

| 配置项                   | 默认值                          |
| --------------------- | ---------------------------- |
| `GRAFANA_URL`         | `https://grafana.xxx.com` |
| `GRAFANA_ORG_ID`      | `5`                          |
| `LOKI_DATASOURCE_UID` | `ffkfi6twwk6wwf`             |
| `LOKI_DATASOURCE_ID`  | `6`                          |

团队成员只需要提供自己的 **Grafana 账号和密码** 即可完成配置。
