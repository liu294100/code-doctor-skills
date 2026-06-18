"""
Grafana Loki MCP Server v2
通过 Grafana API 查询 Loki 日志，支持：
1. 按 service_name + 关键词搜索日志
2. 日志量统计 (logs volume)
3. 获取某条日志的上下文 (context)
4. 列出可用的 service 列表
5. 自动登录 Grafana 获取/刷新 session（无需手动粘贴 cookie）

v2 改进：
- 自动通过账号密码登录，无需手动维护 session cookie
- Session 过期自动刷新，401 时自动重试
- 查询超时优化（60s），大范围查询不再卡住
"""

import os
import json
import time
import uuid
import httpx
from datetime import datetime, timedelta
from typing import Optional
from mcp.server.fastmcp import FastMCP

# ===== 配置 =====
GRAFANA_URL = os.environ.get("GRAFANA_URL", "https://grafana.xxx.com")
GRAFANA_SESSION = os.environ.get("GRAFANA_SESSION", "")
GRAFANA_TOKEN = os.environ.get("GRAFANA_TOKEN", "")
GRAFANA_ORG_ID = os.environ.get("GRAFANA_ORG_ID", "5")
LOKI_DATASOURCE_UID = os.environ.get("LOKI_DATASOURCE_UID", "ffkfi6twwk6wwf")
LOKI_DATASOURCE_ID = int(os.environ.get("LOKI_DATASOURCE_ID", "6"))

# 自动登录配置
GRAFANA_USERNAME = os.environ.get("GRAFANA_USERNAME", "")
GRAFANA_PASSWORD = os.environ.get("GRAFANA_PASSWORD", "")

# Session 缓存
_session_cache = {
    "session": GRAFANA_SESSION,
    "expire_at": 0,
}

mcp = FastMCP("grafana-loki")


# ===== Session 管理 =====

async def _login_grafana() -> str:
    """通过账号密码登录 Grafana，返回 session cookie"""
    if not GRAFANA_USERNAME or not GRAFANA_PASSWORD:
        return ""
    async with httpx.AsyncClient(verify=False, timeout=15, follow_redirects=False) as client:
        resp = await client.post(
            f"{GRAFANA_URL}/login",
            json={"user": GRAFANA_USERNAME, "password": GRAFANA_PASSWORD},
            headers={"Content-Type": "application/json"},
        )
        if resp.status_code == 200:
            for cookie_header in resp.headers.get_list("set-cookie"):
                if "grafana_session=" in cookie_header:
                    return cookie_header.split("grafana_session=")[1].split(";")[0]
            if "grafana_session" in resp.cookies:
                return resp.cookies["grafana_session"]
    return ""


async def _get_valid_session() -> str:
    """获取有效 session，过期时自动重新登录"""
    global _session_cache
    if GRAFANA_TOKEN:
        return ""
    now = time.time()
    if _session_cache["session"] and _session_cache["expire_at"] > now + 300:
        return _session_cache["session"]
    if _session_cache["session"]:
        try:
            async with httpx.AsyncClient(verify=False, timeout=10) as client:
                resp = await client.get(
                    f"{GRAFANA_URL}/api/org",
                    headers={"Cookie": f'grafana_session={_session_cache["session"]}', "X-Grafana-Org-Id": GRAFANA_ORG_ID},
                )
                if resp.status_code == 200:
                    _session_cache["expire_at"] = now + 1800
                    return _session_cache["session"]
        except Exception:
            pass
    new_session = await _login_grafana()
    if new_session:
        _session_cache["session"] = new_session
        _session_cache["expire_at"] = now + 3600
        return new_session
    return GRAFANA_SESSION


async def _get_headers() -> dict:
    """构建请求头"""
    headers = {
        "accept": "application/json, text/plain, */*",
        "content-type": "application/json",
        "x-datasource-uid": LOKI_DATASOURCE_UID,
        "x-grafana-org-id": GRAFANA_ORG_ID,
        "x-plugin-id": "loki",
        "x-cache-skip": "true",
    }
    if GRAFANA_TOKEN:
        headers["Authorization"] = f"Bearer {GRAFANA_TOKEN}"
    else:
        session = await _get_valid_session()
        headers["Cookie"] = f"grafana_session={session}"
    return headers


