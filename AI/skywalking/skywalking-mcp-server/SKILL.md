---
name: skywalking-apm
description: "通过 Apache SkyWalking MCP Server 查询和分析应用性能指标，支持服务拓扑、链路追踪（Trace）、日志查询、MQE 指标表达式、告警查询、实例/端点分析等，帮助开发者快速定位性能瓶颈、异常链路和线上问题。当用户提到 skywalking、APM、链路追踪、trace、性能分析、慢接口、拓扑图、服务指标、P99、响应时间、吞吐量、错误率、告警 时激活。"
inclusion: manual
---

# Apache SkyWalking APM 分析 Skill

> Python MCP Server，对接 SkyWalking GraphQL API，AI 可直接查询 APM 各类数据。

---

## 快速安装（30秒）

### 步骤 1：获取代码

```bash
git clone https://gitlab.dev.stx365.com/chief/trade/chief-trader-z-ai-tools.git D:\dev\AI\chief-trader-z-ai-tools
```

MCP Server 位于：`D:\dev\AI\skills\skywalking-mcp-server\server.py`

后续更新：`cd D:\dev\AI\chief-trader-z-ai-tools && git pull`

### 步骤 2：安装依赖

```bash
pip install mcp httpx
```

### 步骤 3：安装 Skill

```bash
mkdir %USERPROFILE%\.kiro\skills\skywalking-apm
copy D:\dev\AI\skills\skywalking-mcp-server\SKILL.md %USERPROFILE%\.kiro\skills\skywalking-apm\SKILL.md
```

### 步骤 4：配置 MCP

编辑 `~/.kiro/settings/mcp.json`，在 `mcpServers` 中添加：

```json
"skywalking": {
  "command": "python",
  "args": ["D:/dev/AI/skills/skywalking-mcp-server/server.py"],
  "env": {
    "SW_URL": "https://skywalking.stx365.com",
    "SW_USERNAME": "",
    "SW_PASSWORD": ""
  },
  "disabled": false,
  "autoApprove": [
    "list_services", "list_instances", "list_endpoints",
    "query_traces", "query_trace_detail", "execute_mqe",
    "list_metrics", "query_logs", "query_alarms",
    "query_services_topology", "query_events", "read_metrics_values"
  ]
}
```

### 步骤 5：重启 MCP

Kiro 命令面板 → 搜索 "MCP" → 重连 MCP Server

---

## 可用工具

| 工具 | 说明 |
|------|------|
| `list_services` | 列出指定layer下的所有服务 |
| `list_instances` | 列出服务的所有实例 |
| `list_endpoints` | 列出服务的端点(接口) |
| `query_traces` | 多条件查询Trace |
| `query_trace_detail` | 根据traceId查完整链路 |
| `execute_mqe` | 执行MQE指标表达式 |
| `list_metrics` | 列出可用指标名 |
| `query_logs` | 查询日志 |
| `query_alarms` | 查询告警 |
| `query_services_topology` | 查询服务拓扑 |
| `query_events` | 查询事件 |
| `read_metrics_values` | 读取带标签指标值(P50/P75等) |

---

## 工作流

| 场景 | 步骤 |
|------|------|
| 服务健康 | list_services → execute_mqe(service_resp_time/service_cpm/service_sla) |
| 慢接口 | list_endpoints → execute_mqe(endpoint_resp_time) → query_traces(min_duration) |
| 异常定位 | query_alarms → query_traces(trace_state=ERROR) → query_trace_detail |
| P99分析 | read_metrics_values(service_percentile) |
| 拓扑分析 | query_services_topology |
| 部署验证 | query_events → execute_mqe对比前后指标 |

## 常用MQE表达式

| 表达式 | 说明 |
|--------|------|
| `service_resp_time` | 平均响应时间(ms) |
| `service_cpm` | 每分钟调用量 |
| `service_sla` | 成功率(万分比,10000=100%) |
| `service_percentile` | P50/P75/P90/P95/P99(labels:0-4) |
| `endpoint_resp_time` | 端点响应时间 |
| `endpoint_cpm` | 端点吞吐量 |
| `instance_jvm_memory_heap` | JVM堆内存 |
| `instance_jvm_cpu` | CPU使用率 |

## 时间格式

| 格式 | 示例 |
|------|------|
| 相对 | -15m, -1h, -7d |
| 绝对 | 2026-06-18 10:30:00 |
| now | 当前时间 |

## 环境

| 环境 | URL |
|------|-----|
| 生产 | https://skywalking.xxx.com |

## 注意事项

1. 默认查最近30分钟，历史需指定start/end
2. service_sla万分比(9900=99%)
3. service_percentile labels 0-4 = P50/P75/P90/P95/P99
4. Trace查询加时间范围避免数据量过大
