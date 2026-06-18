---
name: skywalking-apm-mcp-go
description: "通过 Apache SkyWalking MCP Server 查询和分析应用性能指标，支持服务拓扑、链路追踪（Trace）、日志查询、MQE 指标表达式、告警查询、实例/端点分析等，帮助开发者快速定位性能瓶颈、异常链路和线上问题。当用户提到 skywalking、APM、链路追踪、trace、性能分析、慢接口、拓扑图、服务指标、P99、响应时间、吞吐量、错误率、告警 时激活。"
inclusion: manual
---

# Apache SkyWalking APM 分析 Skill

> 基于 [apache/skywalking-mcp](https://github.com/apache/skywalking-mcp) 开源项目，通过 MCP 协议对接 SkyWalking OAP，AI 可直接查询各类 APM 指标、链路追踪、日志、告警等数据，辅助性能分析和问题排查。

---

## 快速安装

### 方式 A：Docker 运行（推荐）

无需编译，直接拉取官方镜像：

```bash
docker pull ghcr.io/apache/skywalking-mcp/skywalking-mcp:latest
```

### 方式 B：从源码编译

```bash
git clone https://github.com/apache/skywalking-mcp.git
cd skywalking-mcp && go mod tidy
make
# 产物在 bin/swmcp
```

### 方式 C：下载 Release 二进制

前往 https://github.com/apache/skywalking-mcp/releases 下载对应平台的二进制文件。

---

## 配置 MCP

编辑 `~/.kiro/settings/mcp.json`（全局），在 `mcpServers` 中添加：

### 使用本地编译的二进制

```json
"skywalking": {
  "command": "D:/dev/AI/skywalking-mcp/bin/swmcp",
  "args": ["stdio", "--sw-url", "https://skywalking.stx365.com"],
  "disabled": false,
  "autoApprove": [
    "list_layers", "list_services", "list_instances", "list_endpoints",
    "list_processes", "query_traces", "query_logs", "execute_mqe_expression",
    "list_mqe_metrics", "get_mqe_metric_type", "query_events",
    "query_alarms", "query_services_topology", "query_instances_topology",
    "query_endpoints_topology", "query_processes_topology"
  ]
}
```

### 使用 Docker

```json
"skywalking": {
  "command": "docker",
  "args": [
    "run", "--rm", "-i",
    "ghcr.io/apache/skywalking-mcp/skywalking-mcp:latest",
    "--sw-url", "https://skywalking.stx365.com"
  ],
  "disabled": false,
  "autoApprove": [
    "list_layers", "list_services", "list_instances", "list_endpoints",
    "list_processes", "query_traces", "query_logs", "execute_mqe_expression",
    "list_mqe_metrics", "get_mqe_metric_type", "query_events",
    "query_alarms", "query_services_topology", "query_instances_topology",
    "query_endpoints_topology", "query_processes_topology"
  ]
}
```

> 如果 SkyWalking OAP 启用了 Basic Auth，添加参数：`"--sw-username", "admin", "--sw-password", "${SW_PASSWORD}"`
> 如果使用自签名证书，添加：`"--sw-insecure"`

### 配置完成后

Kiro 命令面板 → 搜索 "MCP" → 重连 MCP Server

---

## 可用工具一览

### 链路追踪（Trace）

| 工具 | 说明 |
|------|------|
| `query_traces` | 多条件查询 Trace（按服务、端点、状态、标签、时间范围过滤），支持 full/summary/errors_only 视图 |

### 日志（Log）

| 工具 | 说明 |
|------|------|
| `query_logs` | 按服务、实例、端点、traceId、标签等条件查询日志，支持分页 |

### MQE 指标查询

| 工具 | 说明 |
|------|------|
| `execute_mqe_expression` | 执行 MQE 表达式查询/计算指标数据，支持聚合、TopN、趋势分析 |
| `list_mqe_metrics` | 列出可用的指标名称，按正则过滤 |
| `get_mqe_metric_type` | 获取指标类型信息（REGULAR_VALUE/LABELED_VALUE/SAMPLED_RECORD） |

### 元数据（Metadata）

| 工具 | 说明 |
|------|------|
| `list_layers` | 列出 SkyWalking 所有注册的 Layer（如 GENERAL、MESH、K8S） |
| `list_services` | 列出指定 Layer 下所有注册的服务 |
| `list_instances` | 列出某服务的所有实例（Pod/JVM 进程） |
| `list_endpoints` | 列出某服务的端点，支持关键字过滤 |
| `list_processes` | 列出某服务实例下的进程 |

### 事件（Event）

| 工具 | 说明 |
|------|------|
| `query_events` | 查询事件（部署、重启、扩缩容），按服务/实例/端点/类型过滤 |

### 告警（Alarm）

| 工具 | 说明 |
|------|------|
| `query_alarms` | 查询告警（指标阈值触发），按范围、关键字、标签过滤 |

### 拓扑（Topology）

| 工具 | 说明 |
|------|------|
| `query_services_topology` | 查询全局或范围内的服务拓扑 |
| `query_instances_topology` | 查询客户端和服务端之间的实例拓扑 |
| `query_endpoints_topology` | 查询端点依赖拓扑 |
| `query_processes_topology` | 查询服务实例的进程拓扑 |

---

## 可用 Prompts（引导式分析）

| Prompt | 说明 | 参数 |
|--------|------|------|
| `analyze-performance` | 分析服务性能指标 | service_name(必填), start, end |
| `compare-services` | 对比多个服务的性能指标 | services(必填), metrics, start, end |
| `top-services` | 按指标排名 TopN 服务 | metric_name(必填), top_n, order |
| `investigate-traces` | 调查异常和性能问题的链路 | service_id, trace_state, start, end |
| `trace-deep-dive` | 深入分析某条 Trace | trace_id(必填), view |
| `analyze-logs` | 分析服务日志的错误和模式 | service_id, log_level, start, end |
| `explore-service-topology` | 探索服务/实例/端点/进程拓扑 | layer(必填), start(必填), end |
| `build-mqe-query` | 辅助构建 MQE 表达式 | query_type(必填), metrics(必填), conditions |
| `explore-metrics` | 探索可用指标及其类型 | pattern, show_examples |
| `generate_duration` | 自然语言时间范围转换为 duration 对象 | time_range(必填) |

---

## 常用场景工作流

### 场景 1：查看服务整体健康状况

```
1. list_services → 找到目标服务
2. execute_mqe_expression → 查询 service_resp_time / service_cpm / service_sla
3. 分析 P50/P75/P99 响应时间趋势
```

### 场景 2：排查慢接口

```
1. list_endpoints(serviceName) → 列出端点
2. execute_mqe_expression → 查询 endpoint_resp_time / endpoint_percentile
3. query_traces(minDuration) → 查找慢 Trace
4. 深入分析 Trace 的每个 Span 耗时
```

### 场景 3：线上异常定位

```
1. query_alarms → 查看最近告警
2. query_traces(state=ERROR) → 查找错误链路
3. query_logs(traceId) → 关联日志
4. query_services_topology → 查看依赖拓扑，定位问题节点
```

### 场景 4：服务对比分析

```
1. list_services → 列出所有服务
2. compare-services prompt → 对比多个服务的 CPM、响应时间、错误率
3. execute_mqe_expression → 自定义指标对比
```

### 场景 5：部署后验证

```
1. query_events → 查看部署事件
2. execute_mqe_expression → 对比部署前后的响应时间和错误率
3. query_alarms → 检查是否触发新告警
```

---

## 常用 MQE 表达式参考

| 指标 | 表达式 | 说明 |
|------|--------|------|
| 服务平均响应时间 | `service_resp_time` | 毫秒 |
| 服务 CPM（每分钟调用量） | `service_cpm` | 吞吐量 |
| 服务成功率 | `service_sla` | 万分比（10000=100%） |
| 服务 P50/P75/P90/P95/P99 | `service_percentile` | labels: 0=P50,1=P75,2=P90,3=P95,4=P99 |
| 端点响应时间 | `endpoint_resp_time` | 按端点维度 |
| 端点 CPM | `endpoint_cpm` | 端点吞吐量 |
| 实例 JVM 内存 | `instance_jvm_memory_heap` | 堆内存使用（字节） |
| 实例 JVM GC 次数 | `instance_jvm_young_gc_count` | Young GC 次数 |
| 实例 CPU 使用率 | `instance_jvm_cpu` | CPU 百分比 |
| 数据库响应时间 | `database_access_resp_time` | 数据库层响应时间 |

---

## 时间参数格式

SkyWalking MCP 使用 duration 对象：

```json
{
  "start": "2026-06-18 0800",
  "end": "2026-06-18 0900",
  "step": "MINUTE"
}
```

| step 可选值 | 说明 |
|------------|------|
| `MINUTE` | 分钟粒度 |
| `HOUR` | 小时粒度 |
| `DAY` | 天粒度 |

> 使用 `generate_duration` prompt 可以从自然语言（如"最近1小时"）自动生成 duration 对象。

---

## 我们的 SkyWalking 环境

| 环境 | URL | 说明 |
|------|-----|------|
| 生产 | https://skywalking.xxx.com | 生产环境 APM |

### 常用服务名称

| 服务 | SkyWalking 中的名称 |
|------|---------------------|


> 实际服务名称可通过 `list_services` 工具动态获取。

---

## 注意事项

1. **时间范围**：查询默认返回最近 15 分钟数据，历史分析需明确指定 start/end
2. **数据量控制**：Trace 查询建议加时间范围和条件过滤，避免返回过多数据
3. **指标理解**：service_sla 是万分比（9900 = 99%），service_percentile labels 0-4 分别对应 P50/P75/P90/P95/P99
4. **拓扑查询**：需要指定 Layer（通常为 GENERAL），可先用 list_layers 确认
5. **生产环境**：只做读取操作，MCP Server 建议加 `--read-only` 参数
