"""
Nacos 2.x MCP Server - 单 Tool 设计，类似 execute_sql 的思路

通过一个 execute_nacos_api tool 统一调用 Nacos Open API。
使用方式: pip install mcp httpx && python server.py
"""
import os
import json
from typing import Optional

import httpx
from mcp.server.fastmcp import FastMCP

NACOS_HOST = os.environ.get("NACOS_HOST", "127.0.0.1")
NACOS_PORT = os.environ.get("NACOS_PORT", "8848")
NACOS_USERNAME = os.environ.get("NACOS_USERNAME", "")
NACOS_PASSWORD = os.environ.get("NACOS_PASSWORD", "")
BASE_URL = f"http://{NACOS_HOST}:{NACOS_PORT}"

mcp = FastMCP("nacos2")


async def _get_token() -> Optional[str]:
    if not NACOS_USERNAME or not NACOS_PASSWORD:
        return None
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{BASE_URL}/nacos/v1/auth/login",
            data={"username": NACOS_USERNAME, "password": NACOS_PASSWORD}
        )
        if resp.status_code == 200:
            return resp.json().get("accessToken")
    return None


@mcp.tool()
async def execute_nacos_api(method: str, path: str, params: str = "", body: str = "") -> str:
    """执行 Nacos Open API 请求。

    通过 HTTP 方法 + 路径 + 参数直接调用 Nacos 2.x REST API。
    自动处理认证 Token。

    Args:
        method: HTTP 方法，如 GET、POST、PUT、DELETE
        path: API 路径，如 /nacos/v2/cs/config
        params: URL 查询参数，JSON 格式字符串，如 {"dataId":"app.yaml","group":"DEFAULT_GROUP"}
        body: 请求体（POST/PUT 时使用），JSON 格式字符串，作为 form-urlencoded 发送

    常用 API 路径参考：
    - 配置管理:
      GET    /nacos/v2/cs/config              获取配置 (params: dataId, group, namespaceId)
      POST   /nacos/v2/cs/config              发布配置 (body: dataId, group, namespaceId, content, type)
      DELETE /nacos/v2/cs/config              删除配置 (params: dataId, group, namespaceId)
      GET    /nacos/v2/cs/history/configs     列出配置 (params: namespaceId)
      GET    /nacos/v2/cs/history/list        配置历史 (params: dataId, group, namespaceId, pageNo, pageSize)
    - 服务发现:
      POST   /nacos/v2/ns/instance            注册实例 (body: serviceName, ip, port, ...)
      DELETE /nacos/v2/ns/instance            注销实例 (body: serviceName, ip, port, ...)
      GET    /nacos/v2/ns/instance            实例详情 (params: serviceName, ip, port, ...)
      GET    /nacos/v2/ns/instance/list       实例列表 (params: serviceName, namespaceId, ...)
      GET    /nacos/v2/ns/service/list        服务列表 (params: namespaceId, groupName, pageNo, pageSize)
      GET    /nacos/v2/ns/service             服务详情 (params: serviceName, namespaceId, groupName)
    - 命名空间:
      GET    /nacos/v2/console/namespace/list 命名空间列表
      GET    /nacos/v2/console/namespace      命名空间详情 (params: namespaceId)
      POST   /nacos/v2/console/namespace      创建命名空间 (body: namespaceId, namespaceName, namespaceDesc)
      DELETE /nacos/v2/console/namespace      删除命名空间 (params: namespaceId)
    - 集群:
      GET    /nacos/v2/core/cluster/node/list       集群节点列表
      GET    /nacos/v2/core/cluster/node/self/health 节点健康状态
      GET    /nacos/v2/ns/operator/metrics          系统指标 (params: onlyStatus=false)
      GET    /nacos/v2/ns/operator/switches         系统开关
    """
    token = await _get_token()
    query_params = json.loads(params) if params else {}
    form_data = json.loads(body) if body else None
    if token:
        query_params["accessToken"] = token

    async with httpx.AsyncClient(timeout=30.0) as client:
        m = method.upper()
        url = f"{BASE_URL}{path}"
        if m == "GET":
            resp = await client.get(url, params=query_params)
        elif m == "POST":
            resp = await client.post(url, params=query_params, data=form_data)
        elif m == "PUT":
            resp = await client.put(url, params=query_params, data=form_data)
        elif m == "DELETE":
            resp = await client.delete(url, params=query_params)
        else:
            return json.dumps({"error": f"不支持的方法: {m}"}, ensure_ascii=False)

        try:
            return json.dumps(resp.json(), ensure_ascii=False, indent=2)
        except Exception:
            return json.dumps({"status_code": resp.status_code, "text": resp.text}, ensure_ascii=False)


if __name__ == "__main__":
    mcp.run()
