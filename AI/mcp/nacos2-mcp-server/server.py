"""
Nacos 2.x MCP Server - 基于 Nacos Open API 实现的 MCP 服务器

支持功能：
- 配置管理（获取/发布/删除配置）
- 服务发现（注册/注销/查询实例）
- 命名空间管理
- 集群信息查询

使用方式：
  pip install mcp httpx
  python server.py
"""

import os
import json
import logging
from typing import Optional

import httpx
from mcp.server.fastmcp import FastMCP

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("nacos-mcp")

# 从环境变量读取 Nacos 配置
NACOS_HOST = os.environ.get("NACOS_HOST", "127.0.0.1")
NACOS_PORT = os.environ.get("NACOS_PORT", "8848")
NACOS_USERNAME = os.environ.get("NACOS_USERNAME", "")
NACOS_PASSWORD = os.environ.get("NACOS_PASSWORD", "")

BASE_URL = f"http://{NACOS_HOST}:{NACOS_PORT}"

# 创建 MCP Server
mcp = FastMCP("nacos-mcp-server")


async def _get_token() -> Optional[str]:
    """获取 Nacos 认证 Token（如果配置了用户名密码）"""
    if not NACOS_USERNAME or not NACOS_PASSWORD:
        return None
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{BASE_URL}/nacos/v1/auth/login",
            data={"username": NACOS_USERNAME, "password": NACOS_PASSWORD}
        )
        if resp.status_code == 200:
            data = resp.json()
            return data.get("accessToken")
    return None


async def _request(method: str, path: str, params: dict = None, data: dict = None) -> dict:
    """统一请求封装，自动处理认证"""
    token = await _get_token()
    headers = {}
    if params is None:
        params = {}
    if token:
        params["accessToken"] = token

    async with httpx.AsyncClient(timeout=30.0) as client:
        if method.upper() == "GET":
            resp = await client.get(f"{BASE_URL}{path}", params=params, headers=headers)
        elif method.upper() == "POST":
            resp = await client.post(f"{BASE_URL}{path}", params=params, data=data, headers=headers)
        elif method.upper() == "PUT":
            resp = await client.put(f"{BASE_URL}{path}", params=params, data=data, headers=headers)
        elif method.upper() == "DELETE":
            resp = await client.delete(f"{BASE_URL}{path}", params=params, headers=headers)
        else:
            return {"error": f"不支持的 HTTP 方法: {method}"}

        try:
            return resp.json()
        except Exception:
            return {"status_code": resp.status_code, "text": resp.text}


# ==================== 配置管理 ====================

@mcp.tool()
async def get_config(data_id: str, group: str = "DEFAULT_GROUP", namespace_id: str = "") -> str:
    """获取 Nacos 配置内容

    Args:
        data_id: 配置的 dataId
        group: 配置分组，默认 DEFAULT_GROUP
        namespace_id: 命名空间ID，默认为 public（空字符串）
    """
    result = await _request("GET", "/nacos/v2/cs/config", params={
        "dataId": data_id,
        "group": group,
        "namespaceId": namespace_id
    })
    return json.dumps(result, ensure_ascii=False, indent=2)


@mcp.tool()
async def publish_config(data_id: str, content: str, group: str = "DEFAULT_GROUP",
                         namespace_id: str = "", config_type: str = "") -> str:
    """发布/更新 Nacos 配置

    Args:
        data_id: 配置的 dataId
        content: 配置内容
        group: 配置分组，默认 DEFAULT_GROUP
        namespace_id: 命名空间ID，默认为 public
        config_type: 配置类型（如 yaml, json, properties 等）
    """
    form_data = {
        "dataId": data_id,
        "group": group,
        "namespaceId": namespace_id,
        "content": content
    }
    if config_type:
        form_data["type"] = config_type
    result = await _request("POST", "/nacos/v2/cs/config", data=form_data)
    return json.dumps(result, ensure_ascii=False, indent=2)


@mcp.tool()
async def delete_config(data_id: str, group: str = "DEFAULT_GROUP", namespace_id: str = "") -> str:
    """删除 Nacos 配置

    Args:
        data_id: 配置的 dataId
        group: 配置分组，默认 DEFAULT_GROUP
        namespace_id: 命名空间ID，默认为 public
    """
    result = await _request("DELETE", "/nacos/v2/cs/config", params={
        "dataId": data_id,
        "group": group,
        "namespaceId": namespace_id
    })
    return json.dumps(result, ensure_ascii=False, indent=2)


