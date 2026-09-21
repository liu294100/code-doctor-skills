"""
Nacos 3.x MCP Server - 支持自动登录和 v3 API

专为 Nacos 3.x 版本设计，提供命名空间、服务、配置的查询功能。
自动处理认证 Token，无需手动配置。

使用方式: pip install mcp httpx && python server.py

环境变量:
  NACOS_HOST: Nacos 服务器地址，默认 127.0.0.1
  NACOS_PORT: Nacos 服务器端口，默认 8080 (注意: Nacos 3.x Console 默认端口是 8080)
  NACOS_USERNAME: 用户名
  NACOS_PASSWORD: 密码
"""
import os
import json
import time
from typing import Optional, Any

import httpx
from mcp.server.fastmcp import FastMCP

# 配置
NACOS_HOST = os.environ.get("NACOS_HOST", "127.0.0.1")
NACOS_PORT = os.environ.get("NACOS_PORT", "8080")
NACOS_USERNAME = os.environ.get("NACOS_USERNAME", "")
NACOS_PASSWORD = os.environ.get("NACOS_PASSWORD", "")
BASE_URL = f"http://{NACOS_HOST}:{NACOS_PORT}"

# Token 缓存
_token_cache = {
    "token": None,
    "expire_time": 0
}

mcp = FastMCP("nacos3")


async def _get_token() -> Optional[str]:
    """获取 Nacos 认证 Token，支持缓存和自动刷新"""
    if not NACOS_USERNAME or not NACOS_PASSWORD:
        return None
    
    # 检查缓存的 token 是否有效（预留 5 分钟缓冲）
    if _token_cache["token"] and time.time() < _token_cache["expire_time"] - 300:
        return _token_cache["token"]
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Nacos 3.x 使用 v3 登录 API，注意要用 form-urlencoded 格式
        try:
            resp = await client.post(
                f"{BASE_URL}/v3/auth/user/login",
                data={"username": NACOS_USERNAME, "password": NACOS_PASSWORD}
            )
            if resp.status_code == 200:
                data = resp.json()
                token = data.get("accessToken")
                ttl = data.get("tokenTtl", 18000)
                _token_cache["token"] = token
                _token_cache["expire_time"] = time.time() + ttl
                return token
        except Exception as e:
            print(f"Login failed: {e}")
    
    return None


async def _request(method: str, path: str, params: dict = None, body: dict = None) -> dict:
    """发送 Nacos API 请求"""
    token = await _get_token()
    query_params = params or {}
    if token:
        query_params["accessToken"] = token
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        url = f"{BASE_URL}{path}"
        m = method.upper()
        
        if m == "GET":
            resp = await client.get(url, params=query_params)
        elif m == "POST":
            resp = await client.post(url, params=query_params, json=body)
        elif m == "PUT":
            resp = await client.put(url, params=query_params, json=body)
        elif m == "DELETE":
            resp = await client.delete(url, params=query_params)
        else:
            return {"error": f"不支持的方法: {m}"}
        
        try:
            return resp.json()
        except Exception:
            return {"status_code": resp.status_code, "text": resp.text}


def _format_result(data: Any) -> str:
    """格式化返回结果"""
    return json.dumps(data, ensure_ascii=False, indent=2)


# ==================== 命名空间相关 ====================

@mcp.tool()
async def list_namespaces() -> str:
    """列出 Nacos 集群中的所有命名空间。
    
    Returns:
        命名空间列表，包含 namespace、namespaceShowName、namespaceDesc、configCount 等信息
    """
    result = await _request("GET", "/v3/console/core/namespace/list")
    return _format_result(result)


# ==================== 服务发现相关 ====================

@mcp.tool()
async def list_services(
    namespace_id: str = "public",
    group_name: str = "",
    service_name: str = "",
    page_no: int = 1,
    page_size: int = 100,
    ignore_empty_service: bool = True,
    with_instances: bool = False
) -> str:
    """列出指定命名空间下的服务列表。
    
    Args:
        namespace_id: 命名空间 ID，默认 public
        group_name: 服务组名模式匹配，默认空表示所有组
        service_name: 服务名模式匹配，默认空表示所有服务
        page_no: 页码，默认 1
        page_size: 每页大小，默认 100
        ignore_empty_service: 是否忽略空服务，默认 True
        with_instances: 是否包含实例信息，默认 False（建议保持 False，性能更好）
    
    Returns:
        服务列表
    """
    params = {
        "namespaceId": namespace_id,
        "pageNo": page_no,
        "pageSize": page_size,
        "ignoreEmptyService": str(ignore_empty_service).lower(),
        "withInstances": str(with_instances).lower()
    }
    if group_name:
        params["groupNameParam"] = group_name
    if service_name:
        params["serviceNameParam"] = service_name
    
    result = await _request("GET", "/v3/console/ns/service/list", params)
    return _format_result(result)


