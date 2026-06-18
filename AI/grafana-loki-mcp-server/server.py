"""
Grafana Loki MCP Server
通过 Grafana API 查询 Loki 日志，支持：
1. 按 service_name + 关键词搜索日志
2. 日志量统计 (logs volume)
3. 获取某条日志的上下文 (context)
4. 列出可用的 service 列表
"""

import os
import json
import time
import uuid
import httpx
from datetime import datetime, timedelta
from typing import Optional
from mcp.server.fastmcp import FastMCP

# 配置
GRAFANA_URL = os.environ.get("GRAFANA_URL", "https://grafana.stx365.com")
GRAFANA_SESSION = os.environ.get("GRAFANA_SESSION", "")
GRAFANA_ORG_ID = os.environ.get("GRAFANA_ORG_ID", "5")
LOKI_DATASOURCE_UID = os.environ.get("LOKI_DATASOURCE_UID", "ffkfi6twwk6wwf")
LOKI_DATASOURCE_ID = int(os.environ.get("LOKI_DATASOURCE_ID", "6"))

mcp = FastMCP("grafana-loki")


def _get_headers():
    """构建请求头"""
    return {
        "accept": "application/json, text/plain, */*",
        "content-type": "application/json",
        "x-datasource-uid": LOKI_DATASOURCE_UID,
        "x-grafana-org-id": GRAFANA_ORG_ID,
        "x-plugin-id": "loki",
        "x-cache-skip": "true",
        "Cookie": f"grafana_session={GRAFANA_SESSION}",
    }


def _parse_time_range(time_from: str, time_to: str) -> tuple[str, str]:
    """
    解析时间范围，支持：
    - 相对时间: "now-15m", "now-1h", "now-24h", "now"
    - 绝对时间戳(毫秒): "1781749684155"
    - ISO格式: "2026-06-18 10:30:00"
    返回毫秒时间戳字符串
    """
    def parse_one(t: str) -> str:
        t = t.strip()
        if t.isdigit():
            return t
        if t == "now":
            return str(int(time.time() * 1000))
        if t.startswith("now-"):
            suffix = t[4:]
            num = int(suffix[:-1])
            unit = suffix[-1]
            multiplier = {"s": 1, "m": 60, "h": 3600, "d": 86400}
            seconds = num * multiplier.get(unit, 60)
            return str(int((time.time() - seconds) * 1000))
        # ISO format
        try:
            dt = datetime.strptime(t, "%Y-%m-%d %H:%M:%S")
            return str(int(dt.timestamp() * 1000))
        except ValueError:
            pass
        try:
            dt = datetime.strptime(t, "%Y-%m-%dT%H:%M:%S")
            return str(int(dt.timestamp() * 1000))
        except ValueError:
            pass
        return str(int(time.time() * 1000))

    return parse_one(time_from), parse_one(time_to)


def _extract_log_lines(response_data: dict) -> list[dict]:
    """从 Grafana ds/query 响应中提取日志行"""
    results = []
    for ref_id, result in response_data.get("results", {}).items():
        frames = result.get("frames", [])
        for frame in frames:
            schema = frame.get("schema", {})
            data = frame.get("data", {})
            values = data.get("values", [])
            if not values or len(values) < 3:
                continue
            # values[0] = labels array
            # values[1] = timestamps array
            # values[2] = log lines array
            labels_arr = values[0] if len(values) > 0 else []
            times_arr = values[1] if len(values) > 1 else []
            lines_arr = values[2] if len(values) > 2 else []
            for i in range(len(lines_arr)):
                entry = {
                    "timestamp": times_arr[i] if i < len(times_arr) else None,
                    "line": lines_arr[i] if i < len(lines_arr) else "",
                }
                if i < len(labels_arr) and isinstance(labels_arr[i], dict):
                    entry["pod"] = labels_arr[i].get("pod", "")
                    entry["node"] = labels_arr[i].get("node_name", "")
                results.append(entry)
    return results