async def _request_with_retry(method: str, url: str, headers: dict, **kwargs) -> httpx.Response:
    """带 401 自动重试的请求"""
    async with httpx.AsyncClient(verify=False, timeout=60) as client:
        if method == "GET":
            resp = await client.get(url, headers=headers, **kwargs)
        else:
            resp = await client.post(url, headers=headers, **kwargs)
        if resp.status_code == 401:
            _session_cache["expire_at"] = 0
            _session_cache["session"] = ""
            headers = await _get_headers()
            if method == "GET":
                resp = await client.get(url, headers=headers, **kwargs)
            else:
                resp = await client.post(url, headers=headers, **kwargs)
        return resp


# ===== 工具函数 =====

def _parse_time_range(time_from: str, time_to: str) -> tuple[str, str]:
    """解析时间范围，返回毫秒时间戳"""
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
        for frame in result.get("frames", []):
            values = frame.get("data", {}).get("values", [])
            if not values or len(values) < 3:
                continue
            labels_arr = values[0]
            times_arr = values[1]
            lines_arr = values[2]
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


def _format_timestamp(ts) -> str:
    """格式化时间戳"""
    if ts:
        try:
            dt = datetime.fromtimestamp(ts / 1000)
            return dt.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        except (OSError, ValueError):
            return str(ts)
    return "unknown"