@mcp.tool()
async def get_service(
    service_name: str,
    namespace_id: str = "public",
    group_name: str = "DEFAULT_GROUP"
) -> str:
    """获取指定服务的详细信息，包括元数据和集群信息。
    
    Args:
        service_name: 服务名（必填）
        namespace_id: 命名空间 ID，默认 public
        group_name: 服务组名，默认 DEFAULT_GROUP
    
    Returns:
        服务详细信息
    """
    params = {
        "namespaceId": namespace_id,
        "groupName": group_name,
        "serviceName": service_name
    }
    result = await _request("GET", "/v3/console/ns/service", params)
    return _format_result(result)


@mcp.tool()
async def list_service_instances(
    service_name: str,
    namespace_id: str = "public",
    group_name: str = "DEFAULT_GROUP",
    cluster_name: str = ""
) -> str:
    """列出指定服务的实例列表。
    
    Args:
        service_name: 服务名（必填）
        namespace_id: 命名空间 ID，默认 public
        group_name: 服务组名，默认 DEFAULT_GROUP
        cluster_name: 集群名，默认空表示所有集群
    
    Returns:
        实例列表
    """
    params = {
        "namespaceId": namespace_id,
        "groupName": group_name,
        "serviceName": service_name
    }
    if cluster_name:
        params["clusterName"] = cluster_name
    
    result = await _request("GET", "/v3/console/ns/service/instance/list", params)
    return _format_result(result)


@mcp.tool()
async def list_service_subscribers(
    service_name: str,
    namespace_id: str = "public",
    group_name: str = "DEFAULT_GROUP",
    page_no: int = 1,
    page_size: int = 100,
    aggregation: bool = True
) -> str:
    """列出订阅指定服务的客户端列表。
    
    Args:
        service_name: 服务名（必填）
        namespace_id: 命名空间 ID，默认 public
        group_name: 服务组名，默认 DEFAULT_GROUP
        page_no: 页码，默认 1
        page_size: 每页大小，默认 100
        aggregation: 是否聚合整个集群的结果，默认 True
    
    Returns:
        订阅者列表
    """
    params = {
        "namespaceId": namespace_id,
        "groupName": group_name,
        "serviceName": service_name,
        "pageNo": page_no,
        "pageSize": page_size,
        "aggregation": str(aggregation).lower()
    }
    result = await _request("GET", "/v3/console/ns/service/subscriber/list", params)
    return _format_result(result)


# ==================== 配置中心相关 ====================

@mcp.tool()
async def list_configs(
    namespace_id: str = "public",
    group_name: str = "",
    data_id: str = "",
    config_type: str = "",
    config_tags: str = "",
    app_name: str = "",
    search: str = "blur",
    page_no: int = 1,
    page_size: int = 100
) -> str:
    """列出指定命名空间下的配置列表。
    
    Args:
        namespace_id: 命名空间 ID，默认 public
        group_name: 配置组名模式匹配，默认空表示所有组
        data_id: 配置 dataId 模式匹配，默认空表示所有
        config_type: 配置类型（如 yaml、json、properties），默认空表示所有
        config_tags: 配置标签，默认空表示所有
        app_name: 应用名，默认空表示所有
        search: 搜索方式，blur（模糊）或 accurate（精确），默认 blur
        page_no: 页码，默认 1
        page_size: 每页大小，默认 100
    
    Returns:
        配置列表
    """
    params = {
        "namespaceId": namespace_id,
        "pageNo": page_no,
        "pageSize": page_size,
        "search": search
    }
    if group_name:
        params["groupName"] = group_name
    if data_id:
        params["dataId"] = data_id
    if config_type:
        params["type"] = config_type
    if config_tags:
        params["configTags"] = config_tags
    if app_name:
        params["appName"] = app_name
    
    result = await _request("GET", "/v3/console/cs/config/list", params)
    return _format_result(result)


