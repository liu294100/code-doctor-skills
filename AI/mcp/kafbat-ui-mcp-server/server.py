"""
Kafbat UI MCP Server - 通过 Kafbat UI (kafbat/kafka-ui v1.x) REST API 管理 Kafka

替代旧的 provectus kafka-ui MCP，主要差异：
- 登录：Kafbat 使用表单登录（POST /login）+ SESSION Cookie，本服务自动登录并在会话失效时重登
- 消息：使用 /messages/v2 接口（mode=LATEST/EARLIEST/FROM_OFFSET/...），返回字段为 value

支持功能:
- 集群: 集群列表、Broker 列表
- Topic: 列表、详情、配置、创建、删除、批量创建
- 消息: 发送、消费（支持关键字过滤、指定分区、按 offset/时间戳定位）
- 消费组: 列表、Topic 关联消费组（含 Lag）

使用方式: pip install -r requirements.txt && python server.py

环境变量:
- KAFBAT_UI_URL: Kafbat UI 地址，如 https://kafka-ui-v2.test.xxxxx.com
- KAFBAT_UI_USERNAME / KAFBAT_UI_PASSWORD: 登录账号密码（未开启认证可不填）
- KAFBAT_UI_CLUSTER: 默认集群名称，默认 kafka-msk-test
- KAFBAT_UI_VERIFY_SSL: 是否校验证书，默认 true
- KAFBAT_UI_MAX_VALUE_LEN: 单条消息 value 最大返回长度，默认 5000（0 表示不截断）
"""
import asyncio
import json
import logging
import os
import random
from datetime import datetime
from typing import Any, Dict, Optional

import httpx
from mcp.server.fastmcp import FastMCP

# 配置
KAFBAT_UI_URL = os.environ.get("KAFBAT_UI_URL", "http://localhost:8080").rstrip("/")
USERNAME = os.environ.get("KAFBAT_UI_USERNAME", "")
PASSWORD = os.environ.get("KAFBAT_UI_PASSWORD", "")
DEFAULT_CLUSTER = os.environ.get("KAFBAT_UI_CLUSTER", "kafka-msk-test")
VERIFY_SSL = os.environ.get("KAFBAT_UI_VERIFY_SSL", "true").lower() != "false"
MAX_VALUE_LEN = int(os.environ.get("KAFBAT_UI_MAX_VALUE_LEN", "5000"))

mcp = FastMCP("kafbat-ui")

# 屏蔽 httpx 每次请求的 INFO 日志
logging.getLogger("httpx").setLevel(logging.WARNING)

_client: Optional[httpx.AsyncClient] = None
_login_lock = asyncio.Lock()


# ==================== HTTP 基础 ====================

def _get_client() -> httpx.AsyncClient:
    """获取共享 HTTP 客户端（复用 SESSION Cookie）"""
    global _client
    if _client is None:
        _client = httpx.AsyncClient(
            base_url=KAFBAT_UI_URL,
            timeout=60.0,
            verify=VERIFY_SSL,
            follow_redirects=False,
        )
    return _client


async def _login() -> None:
    """表单登录，成功后 SESSION Cookie 保存在客户端中"""
    if not USERNAME:
        return
    client = _get_client()
    client.cookies.clear()
    resp = await client.post("/login", data={"username": USERNAME, "password": PASSWORD})
    # 登录成功重定向到 /，失败重定向到 /login?error
    location = resp.headers.get("location", "")
    if resp.status_code not in (200, 302) or "error" in location:
        raise RuntimeError(f"Kafbat UI 登录失败: status={resp.status_code}, location={location}")


def _need_login(resp: httpx.Response) -> bool:
    """判断会话是否失效"""
    if resp.status_code == 401:
        return True
    if resp.status_code in (302, 303) and "/login" in resp.headers.get("location", ""):
        return True
    return False


async def _request(method: str, path: str, **kwargs) -> httpx.Response:
    """发送请求，会话失效时自动重新登录并重试一次"""
    client = _get_client()
    if USERNAME and "SESSION" not in client.cookies:
        async with _login_lock:
            if "SESSION" not in client.cookies:
                await _login()
    resp = await client.request(method, path, **kwargs)
    if USERNAME and _need_login(resp):
        async with _login_lock:
            await _login()
        resp = await client.request(method, path, **kwargs)
    return resp