# ===== MCP Tools =====

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
        keyword: 搜索关键词，多个用 | 分隔，如 "error|exception"
        time_from: 开始时间，支持 now-15m, now-1h, now-24h 或 2026-06-18 10:30:00
        time_to: 结束时间，支持 now 或具体时间
        max_lines: 最大返回行数，默认100，最大1000
        extra_labels: 额外 label 过滤，如 'pod="xxx"' 或 'detected_level="error"'
    """
    from_ms, to_ms = _parse_time_range(time_from, time_to)
    label_selector = f'service_name="{service_name}"'
    if extra_labels:
        label_selector += f", {extra_labels}"
    expr = "{" + label_selector + "}"
    if keyword:
        for kw in keyword.split("|"):
            expr += f" |= `{kw.strip()}`"

    payload = {
        "queries": [{
            "refId": "A", "expr": expr, "queryType": "range",
            "datasource": {"type": "loki", "uid": LOKI_DATASOURCE_UID},
            "editorMode": "builder", "maxLines": min(max_lines, 1000),
            "step": "", "legendFormat": "",
            "datasourceId": LOKI_DATASOURCE_ID, "intervalMs": 500, "maxDataPoints": 1263,
        }],
        "from": from_ms, "to": to_ms,
    }

    url = f"{GRAFANA_URL}/api/ds/query?ds_type=loki&requestId=mcp_{uuid.uuid4().hex[:8]}"
    headers = await _get_headers()
    resp = await _request_with_retry("POST", url, headers, json=payload)
    if resp.status_code != 200:
        return f"请求失败: HTTP {resp.status_code}\n{resp.text}"

    logs = _extract_log_lines(resp.json())
    if not logs:
        return f"未查询到日志。\n查询表达式: {expr}\n时间范围: {time_from} ~ {time_to}"

    output = [f"查询: {expr}", f"时间: {time_from} ~ {time_to}", f"结果: {len(logs)} 条", "=" * 80]
    for log in logs:
        output.append(f"[{_format_timestamp(log.get('timestamp'))}] [{log.get('pod', '')}] {log.get('line', '')}")
    return "\n".join(output)


@mcp.tool()
async def query_logs_volume(
    service_name: str,
    keyword: str = "",
    time_from: str = "now-1h",
    time_to: str = "now",
    extra_labels: str = "",
) -> str:
    """
    查询日志量统计（按 level 分组）。
    Args:
        service_name: 服务名称
        keyword: 搜索关键词
        time_from: 开始时间
        time_to: 结束时间
        extra_labels: 额外label过滤
    """
    from_ms, to_ms = _parse_time_range(time_from, time_to)
    label_selector = f'service_name="{service_name}"'
    if extra_labels:
        label_selector += f", {extra_labels}"
    inner_expr = "{" + label_selector + "}"
    if keyword:
        for kw in keyword.split("|"):
            inner_expr += f" |= `{kw.strip()}`"

    expr = f"sum by (level) (count_over_time({inner_expr} | drop __error__[$__auto]))"
    payload = {
        "queries": [{
            "refId": "log-volume-A", "expr": expr, "queryType": "range",
            "datasource": {"type": "loki", "uid": LOKI_DATASOURCE_UID},
            "editorMode": "builder", "supportingQueryType": "logsVolume",
            "legendFormat": "{{ level }}", "step": "",
            "datasourceId": LOKI_DATASOURCE_ID, "intervalMs": 1000, "maxDataPoints": 1263,
        }],
        "from": from_ms, "to": to_ms,
    }

    url = f"{GRAFANA_URL}/api/ds/query?ds_type=loki&requestId=mcp_vol_{uuid.uuid4().hex[:8]}"
    headers = await _get_headers()
    resp = await _request_with_retry("POST", url, headers, json=payload)
    if resp.status_code != 200:
        return f"请求失败: HTTP {resp.status_code}\n{resp.text}"

    data = resp.json()
    output = [f"服务: {service_name}", f"关键词: {keyword or '(无)'}", f"时间: {time_from} ~ {time_to}", "=" * 60]
    total_count = 0
    for ref_id, result in data.get("results", {}).items():
        for frame in result.get("frames", []):
            fields = frame.get("schema", {}).get("fields", [])
            values = frame.get("data", {}).get("values", [])
            if len(values) >= 2:
                counts = values[1]
                level_label = ""
                for f in fields:
                    if f.get("labels"):
                        level_label = str(f["labels"])
                count_sum = sum(c for c in counts if isinstance(c, (int, float)))
                total_count += count_sum
                output.append(f"Level [{level_label or 'all'}]: {int(count_sum)} 条")
    output.insert(4, f"总日志量: {total_count} 条")
    return "\n".join(output)


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
    获取某条日志前后的上下文。
    Args:
        service_name: 服务名称
        timestamp_ms: 目标日志时间戳(毫秒)
        keyword: 原始关键词（可选）
        before_lines: 向前行数，默认30
        after_lines: 向后行数，默认30
        pod: 指定 pod（可选）
    """
    ts = int(timestamp_ms)
    from_ms = str(ts - 60000)
    to_ms = str(ts + 60000)

    label_selector = f'service_name="{service_name}"'
    if pod:
        label_selector += f', pod="{pod}"'
    expr = "{" + label_selector + "}"

    payload = {
        "queries": [{
            "refId": "A", "expr": expr, "queryType": "range",
            "datasource": {"type": "loki", "uid": LOKI_DATASOURCE_UID},
            "editorMode": "builder", "maxLines": min((before_lines + after_lines + 1) * 2, 1000),
            "step": "", "legendFormat": "",
            "datasourceId": LOKI_DATASOURCE_ID, "intervalMs": 500, "maxDataPoints": 1263,
        }],
        "from": from_ms, "to": to_ms,
    }

    url = f"{GRAFANA_URL}/api/ds/query?ds_type=loki&requestId=mcp_ctx_{uuid.uuid4().hex[:8]}"
    headers = await _get_headers()
    resp = await _request_with_retry("POST", url, headers, json=payload)
    if resp.status_code != 200:
        return f"请求失败: HTTP {resp.status_code}\n{resp.text}"

    logs = _extract_log_lines(resp.json())
    if not logs:
        return "未查询到上下文日志"

    logs.sort(key=lambda x: x.get("timestamp", 0) or 0)
    target_idx = min(range(len(logs)), key=lambda i: abs((logs[i].get("timestamp", 0) or 0) - ts))
    start = max(0, target_idx - before_lines)
    end = min(len(logs), target_idx + after_lines + 1)

    output = [f"上下文日志 (目标: {timestamp_ms})", f"服务: {service_name}" + (f", Pod: {pod}" if pod else ""), "=" * 80]
    for i, log in enumerate(logs[start:end]):
        marker = ">>>" if (i + start) == target_idx else "   "
        output.append(f"{marker} [{_format_timestamp(log.get('timestamp'))}] {log.get('line', '')}")
    return "\n".join(output)