@mcp.tool()
async def list_configs(namespace_id: str = "") -> str:
    """查询指定命名空间下的所有配置列表

    Args:
        namespace_id: 命名空间ID，默认为 public（空字符串）
    """
    result = await _request("GET", "/nacos/v2/cs/history/configs", params={
        "namespaceId": namespace_id
    })
    return json.dumps(result, ensure_ascii=False, indent=2)


@mcp.tool()
async def get_config_history(data_id: str, group: str = "DEFAULT_GROUP",
                             namespace_id: str = "", page_no: int = 1,
                             page_size: int = 20) -> str:
    """查询配置的历史版本列表

    Args:
        data_id: 配置的 dataId
        group: 配置分组
        namespace_id: 命名空间ID
        page_no: 当前页码，默认 1
        page_size: 每页条数，默认 20
    """
    result = await _request("GET", "/nacos/v2/cs/history/list", params={
        "dataId": data_id,
        "group": group,
        "namespaceId": namespace_id,
        "pageNo": page_no,
        "pageSize": page_size
    })
    return json.dumps(result, ensure_ascii=False, indent=2)


# ==================== 服务发现 ====================

@mcp.tool()
async def register_instance(service_name: str, ip: str, port: int,
                            namespace_id: str = "", group_name: str = "DEFAULT_GROUP",
                            weight: float = 1.0, enabled: bool = True,
                            ephemeral: bool = True, metadata: str = "") -> str:
    """注册服务实例

    Args:
        service_name: 服务名称
        ip: 实例 IP 地址
        port: 实例端口号
        namespace_id: 命名空间ID
        group_name: 分组名称，默认 DEFAULT_GROUP
        weight: 实例权重，默认 1.0
        enabled: 是否启用，默认 true
        ephemeral: 是否临时实例，默认 true
        metadata: 实例元数据，JSON 格式字符串
    """
    form_data = {
        "serviceName": service_name,
        "ip": ip,
        "port": str(port),
        "namespaceId": namespace_id,
        "groupName": group_name,
        "weight": str(weight),
        "enabled": str(enabled).lower(),
        "ephemeral": str(ephemeral).lower()
    }
    if metadata:
        form_data["metadata"] = metadata
    result = await _request("POST", "/nacos/v2/ns/instance", data=form_data)
    return json.dumps(result, ensure_ascii=False, indent=2)


@mcp.tool()
async def deregister_instance(service_name: str, ip: str, port: int,
                              namespace_id: str = "", group_name: str = "DEFAULT_GROUP",
                              ephemeral: bool = True) -> str:
    """注销服务实例

    Args:
        service_name: 服务名称
        ip: 实例 IP 地址
        port: 实例端口号
        namespace_id: 命名空间ID
        group_name: 分组名称
        ephemeral: 是否临时实例
    """
    form_data = {
        "serviceName": service_name,
        "ip": ip,
        "port": str(port),
        "namespaceId": namespace_id,
        "groupName": group_name,
        "ephemeral": str(ephemeral).lower()
    }
    result = await _request("DELETE", "/nacos/v2/ns/instance", data=form_data)
    return json.dumps(result, ensure_ascii=False, indent=2)


@mcp.tool()
async def query_instances(service_name: str, namespace_id: str = "",
                          group_name: str = "", cluster_name: str = "",
                          healthy_only: bool = False) -> str:
    """查询服务下的实例列表

    Args:
        service_name: 服务名称
        namespace_id: 命名空间ID
        group_name: 分组名称
        cluster_name: 集群名称
        healthy_only: 是否只返回健康实例，默认 false
    """
    params = {
        "serviceName": service_name,
        "namespaceId": namespace_id,
        "groupName": group_name,
        "clusterName": cluster_name,
        "healthyOnly": str(healthy_only).lower()
    }
    result = await _request("GET", "/nacos/v2/ns/instance/list", params=params)
    return json.dumps(result, ensure_ascii=False, indent=2)