def _base(cluster: str = "") -> str:
    return f"/api/clusters/{cluster or DEFAULT_CLUSTER}"


def _dump(data: Any) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2)


def _result(resp: httpx.Response) -> str:
    """统一处理响应"""
    if resp.is_success:
        if not resp.content:
            return _dump({"success": True, "status_code": resp.status_code})
        try:
            return _dump(resp.json())
        except Exception:
            return _dump({"success": True, "status_code": resp.status_code, "text": resp.text})
    return _dump({"success": False, "status_code": resp.status_code, "error": resp.text[:2000]})


def _murmur2(data: bytes) -> int:
    """Kafka DefaultPartitioner 使用的 murmur2 哈希（与 Java 客户端结果一致）"""
    length = len(data)
    seed = 0x9747B28C
    m = 0x5BD1E995
    r = 24
    h = (seed ^ length) & 0xFFFFFFFF
    length4 = length // 4
    for i in range(length4):
        i4 = i * 4
        k = (data[i4] & 0xFF) + ((data[i4 + 1] & 0xFF) << 8) \
            + ((data[i4 + 2] & 0xFF) << 16) + ((data[i4 + 3] & 0xFF) << 24)
        k = (k * m) & 0xFFFFFFFF
        k ^= k >> r
        k = (k * m) & 0xFFFFFFFF
        h = (h * m) & 0xFFFFFFFF
        h ^= k
    extra = length % 4
    index = length & ~3
    if extra == 3:
        h ^= (data[index + 2] & 0xFF) << 16
    if extra >= 2:
        h ^= (data[index + 1] & 0xFF) << 8
    if extra >= 1:
        h ^= data[index] & 0xFF
        h = (h * m) & 0xFFFFFFFF
    h ^= h >> 13
    h = (h * m) & 0xFFFFFFFF
    h ^= h >> 15
    # 转为 Java 有符号 int
    return h - 0x100000000 if h & 0x80000000 else h


def _to_epoch_ms(value: str) -> Optional[int]:
    """支持毫秒时间戳或 'YYYY-MM-DD HH:MM:SS'（本地时间）格式"""
    if not value:
        return None
    value = value.strip()
    if value.isdigit():
        return int(value)
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d"):
        try:
            return int(datetime.strptime(value, fmt).timestamp() * 1000)
        except ValueError:
            continue
    raise ValueError(f"无法解析时间: {value}，请使用毫秒时间戳或 YYYY-MM-DD HH:MM:SS")


# ==================== 集群 ====================

@mcp.tool()
async def list_clusters() -> str:
    """列出所有 Kafka 集群（名称、状态、Broker 数、Topic 数、版本）。"""
    resp = await _request("GET", "/api/clusters")
    if not resp.is_success:
        return _result(resp)
    return _dump([
        {
            "name": c.get("name"),
            "status": c.get("status"),
            "brokerCount": c.get("brokerCount"),
            "topicCount": c.get("topicCount"),
            "onlinePartitionCount": c.get("onlinePartitionCount"),
            "version": c.get("version"),
            "readOnly": c.get("readOnly"),
        }
        for c in resp.json()
    ])


@mcp.tool()
async def list_brokers(cluster: str = "") -> str:
    """列出集群 Broker 信息。

    Args:
        cluster: 集群名称，不指定则使用默认集群
    """
    return _result(await _request("GET", f"{_base(cluster)}/brokers"))


# ==================== Topic ====================

@mcp.tool()
async def list_topics(cluster: str = "", page: int = 1, per_page: int = 25,
                      show_internal: bool = False, search: str = "") -> str:
    """列出 Topic 列表（精简字段）。

    Args:
        cluster: 集群名称，不指定则使用默认集群
        page: 页码，默认 1
        per_page: 每页数量，默认 25
        show_internal: 是否显示内部 Topic，默认 False
        search: 按名称模糊搜索（可选）
    """
    params: Dict[str, Any] = {
        "page": page,
        "perPage": per_page,
        "showInternal": str(show_internal).lower(),
    }
    if search:
        params["search"] = search
    resp = await _request("GET", f"{_base(cluster)}/topics", params=params)
    if not resp.is_success:
        return _result(resp)
    data = resp.json()
    return _dump({
        "pageCount": data.get("pageCount"),
        "topics": [
            {
                "name": t.get("name"),
                "partitionCount": t.get("partitionCount"),
                "replicationFactor": t.get("replicationFactor"),
                "inSyncReplicas": t.get("inSyncReplicas"),
                "underReplicatedPartitions": t.get("underReplicatedPartitions"),
                "messagesCount": t.get("messagesCount"),
                "segmentSize": t.get("segmentSize"),
                "cleanUpPolicy": t.get("cleanUpPolicy"),
            }
            for t in data.get("topics", [])
        ],
    })


