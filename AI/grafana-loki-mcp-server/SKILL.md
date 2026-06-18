---
name: grafana-loki-logs
description: "通过 Grafana Loki MCP Server 查询线上/测试环境日志，支持按服务名+关键词搜索、日志量统计、上下文日志获取、服务列表查询等，帮助开发者快速定位线上问题。当用户提到查日志、看日志、log、error、exception、线上报错、排查问题、Loki、Grafana 或具体服务名时激活。"
inclusion: manual
---

# Grafana Loki 日志查询 Skill

> 通过 Grafana Loki MCP Server 查询线上/测试环境日志，结合 AI 代码分析能力快速定位线上问题。

---

## 快速安装（30秒）

### 步骤 1：下载 server.py

`bash
# 下载地址（直接保存到本地任意目录）
https://raw.githubusercontent.com/liu294100/code-doctor-skills/refs/heads/main/AI/grafana-loki-mcp-server/server.py
`

Windows 快速下载：
`powershell
mkdir D:\dev\AI\grafana-loki-mcp-server
curl -o D:\dev\AI\grafana-loki-mcp-server\server.py https://raw.githubusercontent.com/liu294100/code-doctor-skills/refs/heads/main/AI/grafana-loki-mcp-server/server.py
`

### 步骤 2：安装依赖

`bash
pip install mcp httpx
`

### 步骤 3：安装 Skill

将本文件（SKILL.md）复制到：
- Windows: %USERPROFILE%\.kiro\skills\grafana-loki-logs\SKILL.md
- Mac/Linux: ~/.kiro/skills/grafana-loki-logs/SKILL.md

### 步骤 4：配置 MCP

编辑 ~/.kiro/settings/mcp.json（全局）或 <项目>/.kiro/settings/mcp.json（项目级），在 mcpServers 中添加：

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

> **注意**：rgs 中的路径改为你实际保存 server.py 的位置。配置了账号密码后 session 过期会自动刷新，无需人工干预。

### 步骤 5：重启 MCP

Kiro 命令面板 → 搜索 "MCP" → 重连 MCP Server

---

## 前置条件
- Python 3.10+
- 已配置 grafana-loki MCP Server
- 配置了 GRAFANA_USERNAME + GRAFANA_PASSWORD（自动登录，无需手动维护 session）

## 可用工具

通过 grafana-loki MCP Server 提供以下工具：

### 1. query_logs - 查询日志
按服务名和关键词搜索日志。

**参数：**
| 参数 | 必填 | 说明 |
|------|------|------|
| service_name | ✅ | 服务名称，如 chief-toptrader-ae |
| keyword | ❌ | 搜索关键词，多个用 \| 分隔 |
| time_from | ❌ | 开始时间，默认 now-15m |
| time_to | ❌ | 结束时间，默认 now |
| max_lines | ❌ | 最大行数，默认100，最大1000 |
| extra_labels | ❌ | 额外 label 过滤，如 detected_level="error" |

**使用示例：**
`
查询 chief-toptrader-ae 最近15分钟的 error 日志
→ query_logs(service_name="chief-toptrader-ae", keyword="error")

查询最近1小时 exception 日志，只看 error 级别
→ query_logs(service_name="chief-ipo-server", keyword="exception", time_from="now-1h", extra_labels='detected_level="error"')

查最近一次重启时间
→ query_logs(service_name="chief-toptrader-ae", keyword="Started", time_from="now-24h", max_lines=20)
`

### 2. query_log_context - 获取上下文日志
获取某条日志前后的上下文，用于追踪完整调用链。

**参数：**
| 参数 | 必填 | 说明 |
|------|------|------|
| service_name | ✅ | 服务名称 |
| timestamp_ms | ✅ | 目标日志时间戳(毫秒)，从 query_logs 结果获取 |
| keyword | ❌ | 原始关键词 |
| before_lines | ❌ | 向前行数，默认30 |
| after_lines | ❌ | 向后行数，默认30 |
| pod | ❌ | 指定 pod 名称 |

### 3. query_logs_volume - 日志量统计
按 level 分组统计日志量，快速了解错误趋势。

### 4. list_services - 列出可用服务
列出 Loki 中所有可用的 service_name。

### 5. list_label_values - 查询 label 值
查询某个 label 的所有可用值（如 pod、namespace、detected_level）。

### 6. query_logs_by_logql - LogQL 高级查询
直接使用 LogQL 表达式查询（适合复杂场景）。

---

## 工作流程

### 场景 A：用户报告线上异常
1. 先用 query_logs 搜索相关错误日志
2. 找到关键错误后，用 query_log_context 获取前后上下文
3. 结合代码分析根因

### 场景 B：用户想了解某服务健康状况
1. 用 query_logs_volume 查看错误趋势
2. 如果错误量异常，用 query_logs 查看具体错误内容

### 场景 C：用户不确定服务名
1. 用 list_services 列出所有可用服务
2. 确认服务名后继续查询

### 场景 D：查看服务最近重启时间
1. 用 query_logs(service_name="xxx", keyword="Started", time_from="now-24h") 查找 Spring Boot 启动日志

---

## 时间格式说明

| 格式 | 示例 | 说明 |
|------|------|------|
| 相对时间 | now-15m, now-1h, now-24h | 最近N分钟/小时/天 |
| 绝对时间 | 2026-06-18 10:30:00 | 精确时间点 |
| 毫秒时间戳 | 1781750435000 | Unix 毫秒时间戳 |

---

## 注意事项

1. **查询范围**：默认只查最近15分钟，排查历史问题时需指定 time_from
2. **行数限制**：单次最多返回1000条，日志量大时建议缩小时间范围或加关键词过滤
3. **Pod 定位**：多副本服务建议指定 pod 参数，避免日志混杂
4. **LogQL 语法**：支持 |=(包含)、!=(不包含)、|~(正则匹配)、!~(正则排除)
5. **自动登录**：配置账号密码后 session 过期会自动刷新，无需人工干预