@mcp.tool()
async def query_logs(
    service_name: str,
    keyword: str = "",
    time_from: str = "now-15m",
    time_to: str = "now",
    max_lines: int = 100,
    extra_labels: str = "",
) -> str:
    """
    查询 Loki 日志。

    Args:
        service_name: 服务名称，如 chief-toptrader-ae, chief-ipo-server
        keyword: 搜索关键词，支持多个用 | 分隔，如 "error|exception"
        time_from: 开始时间，支持 now-15m, now-1h, now-24h 或 2026-06-18 10:30:00
        time_to: 结束时间，支持 now 或具体时间
        max_lines: 最大返回行数，默认100，最大1000
        extra_labels: 额外的 label 过滤，如 'pod="xxx"' 或 'detected_level="error"'

    Returns:
        格式化的日志内容
    """
    from_ms, to_ms = _parse_time_range(time_from, time_to)

    # 构建 LogQL 表达式
    label_selector = f'service_name="{service_name}"'
    if extra_labels:
        label_selector += f", {extra_labels}"
    expr = "{" + label_selector + "}"
    if keyword:
        # 支持多关键词用 | 分隔
        keywords = [k.strip() for k in keyword.split("|")]
        for kw in keywords:
            expr += f" |= `{kw}`"

    max_lines = min(max_lines, 1000)
    payload = {
        "queries": [{
            "refId": "A",
            "expr": expr,
            "queryType": "range",
            "datasource": {"type": "loki", "uid": LOKI_DATASOURCE_UID},
            "editorMode": "builder",
            "maxLines": max_lines,
            "step": "",
            "legendFormat": "",
            "datasourceId": LOKI_DATASOURCE_ID,
            "intervalMs": 500,
            "maxDataPoints": 1263,
        }],
        "from": from_ms,
        "to": to_ms,
    }

    url = f"{GRAFANA_URL}/api/ds/query?ds_type=loki&requestId=mcp_{uuid.uuid4().hex[:8]}"
    async with httpx.AsyncClient(verify=False, timeout=30) as client:
        resp = await client.post(url, headers=_get_headers(), json=payload)
        if resp.status_code != 200:
            return f"请求失败: HTTP {resp.status_code}\n{resp.text}"
        data = resp.json()

    logs = _extract_log_lines(data)
    if not logs:
        return f"未查询到日志。\n查询表达式: {expr}\n时间范围: {time_from} ~ {time_to}"

    # 格式化输出
    output_lines = [
        f"查询表达式: {expr}",
        f"时间范围: {time_from} ~ {time_to}",
        f"结果数量: {len(logs)} 条",
        "=" * 80,
    ]
    for log in logs:
        ts = log.get("timestamp")
        if ts:
            try:
                dt = datetime.fromtimestamp(ts / 1000)
                ts_str = dt.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
            except (OSError, ValueError):
                ts_str = str(ts)
        else:
            ts_str = "unknown"
        pod = log.get("pod", "")
        line = log.get("line", "")
        output_lines.append(f"[{ts_str}] [{pod}] {line}")

    return "\n".join(output_lines)


@mcp.tool()
async def query_logs_volume(
    service_name: str,
    keyword: str = "",
    time_from: str = "now-1h",
    time_to: str = "now",
    extra_labels: str = "",
) -> str:
    """
    查询日志量统计（按 level 分组的 count_over_time）。

    Args:
        service_name: 服务名称
        keyword: 搜索关键词
        time_from: 开始时间
        time_to: 结束时间
        extra_labels: 额外label过滤

    Returns:
        日志量统计信息
    """
    from_ms, to_ms = _parse_time_range(time_from, time_to)

    label_selector = f'service_name="{service_name}"'
    if extra_labels:
        label_selector += f", {extra_labels}"
    inner_expr = "{" + label_selector + "}"
    if keyword:
        for kw in keyword.split("|"):
            inner_expr += f" |= `{kw.strip()}`"

    expr = (
        f"sum by (level) (count_over_time("
        f"{inner_expr} | drop __error__[$__auto]))"
    )

    payload = {
        "queries": [{
            "refId": "log-volume-A",
            "expr": expr,
            "queryType": "range",
            "datasource": {"type": "loki", "uid": LOKI_DATASOURCE_UID},
            "editorMode": "builder",
            "supportingQueryType": "logsVolume",
            "legendFormat": "{{ level }}",
            "step": "",
            "datasourceId": LOKI_DATASOURCE_ID,
            "intervalMs": 1000,
            "maxDataPoints": 1263,
        }],
        "from": from_ms,
        "to": to_ms,
    }

    url = f"{GRAFANA_URL}/api/ds/query?ds_type=loki&requestId=mcp_vol_{uuid.uuid4().hex[:8]}"
    async with httpx.AsyncClient(verify=False, timeout=30) as client:
        resp = await client.post(url, headers=_get_headers(), json=payload)
        if resp.status_code != 200:
            return f"请求失败: HTTP {resp.status_code}\n{resp.text}"
        data = resp.json()

    # 解析 volume 结果
    output_lines = [
        f"服务: {service_name}",
        f"关键词: {keyword or '(无)'}",
        f"时间范围: {time_from} ~ {time_to}",
        "=" * 60,
    ]
    total_count = 0
    for ref_id, result in data.get("results", {}).items():
        stats = []
        for frame in result.get("frames", []):
            meta = frame.get("schema", {}).get("meta", {})
            for stat in meta.get("stats", []):
                stats.append(f"  {stat['displayName']}: {stat['value']}")
            # 提取 level 标签和数值
            fields = frame.get("schema", {}).get("fields", [])
            values = frame.get("data", {}).get("values", [])
            if len(values) >= 2:
                # values[0] = timestamps, values[1] = counts
                counts = values[1] if len(values) > 1 else []
                level_label = ""
                for f in fields:
                    if f.get("labels"):
                        level_label = str(f["labels"])
                count_sum = sum(c for c in counts if isinstance(c, (int, float)))
                total_count += count_sum
                output_lines.append(
                    f"Level [{level_label or 'all'}]: {int(count_sum)} 条"
                )
        if stats:
            output_lines.append("--- 统计 ---")
            output_lines.extend(stats)

    output_lines.insert(4, f"总日志量: {total_count} 条")
    return "\n".join(output_lines)