@mcp.tool()
async def get_topic(topic_name: str, cluster: str = "") -> str:
    """获取 Topic 详情，包含分区、Leader、副本、ISR、offset 范围等。

    Args:
        topic_name: Topic 名称
        cluster: 集群名称，不指定则使用默认集群
    """
    return _result(await _request("GET", f"{_base(cluster)}/topics/{topic_name}"))


@mcp.tool()
async def get_topic_config(topic_name: str, cluster: str = "", only_key: bool = True) -> str:
    """获取 Topic 配置。

    Args:
        topic_name: Topic 名称
        cluster: 集群名称，不指定则使用默认集群
        only_key: 只返回关键配置及动态覆盖配置，默认 True；False 返回全部
    """
    resp = await _request("GET", f"{_base(cluster)}/topics/{topic_name}/config")
    if not resp.is_success or not only_key:
        return _result(resp)
    key_configs = {"min.insync.replicas", "cleanup.policy", "retention.ms",
                   "retention.bytes", "max.message.bytes", "segment.bytes"}
    return _dump([
        {
            "name": item.get("name"),
            "value": item.get("value"),
            "defaultValue": item.get("defaultValue"),
            "source": item.get("source"),
        }
        for item in resp.json()
        # MSK 会把所有项都标为 DYNAMIC_TOPIC_CONFIG，因此只保留关键配置 + 与默认值不同的动态配置
        if item.get("name") in key_configs
        or (item.get("source") == "DYNAMIC_TOPIC_CONFIG"
            and item.get("defaultValue") is not None
            and item.get("value") != item.get("defaultValue"))
    ])


@mcp.tool()
async def create_topic(topic_name: str, partitions: int = 3, replication_factor: int = 3,
                       min_insync_replicas: int = 1, cleanup_policy: str = "delete",
                       retention_ms: str = "", cluster: str = "") -> str:
    """创建 Topic。

    Args:
        topic_name: Topic 名称
        partitions: 分区数，默认 3
        replication_factor: 副本因子，默认 3
        min_insync_replicas: 最小同步副本数，默认 1
        cleanup_policy: 清理策略，delete 或 compact，默认 delete
        retention_ms: 保留时长毫秒（可选，-1 表示永久）
        cluster: 集群名称，不指定则使用默认集群
    """
    configs = {
        "cleanup.policy": cleanup_policy,
        "min.insync.replicas": str(min_insync_replicas),
    }
    if retention_ms:
        configs["retention.ms"] = str(retention_ms)
    payload = {
        "name": topic_name,
        "partitions": partitions,
        "replicationFactor": replication_factor,
        "configs": configs,
    }
    return _result(await _request("POST", f"{_base(cluster)}/topics", json=payload))


@mcp.tool()
async def batch_create_topics(topics_config: str, cluster: str = "") -> str:
    """批量创建 Topic。

    Args:
        topics_config: Topic 配置列表 JSON，格式:
            [{"name": "topic1", "partitions": 3, "replicas": 3, "minISR": 1}]
        cluster: 集群名称，不指定则使用默认集群
    """
    try:
        configs = json.loads(topics_config)
    except Exception as e:
        return _dump({"success": False, "error": f"JSON 解析失败: {e}"})
    results = []
    for cfg in configs:
        result = await create_topic(
            topic_name=cfg.get("name"),
            partitions=cfg.get("partitions", 3),
            replication_factor=cfg.get("replicas", 3),
            min_insync_replicas=cfg.get("minISR", 1),
            cluster=cluster,
        )
        results.append({"topic": cfg.get("name"), "result": json.loads(result)})
    return _dump({"totalCount": len(configs), "results": results})


