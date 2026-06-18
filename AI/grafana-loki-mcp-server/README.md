# Grafana Loki MCP Server

通过 Grafana API 代理查询 Loki 日志的 MCP Server，配合 Kiro / Claude 等 AI 工具实现自然语言查日志。

## 功能

| 工具 | 功能 | 示例 |
|------|------|------|
| `query_logs` | 按服务名+关键词搜索日志 | "查 chief-toptrader-ae 最近的 error" |
| `query_log_context` | 获取某条日志的前后上下文 | "看一下这条报错前后的日志" |
| `query_logs_volume` | 日志量统计（按 level 分组） | "最近1小时 error 趋势" |
| `list_services` | 列出所有可用服务名 | "有哪些服务可以查" |
| `list_label_values` | 查询 label 的所有值 | "这个服务有哪些 pod" |
| `query_logs_by_logql` | 直接用 LogQL 查询 | 高级用法 |

## 快速开始

### 1. 安装依赖

```bash
pip install mcp httpx
```

或者：

```bash
pip install -r requirements.txt
```

### 2. 获取 Grafana Session

1. 在浏览器登录你的 Grafana
2. 打开 DevTools → Application → Cookies
3. 复制 `grafana_session` 的值

> 💡 如果你的 Grafana 支持 API Key / Service Account Token，
> 建议改用 Token 方式（更稳定，不会过期），参见下方"高级配置"。

### 3. 配置 MCP

在 Kiro 的 `.kiro/settings/mcp.json` 中添加：

```json
{
  "mcpServers": {
    "grafana-loki": {
      "command": "python",
      "args": ["<下载路径>/grafana-loki-mcp-server/server.py"],
      "env": {
        "GRAFANA_URL": "https://your-grafana.com",
        "GRAFANA_SESSION": "<your-grafana-session>",
        "GRAFANA_ORG_ID": "1",
        "LOKI_DATASOURCE_UID": "<your-loki-datasource-uid>",
        "LOKI_DATASOURCE_ID": "1"
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
}
```

### 4. 获取 Loki Datasource 信息

在 Grafana 中：
- 进入 Connections → Data Sources → 找到你的 Loki 数据源
- URL 中的 uid 就是 `LOKI_DATASOURCE_UID`
- 或者在 Explore 页面的网络请求中查看 `x-datasource-uid` 头

### 5. 安装 Skill（可选）

将 `SKILL.md` 复制到 Kiro skills 目录：

```bash
# Windows
mkdir %USERPROFILE%\.kiro\skills\grafana-loki-logs
copy SKILL.md %USERPROFILE%\.kiro\skills\grafana-loki-logs\SKILL.md

# macOS / Linux
mkdir -p ~/.kiro/skills/grafana-loki-logs
cp SKILL.md ~/.kiro/skills/grafana-loki-logs/SKILL.md
```

安装后，Kiro 会在你提到"查日志"、"看 error"等关键词时自动激活该 Skill。

---

## 高级配置

### 使用 API Token 替代 Session Cookie

如果你的 Grafana 支持 Service Account：

1. Grafana → Administration → Service Accounts → Create
2. 创建 Token，赋予 Viewer 权限
3. 修改环境变量：

```json
"env": {
  "GRAFANA_URL": "https://your-grafana.com",
  "GRAFANA_TOKEN": "glsa_xxxxxxxxxxxx",
  "GRAFANA_ORG_ID": "1",
  "LOKI_DATASOURCE_UID": "xxxxx",
  "LOKI_DATASOURCE_ID": "1"
}
```

然后修改 `server.py` 中的 `_get_headers()` 函数，将 Cookie 改为：
```python
"Authorization": f"Bearer {os.environ.get('GRAFANA_TOKEN', '')}",
```

### 环境变量说明

| 变量 | 必填 | 说明 |
|------|------|------|
| GRAFANA_URL | ✅ | Grafana 地址，如 `https://grafana.example.com` |
| GRAFANA_SESSION | ✅* | Grafana session cookie（与 TOKEN 二选一） |
| GRAFANA_TOKEN | ✅* | Grafana API Token（与 SESSION 二选一） |
| GRAFANA_ORG_ID | ❌ | 组织 ID，默认 "1" |
| LOKI_DATASOURCE_UID | ✅ | Loki 数据源 UID |
| LOKI_DATASOURCE_ID | ✅ | Loki 数据源数字 ID |

---

## 使用示例

配置完成后，直接在 Kiro 中用自然语言：

```
帮我查一下 chief-toptrader-ae 最近15分钟的 error 日志

看一下 chief-ipo-server 今天10点到11点的 timeout 相关日志

这条报错前后的日志帮我看看（自动调用 context）

最近1小时 chief-toptrader-ae 的错误趋势怎么样
```

---

## 文件结构

```
grafana-loki-mcp-server/
├── server.py           # MCP Server 主文件
├── requirements.txt    # Python 依赖
├── SKILL.md           # Kiro Skill 定义文件
└── README.md          # 本文件
```

---

## 常见问题

**Q: 提示 HTTP 401 Unauthorized？**
A: Session 过期了，重新从浏览器获取 `grafana_session` cookie。

**Q: 提示 HTTP 403 Forbidden？**
A: 检查 `GRAFANA_ORG_ID` 是否正确，你的账号是否有该 Org 的访问权限。

**Q: 查不到日志但 Grafana 页面能查到？**
A: 确认 `LOKI_DATASOURCE_UID` 和 `LOKI_DATASOURCE_ID` 是否匹配。
在 Grafana Explore 页面 F12 查看网络请求中的 `x-datasource-uid`。

**Q: 如何找到 LOKI_DATASOURCE_ID？**
A: 在 Grafana 中打开 Explore，F12 查看 `/api/ds/query` 请求的 payload，
里面 `datasourceId` 字段就是数字 ID。
