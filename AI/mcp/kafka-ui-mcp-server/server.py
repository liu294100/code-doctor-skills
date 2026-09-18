"""
Kafka UI MCP Server - 通过 Kafka UI REST API 管理 Kafka Topic 和消息

支持功能:
- Topic 管理: 创建、查询、删除 Topic
- 消息管理: 发送消息、消费消息
- 集群信息: 查询集群列表

使用方式: pip install mcp httpx && python server.py

环境变量:
- KAFKA_UI_URL: Kafka UI 地址，默认 http://localhost:8080
- KAFKA_UI_CLUSTER: 默认集群名称，默认 kafka-msk-test
"""
import os
import json
from typing import Optional, List, Dict, Any

import httpx
from mcp.server.fastmcp import FastMCP

# 配置
KAFKA_UI_URL = os.environ.get("KAFKA_UI_URL", "http://localhost:8080")
DEFAULT_CLUSTER = os.environ.get("KAFKA_UI_CLUSTER", "kafka-msk-test")

mcp = FastMCP("kafka-ui")


def _get_base_url(cluster: str = None) -> str:
    """获取 API 基础 URL"""
    c = cluster or DEFAULT_CLUSTER
    return f"{KAFKA_UI_URL}/api/clusters/{c}"


@mcp.tool()
async def list_clusters() -> str:
    """列出所有 Kafka 集群。
    
    Returns:
        集群列表 JSON
    """
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.get(f"{KAFKA_UI_URL}/api/clusters")
        try:
            return json.dumps(resp.json(), ensure_ascii=False, indent=2)
        except Exception:
            return json.dumps({"status_code": resp.status_code, "text": resp.text}, ensure_ascii=False)


@mcp.tool()
async def list_topics(cluster: str = "", page: int = 1, per_page: int = 25, 
                      show_internal: bool = True, search: str = "") -> str:
    """列出 Topic 列表。
    
    Args:
        cluster: 集群名称，不指定则使用默认集群
        page: 页码，默认 1
        per_page: 每页数量，默认 25
        show_internal: 是否显示内部 Topic，默认 True
        search: 搜索关键字（可选）
    
    Returns:
        Topic 列表 JSON
    """
    base_url = _get_base_url(cluster)
    params = {
        "page": page,
        "perPage": per_page,
        "showInternal": str(show_internal).lower()
    }
    if search:
        params["search"] = search
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.get(f"{base_url}/topics", params=params)
        try:
            return json.dumps(resp.json(), ensure_ascii=False, indent=2)
        except Exception:
            return json.dumps({"status_code": resp.status_code, "text": resp.text}, ensure_ascii=False)


@mcp.tool()
async def get_topic(topic_name: str, cluster: str = "") -> str:
    """获取 Topic 详情。
    
    Args:
        topic_name: Topic 名称
        cluster: 集群名称，不指定则使用默认集群
    
    Returns:
        Topic 详情 JSON，包含分区、副本、ISR 等信息
    """
    base_url = _get_base_url(cluster)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.get(f"{base_url}/topics/{topic_name}")
        try:
            return json.dumps(resp.json(), ensure_ascii=False, indent=2)
        except Exception:
            return json.dumps({"status_code": resp.status_code, "text": resp.text}, ensure_ascii=False)


@mcp.tool()
async def get_topic_config(topic_name: str, cluster: str = "") -> str:
    """获取 Topic 配置。
    
    Args:
        topic_name: Topic 名称
        cluster: 集群名称，不指定则使用默认集群
    
    Returns:
        Topic 配置 JSON，包含 min.insync.replicas、cleanup.policy 等配置项
    """
    base_url = _get_base_url(cluster)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.get(f"{base_url}/topics/{topic_name}/config")
        try:
            data = resp.json()
            # 简化输出，只返回关键配置
            simplified = []
            key_configs = ["min.insync.replicas", "cleanup.policy", "retention.ms", 
                          "retention.bytes", "max.message.bytes", "replication.factor"]
            for item in data:
                if item.get("name") in key_configs or item.get("source") == "DYNAMIC_TOPIC_CONFIG":
                    simplified.append({
                        "name": item.get("name"),
                        "value": item.get("value"),
                        "defaultValue": item.get("defaultValue"),
                        "source": item.get("source")
                    })
            return json.dumps(simplified, ensure_ascii=False, indent=2)
        except Exception:
            return json.dumps({"status_code": resp.status_code, "text": resp.text}, ensure_ascii=False)