@mcp.tool()
async def delete_topic(topic_name: str, confirm: bool = False, cluster: str = "") -> str:
    """删除 Topic（不可恢复）。

    Args:
        topic_name: Topic 名称
        confirm: 必须显式传 True 才会执行删除
        cluster: 集群名称，不指定则使用默认集群
    """
    if not confirm:
        return _dump({"success": False, "error": "删除 Topic 不可恢复，请确认后传 confirm=true"})
    return _result(await _request("DELETE", f"{_base(cluster)}/topics/{topic_name}"))


# ==================== 消息 ====================

@mcp.tool()
async def produce_message(topic_name: str, content: str, key: str = "", partition: int = -1,
                          headers: str = "", cluster: str = "") -> str:
    """发送消息到 Topic（String 序列化）。

    Args:
        topic_name: Topic 名称
        content: 消息内容（字符串或 JSON 字符串）
        key: 消息 Key（可选）
        partition: 目标分区，-1 表示按 Key 自动分区，默认 -1
        headers: 消息头 JSON 对象字符串，如 {"traceId":"xxx"}（可选）
        cluster: 集群名称，不指定则使用默认集群
    """
    payload: Dict[str, Any] = {
        # Kafbat v1.x 请求体字段为 value（旧 kafka-ui 为 content）
        "value": content,
        "keySerde": "String",
        "valueSerde": "String",
        "keepContents": False,
    }
    if key:
        payload["key"] = key
    if partition < 0:
        # Kafbat 要求 partition 必填：有 Key 时按 Kafka 默认分区算法计算，否则随机
        topic_resp = await _request("GET", f"{_base(cluster)}/topics/{topic_name}")
        if not topic_resp.is_success:
            return _result(topic_resp)
        partition_count = len(topic_resp.json().get("partitions") or []) or 1
        if key:
            partition = (_murmur2(key.encode("utf-8")) & 0x7FFFFFFF) % partition_count
        else:
            partition = random.randrange(partition_count)
    payload["partition"] = partition
    if headers:
        try:
            payload["headers"] = json.loads(headers)
        except Exception as e:
            return _dump({"success": False, "error": f"headers JSON 解析失败: {e}"})
    resp = await _request("POST", f"{_base(cluster)}/topics/{topic_name}/messages", json=payload)
    if resp.is_success:
        return _dump({"success": True, "topic": topic_name, "partition": partition, "key": key or None})
    return _result(resp)


@mcp.tool()
async def consume_messages(topic_name: str, limit: int = 20, mode: str = "LATEST",
                           filter_text: str = "", partitions: str = "", offset: int = -1,
                           timestamp: str = "", key_serde: str = "String",
                           value_serde: str = "String", cluster: str = "") -> str:
    """查询 Topic 中的消息（对应 UI 的 Messages 页）。

    Args:
        topic_name: Topic 名称
        limit: 最大返回消息数，默认 20，最大 500
        mode: 定位方式，默认 LATEST
            LATEST（最新往前）/ EARLIEST（从头）/ FROM_OFFSET / TO_OFFSET /
            FROM_TIMESTAMP / TO_TIMESTAMP
        filter_text: 关键字过滤，匹配 key/value/headers（如订单号、账号）
        partitions: 指定分区，逗号分隔，如 "0,3"（可选）
        offset: mode 为 FROM_OFFSET/TO_OFFSET 时的 offset
        timestamp: mode 为 FROM_TIMESTAMP/TO_TIMESTAMP 时的时间，毫秒或 'YYYY-MM-DD HH:MM:SS'
        key_serde: Key 反序列化方式，默认 String
        value_serde: Value 反序列化方式，默认 String
        cluster: 集群名称，不指定则使用默认集群
    """
    mode = mode.upper()
    params: Dict[str, Any] = {
        "mode": mode,
        "limit": max(1, min(limit, 500)),
        "keySerde": key_serde,
        "valueSerde": value_serde,
    }
    if filter_text:
        params["stringFilter"] = filter_text
    if partitions:
        params["partitions"] = [p.strip() for p in partitions.split(",") if p.strip()]
    if mode in ("FROM_OFFSET", "TO_OFFSET"):
        if offset < 0:
            return _dump({"success": False, "error": f"mode={mode} 需要指定 offset"})
        params["offset"] = offset
    if mode in ("FROM_TIMESTAMP", "TO_TIMESTAMP"):
        try:
            ts = _to_epoch_ms(timestamp)
        except ValueError as e:
            return _dump({"success": False, "error": str(e)})
        if ts is None:
            return _dump({"success": False, "error": f"mode={mode} 需要指定 timestamp"})
        params["timestamp"] = ts

    resp = await _request(
        "GET",
        f"{_base(cluster)}/topics/{topic_name}/messages/v2",
        params=params,
        headers={"Accept": "text/event-stream"},
    )
    if not resp.is_success:
        return _result(resp)

    messages = []
    consuming: Dict[str, Any] = {}
    errors = []
    # 解析 SSE：PHASE / CONSUMING / MESSAGE / DONE / EMIT_THROTTLING
    for line in resp.text.splitlines():
        if not line.startswith("data:"):
            continue
        try:
            event = json.loads(line[5:])
        except Exception:
            continue
        event_type = event.get("type")
        if event_type == "MESSAGE":
            msg = event.get("message") or {}
            value = msg.get("value")
            if MAX_VALUE_LEN > 0 and isinstance(value, str) and len(value) > MAX_VALUE_LEN:
                value = value[:MAX_VALUE_LEN] + f"...(截断，原长度 {len(msg.get('value'))})"
            messages.append({
                "partition": msg.get("partition"),
                "offset": msg.get("offset"),
                "timestamp": msg.get("timestamp"),
                "key": msg.get("key"),
                "headers": msg.get("headers") or None,
                "value": value,
            })
        elif event_type in ("CONSUMING", "DONE"):
            consuming = event.get("consuming") or consuming
        elif event_type == "PHASE":
            phase_name = (event.get("phase") or {}).get("name", "")
            if "error" in phase_name.lower():
                errors.append(phase_name)

    result: Dict[str, Any] = {
        "topic": topic_name,
        "mode": mode,
        "returned": len(messages),
        "messagesScanned": consuming.get("messagesConsumed"),
        "bytesScanned": consuming.get("bytesConsumed"),
        "elapsedMs": consuming.get("elapsedMs"),
        "messages": messages,
    }
    if errors:
        result["errors"] = errors
    return _dump(result)