@mcp.tool()
async def query_instance_detail(service_name: str, ip: str, port: int,
                                namespace_id: str = "",
                                group_name: str = "DEFAULT_GROUP") -> str:
    """查询单个实例详情

    Args:
        service_name: 服务名称
        ip: 实例 IP
        port: 实例端口
        namespace_id: 命名空间ID
        group_name: 分组名称
    """
    params = {
        "serviceName": service_name,
        "ip": ip,
        "port": str(port),
        "namespaceId": namespace_id,
        "groupName": group_name
    }
    result = await _request("GET", "/nacos/v2/ns/instance", params=params)
    return json.dumps(result, ensure_ascii=False, indent=2)


@mcp.tool()
async def list_services(namespace_id: str = "", group_name: str = "",
                        page_no: int = 1, page_size: int = 20) -> str:
    """查询服务列表

    Args:
        namespace_id: 命名空间ID
        group_name: 分组名称
        page_no: 当前页码，默认 1
        page_size: 每页条数，默认 20
    """
    params = {
        "namespaceId": namespace_id,
        "groupName": group_name,
        "pageNo": str(page_no),
        "pageSize": str(page_size)
    }
    result = await _request("GET", "/nacos/v2/ns/service/list", params=params)
    return json.dumps(result, ensure_ascii=False, indent=2)


@mcp.tool()
async def query_service(service_name: str, namespace_id: str = "",
                        group_name: str = "") -> str:
    """查询服务详情

    Args:
        service_name: 服务名称
        namespace_id: 命名空间ID
        group_name: 分组名称
    """
    params = {
        "serviceName": service_name,
        "namespaceId": namespace_id,
        "groupName": group_name
    }
    result = await _request("GET", "/nacos/v2/ns/service", params=params)
    return json.dumps(result, ensure_ascii=False, indent=2)


# ==================== 命名空间管理 ====================

@mcp.tool()
async def list_namespaces() -> str:
    """查询所有命名空间"""
    result = await _request("GET", "/nacos/v2/console/namespace/list")
    return json.dumps(result, ensure_ascii=False, indent=2)


@mcp.tool()
async def get_namespace(namespace_id: str) -> str:
    """查询指定命名空间详情

    Args:
        namespace_id: 命名空间ID
    """
    result = await _request("GET", "/nacos/v2/console/namespace", params={
        "namespaceId": namespace_id
    })
    return json.dumps(result, ensure_ascii=False, indent=2)


@mcp.tool()
async def create_namespace(namespace_id: str, namespace_name: str,
                           namespace_desc: str = "") -> str:
    """创建命名空间

    Args:
        namespace_id: 命名空间ID
        namespace_name: 命名空间名称
        namespace_desc: 命名空间描述
    """
    form_data = {
        "namespaceId": namespace_id,
        "namespaceName": namespace_name
    }
    if namespace_desc:
        form_data["namespaceDesc"] = namespace_desc
    result = await _request("POST", "/nacos/v2/console/namespace", data=form_data)
    return json.dumps(result, ensure_ascii=False, indent=2)


@mcp.tool()
async def delete_namespace(namespace_id: str) -> str:
    """删除命名空间

    Args:
        namespace_id: 命名空间ID
    """
    result = await _request("DELETE", "/nacos/v2/console/namespace", params={
        "namespaceId": namespace_id
    })
    return json.dumps(result, ensure_ascii=False, indent=2)


# ==================== 集群与系统 ====================

@mcp.tool()
async def get_cluster_nodes() -> str:
    """查询集群节点列表"""
    result = await _request("GET", "/nacos/v2/core/cluster/node/list")
    return json.dumps(result, ensure_ascii=False, indent=2)


@mcp.tool()
async def get_node_health() -> str:
    """查询当前节点健康状态"""
    result = await _request("GET", "/nacos/v2/core/cluster/node/self/health")
    return json.dumps(result, ensure_ascii=False, indent=2)


@mcp.tool()
async def get_system_metrics() -> str:
    """查询系统指标（服务数、实例数、订阅数等）"""
    result = await _request("GET", "/nacos/v2/ns/operator/metrics", params={
        "onlyStatus": "false"
    })
    return json.dumps(result, ensure_ascii=False, indent=2)


@mcp.tool()
async def get_system_switches() -> str:
    """查询系统开关配置"""
    result = await _request("GET", "/nacos/v2/ns/operator/switches")
    return json.dumps(result, ensure_ascii=False, indent=2)


# ==================== 启动入口 ====================

if __name__ == "__main__":
    mcp.run()