@mcp.tool()
async def get_config(
    data_id: str,
    group_name: str,
    namespace_id: str = "public"
) -> str:
    """获取指定配置的详细内容。
    
    Args:
        data_id: 配置 ID（必填）
        group_name: 配置组名（必填）
        namespace_id: 命名空间 ID，默认 public
    
    Returns:
        配置详情，包含 content、type、md5 等信息
    """
    params = {
        "namespaceId": namespace_id,
        "groupName": group_name,
        "dataId": data_id
    }
    result = await _request("GET", "/v3/console/cs/config", params)
    return _format_result(result)


@mcp.tool()
async def list_config_history(
    data_id: str,
    group_name: str,
    namespace_id: str = "public",
    page_no: int = 1,
    page_size: int = 100
) -> str:
    """获取配置的修改历史记录列表。
    
    Args:
        data_id: 配置 ID（必填）
        group_name: 配置组名（必填）
        namespace_id: 命名空间 ID，默认 public
        page_no: 页码，默认 1
        page_size: 每页大小，默认 100
    
    Returns:
        配置历史列表
    """
    params = {
        "namespaceId": namespace_id,
        "groupName": group_name,
        "dataId": data_id,
        "pageNo": page_no,
        "pageSize": page_size
    }
    result = await _request("GET", "/v3/console/cs/config/history/list", params)
    return _format_result(result)


@mcp.tool()
async def get_config_history(
    data_id: str,
    group_name: str,
    nid: int,
    namespace_id: str = "public"
) -> str:
    """获取配置的某个历史版本详情。
    
    Args:
        data_id: 配置 ID（必填）
        group_name: 配置组名（必填）
        nid: 历史记录 ID（必填，从 list_config_history 获取）
        namespace_id: 命名空间 ID，默认 public
    
    Returns:
        历史版本的配置详情
    """
    params = {
        "namespaceId": namespace_id,
        "groupName": group_name,
        "dataId": data_id,
        "nid": nid
    }
    result = await _request("GET", "/v3/console/cs/config/history", params)
    return _format_result(result)


@mcp.tool()
async def list_config_listeners(
    data_id: str,
    group_name: str,
    namespace_id: str = "public",
    aggregation: bool = True
) -> str:
    """获取订阅指定配置的监听者列表。
    
    Args:
        data_id: 配置 ID（必填）
        group_name: 配置组名（必填）
        namespace_id: 命名空间 ID，默认 public
        aggregation: 是否聚合整个集群的结果，默认 True
    
    Returns:
        监听者列表
    """
    params = {
        "namespaceId": namespace_id,
        "groupName": group_name,
        "dataId": data_id,
        "aggregation": str(aggregation).lower()
    }
    result = await _request("GET", "/v3/console/cs/config/listener/list", params)
    return _format_result(result)


# ==================== 集群管理相关 ====================

@mcp.tool()
async def get_server_state() -> str:
    """获取 Nacos 服务器状态信息。
    
    Returns:
        服务器状态，包含版本、启动模式、数据源等信息
    """
    result = await _request("GET", "/v3/console/server/state")
    return _format_result(result)


@mcp.tool()
async def list_cluster_nodes() -> str:
    """列出 Nacos 集群中的所有节点。
    
    Returns:
        集群节点列表
    """
    result = await _request("GET", "/v3/core/cluster/node/list")
    return _format_result(result)


# ==================== 通用 API 调用 ====================

@mcp.tool()
async def execute_nacos_api(method: str, path: str, params: str = "", body: str = "") -> str:
    """执行任意 Nacos v3 API 请求（高级用法）。
    
    通过 HTTP 方法 + 路径 + 参数直接调用 Nacos REST API。
    自动处理认证 Token。
    
    Args:
        method: HTTP 方法，如 GET、POST、PUT、DELETE
        path: API 路径，如 /v3/console/cs/config
        params: URL 查询参数，JSON 格式字符串
        body: 请求体（POST/PUT 时使用），JSON 格式字符串
    
    常用 v3 API 路径参考：
    - 命名空间: GET /v3/console/core/namespace/list
    - 服务列表: GET /v3/console/ns/service/list
    - 服务详情: GET /v3/console/ns/service
    - 实例列表: GET /v3/console/ns/service/instance/list
    - 配置列表: GET /v3/console/cs/config/list
    - 配置详情: GET /v3/console/cs/config
    - 配置历史: GET /v3/console/cs/config/history/list
    - 服务器状态: GET /v3/console/server/state
    
    Returns:
        API 响应结果
    """
    query_params = json.loads(params) if params else {}
    body_data = json.loads(body) if body else None
    result = await _request(method.upper(), path, query_params, body_data)
    return _format_result(result)


if __name__ == "__main__":
    mcp.run()