# ==================== 消费组 ====================

@mcp.tool()
async def list_consumer_groups(cluster: str = "", search: str = "", page: int = 1,
                               per_page: int = 25) -> str:
    """分页查询消费组列表。

    Args:
        cluster: 集群名称，不指定则使用默认集群
        search: 按 groupId 模糊搜索（可选）
        page: 页码，默认 1
        per_page: 每页数量，默认 25
    """
    params: Dict[str, Any] = {"page": page, "perPage": per_page}
    if search:
        params["search"] = search
    resp = await _request("GET", f"{_base(cluster)}/consumer-groups/paged", params=params)
    if not resp.is_success:
        return _result(resp)
    data = resp.json()
    return _dump({
        "pageCount": data.get("pageCount"),
        "consumerGroups": [
            {
                "groupId": g.get("groupId"),
                "state": g.get("state"),
                "members": g.get("members"),
                "topics": g.get("topics"),
                "consumerLag": g.get("consumerLag"),
                "coordinator": (g.get("coordinator") or {}).get("id"),
            }
            for g in data.get("consumerGroups", [])
        ],
    })


@mcp.tool()
async def get_consumer_group(group_id: str, cluster: str = "") -> str:
    """获取消费组详情，包含每个分区的 currentOffset、endOffset、lag、consumerId。

    Args:
        group_id: 消费组 ID
        cluster: 集群名称，不指定则使用默认集群
    """
    return _result(await _request("GET", f"{_base(cluster)}/consumer-groups/{group_id}"))


@mcp.tool()
async def get_topic_consumer_groups(topic_name: str, cluster: str = "") -> str:
    """查询订阅某个 Topic 的消费组及其 Lag。

    Args:
        topic_name: Topic 名称
        cluster: 集群名称，不指定则使用默认集群
    """
    resp = await _request("GET", f"{_base(cluster)}/topics/{topic_name}/consumer-groups")
    if not resp.is_success:
        return _result(resp)
    return _dump([
        {
            "groupId": g.get("groupId"),
            "state": g.get("state"),
            "members": g.get("members"),
            "consumerLag": g.get("consumerLag"),
            "partitionAssignor": g.get("partitionAssignor"),
        }
        for g in resp.json()
    ])


if __name__ == "__main__":
    mcp.run()