@mcp.tool()
async def create_topic(topic_name: str, partitions: int = 3, replication_factor: int = 3,
                       min_insync_replicas: int = 1, cleanup_policy: str = "delete",
                       cluster: str = "") -> str:
    """创建 Topic。
    
    Args:
        topic_name: Topic 名称
        partitions: 分区数，默认 3
        replication_factor: 副本因子，默认 3
        min_insync_replicas: 最小同步副本数，默认 1
        cleanup_policy: 清理策略，delete 或 compact，默认 delete
        cluster: 集群名称，不指定则使用默认集群
    
    Returns:
        创建结果 JSON
    """
    base_url = _get_base_url(cluster)
    
    payload = {
        "name": topic_name,
        "partitions": partitions,
        "replicationFactor": str(replication_factor),
        "configs": {
            "cleanup.policy": cleanup_policy,
            "min.insync.replicas": str(min_insync_replicas)
        }
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(
            f"{base_url}/topics",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        try:
            if resp.status_code == 200:
                return json.dumps({
                    "success": True,
                    "message": f"Topic '{topic_name}' 创建成功",
                    "data": resp.json()
                }, ensure_ascii=False, indent=2)
            else:
                return json.dumps({
                    "success": False,
                    "status_code": resp.status_code,
                    "error": resp.text
                }, ensure_ascii=False, indent=2)
        except Exception as e:
            return json.dumps({"success": False, "error": str(e)}, ensure_ascii=False)


@mcp.tool()
async def delete_topic(topic_name: str, cluster: str = "") -> str:
    """删除 Topic。
    
    Args:
        topic_name: Topic 名称
        cluster: 集群名称，不指定则使用默认集群
    
    Returns:
        删除结果 JSON
    """
    base_url = _get_base_url(cluster)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.delete(f"{base_url}/topics/{topic_name}")
        if resp.status_code == 200:
            return json.dumps({
                "success": True,
                "message": f"Topic '{topic_name}' 删除成功"
            }, ensure_ascii=False, indent=2)
        else:
            return json.dumps({
                "success": False,
                "status_code": resp.status_code,
                "error": resp.text
            }, ensure_ascii=False, indent=2)


@mcp.tool()
async def produce_message(topic_name: str, content: str, key: str = "",
                          partition: int = 0, cluster: str = "") -> str:
    """发送消息到 Topic。
    
    Args:
        topic_name: Topic 名称
        content: 消息内容（字符串或 JSON 字符串）
        key: 消息 Key（可选）
        partition: 目标分区，默认 0
        cluster: 集群名称，不指定则使用默认集群
    
    Returns:
        发送结果 JSON
    """
    base_url = _get_base_url(cluster)
    
    payload = {
        "partition": partition,
        "content": content,
        "keySerde": "String",
        "valueSerde": "String"
    }
    if key:
        payload["key"] = key
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(
            f"{base_url}/topics/{topic_name}/messages",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        if resp.status_code == 200:
            return json.dumps({
                "success": True,
                "message": f"消息发送成功到 Topic '{topic_name}'",
                "key": key,
                "partition": partition
            }, ensure_ascii=False, indent=2)
        else:
            return json.dumps({
                "success": False,
                "status_code": resp.status_code,
                "error": resp.text
            }, ensure_ascii=False, indent=2)


@mcp.tool()
async def consume_messages(topic_name: str, limit: int = 10, seek_type: str = "BEGINNING",
                           cluster: str = "") -> str:
    """消费 Topic 中的消息。
    
    Args:
        topic_name: Topic 名称
        limit: 最大消息数，默认 10
        seek_type: 起始位置，BEGINNING（从头）或 LATEST（最新），默认 BEGINNING
        cluster: 集群名称，不指定则使用默认集群
    
    Returns:
        消息列表 JSON
    """
    base_url = _get_base_url(cluster)
    
    params = {
        "keySerde": "String",
        "valueSerde": "String",
        "limit": limit,
        "seekType": seek_type,
        "seekDirection": "FORWARD"
    }
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        # 注意：这是 SSE 接口，需要特殊处理
        resp = await client.get(
            f"{base_url}/topics/{topic_name}/messages",
            params=params,
            headers={"Accept": "text/event-stream"}
        )
        
        messages = []
        consuming_info = {}
        
        # 解析 SSE 响应
        for line in resp.text.split('\n'):
            if line.startswith('data:'):
                try:
                    data = json.loads(line[5:])
                    if data.get("type") == "MESSAGE":
                        msg = data.get("message", {})
                        messages.append({
                            "partition": msg.get("partition"),
                            "offset": msg.get("offset"),
                            "timestamp": msg.get("timestamp"),
                            "key": msg.get("key"),
                            "value": msg.get("content")
                        })
                    elif data.get("type") == "DONE":
                        consuming_info = data.get("consuming", {})
                except Exception:
                    pass
        
        return json.dumps({
            "topic": topic_name,
            "messagesConsumed": consuming_info.get("messagesConsumed", len(messages)),
            "bytesConsumed": consuming_info.get("bytesConsumed", 0),
            "messages": messages
        }, ensure_ascii=False, indent=2)


@mcp.tool()
async def batch_create_topics(topics_config: str, cluster: str = "") -> str:
    """批量创建 Topic。
    
    Args:
        topics_config: Topic 配置列表 JSON，格式:
            [
                {"name": "topic1", "partitions": 3, "replicas": 3, "minISR": 1},
                {"name": "topic2", "partitions": 3, "replicas": 3, "minISR": 2}
            ]
        cluster: 集群名称，不指定则使用默认集群
    
    Returns:
        批量创建结果 JSON
    """
    try:
        configs = json.loads(topics_config)
    except Exception as e:
        return json.dumps({"success": False, "error": f"JSON 解析失败: {e}"}, ensure_ascii=False)
    
    results = []
    for cfg in configs:
        name = cfg.get("name")
        partitions = cfg.get("partitions", 3)
        replicas = cfg.get("replicas", 3)
        min_isr = cfg.get("minISR", 1)
        
        result = await create_topic(
            topic_name=name,
            partitions=partitions,
            replication_factor=replicas,
            min_insync_replicas=min_isr,
            cluster=cluster
        )
        results.append({"topic": name, "result": json.loads(result)})
    
    return json.dumps({
        "success": True,
        "totalCount": len(configs),
        "results": results
    }, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    mcp.run()