@mcp.tool()
async def query_log_context(
    service_name: str,
    timestamp_ms: str,
    keyword: str = "",
    before_lines: int = 30,
    after_lines: int = 30,
    pod: str = "",
) -> str:
    """
    获取某条日志前后的上下文日志。

    Args:
        service_name: 服务名称
        timestamp_ms: 目标日志的时间戳(毫秒)，从 query_logs 结果中获取
        keyword: 原始搜索关键词（可选，用于高亮标记）
        before_lines: 向前获取的行数，默认30
        after_lines: 向后获取的行数，默认30
        pod: 指定 pod 名称（可选，精确定位到某个实例）

    Returns:
        目标时间点前后的日志内容
    """
    ts = int(timestamp_ms)
    # 前后各扩展一段时间窗口来获取上下文
    window_ms = 60000  # 前后各1分钟
    from_ms = str(ts - window_ms)
    to_ms = str(ts + window_ms)

    label_selector = f'service_name="{service_name}"'
    if pod:
        label_selector += f', pod="{pod}"'
    expr = "{" + label_selector + "}"

    total_lines = before_lines + after_lines + 1
    payload = {
        "queries": [{
            "refId": "A",
            "expr": expr,
            "queryType": "range",
            "datasource": {"type": "loki", "uid": LOKI_DATASOURCE_UID},
            "editorMode": "builder",
            "maxLines": min(total_lines * 2, 1000),
            "step": "",
            "legendFormat": "",
            "datasourceId": LOKI_DATASOURCE_ID,
            "intervalMs": 500,
            "maxDataPoints": 1263,
        }],
        "from": from_ms,
        "to": to_ms,
    }

    url = f"{GRAFANA_URL}/api/ds/query?ds_type=loki&requestId=mcp_ctx_{uuid.uuid4().hex[:8]}"
    async with httpx.AsyncClient(verify=False, timeout=30) as client:
        resp = await client.post(url, headers=_get_headers(), json=payload)
        if resp.status_code != 200:
            return f"请求失败: HTTP {resp.status_code}\n{resp.text}"
        data = resp.json()

    logs = _extract_log_lines(data)
    if not logs:
        return "未查询到上下文日志"

    # 按时间排序
    logs.sort(key=lambda x: x.get("timestamp", 0) or 0)

    # 找到最接近目标时间戳的日志
    target_idx = 0
    min_diff = float("inf")
    for i, log in enumerate(logs):
        log_ts = log.get("timestamp", 0) or 0
        diff = abs(log_ts - ts)
        if diff < min_diff:
            min_diff = diff
            target_idx = i

    # 截取前后范围
    start = max(0, target_idx - before_lines)
    end = min(len(logs), target_idx + after_lines + 1)
    context_logs = logs[start:end]

    # 格式化输出
    output_lines = [
        f"上下文日志 (目标时间: {timestamp_ms})",
        f"服务: {service_name}" + (f", Pod: {pod}" if pod else ""),
        f"显示范围: 前{target_idx - start}条 + 目标 + 后{end - target_idx - 1}条",
        "=" * 80,
    ]
    for i, log in enumerate(context_logs):
        log_ts = log.get("timestamp")
        if log_ts:
            try:
                dt = datetime.fromtimestamp(log_ts / 1000)
                ts_str = dt.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
            except (OSError, ValueError):
                ts_str = str(log_ts)
        else:
            ts_str = "unknown"
        line = log.get("line", "")
        # 标记目标行
        marker = ">>>" if (i + start) == target_idx else "   "
        output_lines.append(f"{marker} [{ts_str}] {line}")

    return "\n".join(output_lines)