@mcp.tool()
async def list_services(time_from: str = "now-1h", time_to: str = "now") -> str:
    """列出 Loki 中所有可用的 service_name。"""
    from_ms, to_ms = _parse_time_range(time_from, time_to)
    url = f"{GRAFANA_URL}/api/datasources/proxy/uid/{LOKI_DATASOURCE_UID}/loki/api/v1/label/service_name/values?start={int(from_ms)//1000}&end={int(to_ms)//1000}"
    headers = await _get_headers()
    resp = await _request_with_retry("GET", url, headers)
    if resp.status_code != 200:
        return f"请求失败: HTTP {resp.status_code}\n{resp.text}"
    values = resp.json().get("data", [])
    if not values:
        return "未获取到服务列表"
    return f"可用服务 (共{len(values)}个):\n" + "\n".join(f"  - {v}" for v in sorted(values))


@mcp.tool()
async def list_label_values(label_name: str, time_from: str = "now-1h", time_to: str = "now") -> str:
    """列出某个 label 的所有可用值（如 pod, namespace, detected_level）。"""
    from_ms, to_ms = _parse_time_range(time_from, time_to)
    url = f"{GRAFANA_URL}/api/datasources/proxy/uid/{LOKI_DATASOURCE_UID}/loki/api/v1/label/{label_name}/values?start={int(from_ms)//1000}&end={int(to_ms)//1000}"
    headers = await _get_headers()
    resp = await _request_with_retry("GET", url, headers)
    if resp.status_code != 200:
        return f"请求失败: HTTP {resp.status_code}\n{resp.text}"
    values = resp.json().get("data", [])
    if not values:
        return f"未获取到 label '{label_name}' 的值"
    return f"Label '{label_name}' (共{len(values)}个):\n" + "\n".join(f"  - {v}" for v in sorted(values))


@mcp.tool()
async def query_logs_by_logql(expr: str, time_from: str = "now-15m", time_to: str = "now", max_lines: int = 100) -> str:
    """直接使用 LogQL 表达式查询（高级用法）。"""
    from_ms, to_ms = _parse_time_range(time_from, time_to)
    payload = {
        "queries": [{
            "refId": "A", "expr": expr, "queryType": "range",
            "datasource": {"type": "loki", "uid": LOKI_DATASOURCE_UID},
            "editorMode": "code", "maxLines": min(max_lines, 1000),
            "step": "", "legendFormat": "",
            "datasourceId": LOKI_DATASOURCE_ID, "intervalMs": 500, "maxDataPoints": 1263,
        }],
        "from": from_ms, "to": to_ms,
    }

    url = f"{GRAFANA_URL}/api/ds/query?ds_type=loki&requestId=mcp_raw_{uuid.uuid4().hex[:8]}"
    headers = await _get_headers()
    resp = await _request_with_retry("POST", url, headers, json=payload)
    if resp.status_code != 200:
        return f"请求失败: HTTP {resp.status_code}\n{resp.text}"

    logs = _extract_log_lines(resp.json())
    if not logs:
        return f"未查询到日志。\n表达式: {expr}\n时间: {time_from} ~ {time_to}"

    output = [f"表达式: {expr}", f"时间: {time_from} ~ {time_to}", f"结果: {len(logs)} 条", "=" * 80]
    for log in logs:
        output.append(f"[{_format_timestamp(log.get('timestamp'))}] [{log.get('pod', '')}] {log.get('line', '')}")
    return "\n".join(output)


if __name__ == "__main__":
    mcp.run(transport="stdio")
