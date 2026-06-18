# Grafana Loki 日志查询 Skill

## 名称
grafana-loki-logs

## 描述
通过 Grafana Loki MCP Server 查询线上/测试环境日志，支持按服务名+关键词搜索、日志量统计、上下文日志获取、服务列表查询等，帮助开发者快速定位线上问题。

## 触发条件
当用户提到以下关键词时激活此 Skill：
- "查日志"、"看日志"、"日志"、"log"、"logs"
- "报错"、"异常"、"error"、"exception"
- "线上问题"、"生产问题"、"排查问题"
- "Loki"、"Grafana"
- 具体服务名如 "chief-toptrader-ae"、"chief-ipo-server" 等

## 前置条件
- 已配置 `grafana-loki` MCP Server（见下方配置说明）
- Grafana session 未过期

## 可用工具

通过 `grafana-loki` MCP Server 提供以下工具：

### 1. query_logs - 查询日志
按服务名和关键词搜索日志。

**参数：**
| 参数 | 必填 | 说明 |
|------|------|------|
| service_name | ✅ | 服务名称，如 chief-toptrader-ae |
| keyword | ❌ | 搜索关键词，多个用 `\|` 分隔 |
| time_from | ❌ | 开始时间，默认 now-15m |
| time_to | ❌ | 结束时间，默认 now |
| max_lines | ❌ | 最大行数，默认100，最大1000 |
| extra_labels | ❌ | 额外 label 过滤，如 `detected_level="error"` |

**使用示例：**
```
查询 chief-toptrader-ae 最近15分钟的 error 日志
→ query_logs(service_name="chief-toptrader-ae", keyword="error")

查询 chief-ipo-server 最近1小时的 exception 日志，只看 error 级别
→ query_logs(service_name="chief-ipo-server", keyword="exception", time_from="now-1h", extra_labels='detected_level="error"')
```

### 2. query_log_context - 获取上下文日志
获取某条日志前后的上下文，用于追踪完整调用链。

**参数：**
| 参数 | 必填 | 说明 |
|------|------|------|
| service_name | ✅ | 服务名称 |
| timestamp_ms | ✅ | 目标日志时间戳(毫秒)，从 query_logs 结果获取 |
| keyword | ❌ | 原始关键词（用于标记） |
| before_lines | ❌ | 向前行数，默认30 |
| after_lines | ❌ | 向后行数，默认30 |
| pod | ❌ | 指定 pod 名称，精确到实例 |

**使用示例：**
```
获取某条日志前后的上下文
→ query_log_context(service_name="chief-toptrader-ae", timestamp_ms="1781750435000", pod="chief-toptrader-ae-xxx")
```

### 3. query_logs_volume - 日志量统计
按 level 分组统计日志量，快速了解错误趋势。

**参数：**
| 参数 | 必填 | 说明 |
|------|------|------|
| service_name | ✅ | 服务名称 |
| keyword | ❌ | 搜索关键词 |
| time_from | ❌ | 开始时间，默认 now-1h |
| time_to | ❌ | 结束时间，默认 now |
| extra_labels | ❌ | 额外 label 过滤 |

### 4. list_services - 列出可用服务
列出 Loki 中所有可用的 service_name。

**参数：**
| 参数 | 必填 | 说明 |
|------|------|------|
| time_from | ❌ | 开始时间，默认 now-1h |
| time_to | ❌ | 结束时间，默认 now |

### 5. list_label_values - 查询 label 值
查询某个 label 的所有可用值（如 pod、namespace、detected_level）。

**参数：**
| 参数 | 必填 | 说明 |
|------|------|------|
| label_name | ✅ | label 名称 |
| time_from | ❌ | 开始时间 |
| time_to | ❌ | 结束时间 |

### 6. query_logs_by_logql - LogQL 高级查询
直接使用 LogQL 表达式查询（适合复杂场景）。

**参数：**
| 参数 | 必填 | 说明 |
|------|------|------|
| expr | ✅ | LogQL 表达式 |
| time_from | ❌ | 开始时间 |
| time_to | ❌ | 结束时间 |
| max_lines | ❌ | 最大行数 |

---

## 工作流程

### 场景 A：用户报告线上异常

1. 先用 `query_logs` 搜索相关错误日志
2. 找到关键错误后，用 `query_log_context` 获取前后上下文
3. 结合代码分析根因

### 场景 B：用户想了解某服务健康状况

1. 用 `query_logs_volume` 查看错误趋势
2. 如果错误量异常，用 `query_logs` 查看具体错误内容

### 场景 C：用户不确定服务名

1. 用 `list_services` 列出所有可用服务
2. 确认服务名后继续查询

---

## 常用服务名参考

| 服务 | service_name |
|------|-------------|
| TopTrader AE | chief-toptrader-ae |
| IPO 服务 | chief-ipo-server |
| 行情服务 | chief-quote-api-server |
| 资金账户 | chief-fundAccount-server |
| 客户信息 | customer-info-server |

---

## 时间格式说明

| 格式 | 示例 | 说明 |
|------|------|------|
| 相对时间 | now-15m, now-1h, now-24h | 最近N分钟/小时/天 |
| 绝对时间 | 2026-06-18 10:30:00 | 精确时间点 |
| 毫秒时间戳 | 1781750435000 | Unix 毫秒时间戳 |

---

## MCP 配置

在 `.kiro/settings/mcp.json` 中添加：

```json
"grafana-loki": {
  "command": "python",
  "args": ["<path-to>/grafana-loki-mcp-server/server.py"],
  "env": {
    "GRAFANA_URL": "https://grafana.stx365.com",
    "GRAFANA_SESSION": "<your-grafana-session-cookie>",
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
```

### Session 过期处理
Grafana session cookie 有有效期，过期后需要：
1. 在浏览器登录 Grafana
2. 从浏览器 DevTools → Application → Cookies 中获取 `grafana_session` 值
3. 更新 mcp.json 中的 `GRAFANA_SESSION` 环境变量

---

## 注意事项

1. **查询范围**：默认只查最近15分钟，排查历史问题时需指定 time_from
2. **行数限制**：单次最多返回1000条，日志量大时建议缩小时间范围或加关键词过滤
3. **Pod 定位**：多副本服务建议指定 pod 参数，避免日志混杂
4. **LogQL 语法**：高级查询支持 `|=`(包含)、`!=`(不包含)、`|~`(正则匹配)、`!~`(正则排除)