@mcp.tool()
async def list_services(
    time_from: str = "now-1h",
    time_to: str = "now",
) -> str:
    """
    列出 Loki 中所有可用的 service_name（服务列表）。

    Args:
        time_from: 开始时间，默认 now-1h
        time_to: 结束时间，默认 now

    Returns:
        可用的服务名称列表
    """
    from_ms, to_ms = _parse_time_range(time_from, time_to)
    from_sec = int(from_ms) // 1000
    to_sec = int(to_ms) // 1000

    url = (
        f"{GRAFANA_URL}/api/datasources/proxy/uid/{LOKI_DATASOURCE_UID}"
        f"/loki/api/v1/label/service_name/values"
        f"?start={from_sec}&end={to_sec}"
    )
    async with httpx.AsyncClient(verify=False, timeout=30) as client:
        resp = await client.get(url, headers=_get_headers())
        if resp.status_code != 200:
            return f"请求失败: HTTP {resp.status_code}\n{resp.text}"
        data = resp.json()

    values = data.get("data", data.get("values", []))
    if not values:
        return "未获取到服务列表"

    output_lines = [
        f"可用服务列表 (共 {len(values)} 个):",
        "=" * 40,
    ]
    for v in sorted(values):
        output_lines.append(f"  - {v}")
    return "\n".join(output_lines)


@mcp.tool()
async def list_label_values(
    label_name: str,
    time_from: str = "now-1h",
    time_to: str = "now",
) -> str:
    """
    列出 Loki 中某个 label 的所有可用值。

    Args:
        label_name: label 名称，如 service_name, pod, namespace, detected_level
        time_from: 开始时间
        time_to: 结束时间

    Returns:
        该 label 的所有可用值
    """
    from_ms, to_ms = _parse_time_range(time_from, time_to)
    from_sec = int(from_ms) // 1000
    to_sec = int(to_ms) // 1000

    url = (
        f"{GRAFANA_URL}/api/datasources/proxy/uid/{LOKI_DATASOURCE_UID}"
        f"/loki/api/v1/label/{label_name}/values"
        f"?start={from_sec}&end={to_sec}"
    )
    async with httpx.AsyncClient(verify=False, timeout=30) as client:
        resp = await client.get(url, headers=_get_headers())
        if resp.status_code != 200:
            return f"请求失败: HTTP {resp.status_code}\n{resp.text}"
        data = resp.json()

    values = data.get("data", data.get("values", []))
    if not values:
        return f"未获取到 label '{label_name}' 的值"

    output_lines = [
        f"Label '{label_name}' 的值 (共 {len(values)} 个):",
        "=" * 40,
    ]
    for v in sorted(values):
        output_lines.append(f"  - {v}")
    return "\n".join(output_lines)


@mcp.tool()
async def query_logs_by_logql(
    expr: str,
    time_from: str = "now-15m",
    time_to: str = "now",
    max_lines: int = 100,
) -> str:
    """
    直接使用 LogQL 表达式查询日志（高级用法）。

    Args:
        expr: 完整的 LogQL 表达式，如 {service_name="xx"} |= `error` | json
        time_from: 开始时间
        time_to: 结束时间
        max_lines: 最大返回行数

    Returns:
        查询结果
    """
    from_ms, to_ms = _parse_time_range(time_from, time_to)
    max_lines = min(max_lines, 1000)

    payload = {
        "queries": [{
            "refId": "A",
            "expr": expr,
            "queryType": "range",
            "datasource": {"type": "loki", "uid": LOKI_DATASOURCE_UID},
            "editorMode": "code",
            "maxLines": max_lines,
            "step": "",
            "legendFormat": "",
            "datasourceId": LOKI_DATASOURCE_ID,
            "intervalMs": 500,
            "maxDataPoints": 1263,
        }],
        "from": from_ms,
        "to": to_ms,
    }

    url = f"{GRAFANA_URL}/api/ds/query?ds_type=loki&requestId=mcp_raw_{uuid.uuid4().hex[:8]}"
    async with httpx.AsyncClient(verify=False, timeout=30) as client:
        resp = await client.post(url, headers=_get_headers(), json=payload)
        if resp.status_code != 200:
            return f"请求失败: HTTP {resp.status_code}\n{resp.text}"
        data = resp.json()

    logs = _extract_log_lines(data)
    if not logs:
        return f"未查询到日志。\n表达式: {expr}\n时间范围: {time_from} ~ {time_to}"

    output_lines = [
        f"表达式: {expr}",
        f"时间范围: {time_from} ~ {time_to}",
        f"结果数量: {len(logs)} 条",
        "=" * 80,
    ]
    for log in logs:
        ts = log.get("timestamp")
        if ts:
            try:
                dt = datetime.fromtimestamp(ts / 1000)
                ts_str = dt.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
            except (OSError, ValueError):
                ts_str = str(ts)
        else:
            ts_str = "unknown"
        pod = log.get("pod", "")
        line = log.get("line", "")
        output_lines.append(f"[{ts_str}] [{pod}] {line}")

    return "\n".join(output_lines)


if __name__ == "__main__":
    mcp.run(transport="stdio")
