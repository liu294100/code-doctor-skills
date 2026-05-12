---
name: setup-nacos2-mcp
description: RSetup Nacos MCP Server.
---

# Setup Nacos MCP Server

安装并配置 Nacos 2.x MCP Server，使 AI 助手能够通过 MCP 协议直接管理 Nacos 配置中心和服务发现。

## 触发条件

当用户要求：
- 安装/配置 Nacos MCP
- 连接 Nacos 配置中心
- 设置 Nacos MCP Server

## 安装步骤

### 1. 确认 Python 环境

确保系统已安装 Python 3.8+ 和 pip：

```bash
python --version
pip --version
```

### 2. 安装依赖

```bash
pip install mcp httpx
```

### 3. 收集用户信息

向用户询问以下配置信息：

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| Nacos 地址 | Nacos 服务器 IP 或域名 | `127.0.0.1` |
| Nacos 端口 | Nacos HTTP 端口 | `8848` |
| 用户名 | Nacos 认证用户名（可选） | 空 |
| 密码 | Nacos 认证密码（可选） | 空 |
| 配置级别 | workspace 级别还是 user 全局级别 | workspace |

### 4. 写入 MCP 配置

根据用户选择的级别，写入对应的 `mcp.json` 文件：

- **Workspace 级别**: `.kiro/settings/mcp.json`
- **User 全局级别**: `~/.kiro/settings/mcp.json`

配置模板：

```json
{
  "mcpServers": {
    "nacos": {
      "command": "python",
      "args": ["${SERVER_SCRIPT_PATH}"],
      "env": {
        "NACOS_HOST": "${NACOS_HOST}",
        "NACOS_PORT": "${NACOS_PORT}",
        "NACOS_USERNAME": "${NACOS_USERNAME}",
        "NACOS_PASSWORD": "${NACOS_PASSWORD}"
      },
      "disabled": false,
      "autoApprove": [
        "get_config",
        "list_configs",
        "get_config_history",
        "query_instances",
        "query_instance_detail",
        "list_services",
        "query_service",
        "list_namespaces",
        "get_namespace",
        "get_cluster_nodes",
        "get_node_health",
        "get_system_metrics",
        "get_system_switches"
      ]
    }
  }
}
```

其中 `${SERVER_SCRIPT_PATH}` 为 `tools/nacos-mcp-server/server.py` 的绝对路径。

**注意**：`autoApprove` 中只包含只读操作。写操作（publish_config、delete_config、register_instance、deregister_instance、create_namespace、delete_namespace）需要用户手动确认。

### 5. 验证连接

安装完成后，建议用户测试连接：

```
请帮我查询 Nacos 的命名空间列表
```

如果返回正常数据，说明配置成功。

## MCP Server 源码位置

https://raw.githubusercontent.com/liu294100/code-doctor-skills/refs/heads/main/AI/mcp/nacos2-mcp-server/server.py 可以下载

```
tools/nacos-mcp-server/
├── server.py           # MCP Server 主程序
├── requirements.txt    # Python 依赖
└── README.md           # 使用说明
```

## 支持的 Tools

### 配置管理（Configuration）
- `get_config(data_id, group, namespace_id)` - 获取配置
- `publish_config(data_id, content, group, namespace_id, config_type)` - 发布配置
- `delete_config(data_id, group, namespace_id)` - 删除配置
- `list_configs(namespace_id)` - 列出配置
- `get_config_history(data_id, group, namespace_id, page_no, page_size)` - 配置历史

### 服务发现（Service Discovery）
- `register_instance(service_name, ip, port, ...)` - 注册实例
- `deregister_instance(service_name, ip, port, ...)` - 注销实例
- `query_instances(service_name, namespace_id, ...)` - 查询实例列表
- `query_instance_detail(service_name, ip, port, ...)` - 实例详情
- `list_services(namespace_id, group_name, ...)` - 服务列表
- `query_service(service_name, ...)` - 服务详情

### 命名空间（Namespace）
- `list_namespaces()` - 命名空间列表
- `get_namespace(namespace_id)` - 命名空间详情
- `create_namespace(namespace_id, namespace_name, namespace_desc)` - 创建
- `delete_namespace(namespace_id)` - 删除

### 集群与系统（Cluster & System）
- `get_cluster_nodes()` - 集群节点
- `get_node_health()` - 节点健康
- `get_system_metrics()` - 系统指标
- `get_system_switches()` - 系统开关

## 故障排查

### 连接失败
1. 确认 Nacos 服务已启动且端口可访问
2. 检查防火墙是否放行端口
3. 如果开启了认证，确认用户名密码正确

### Python 依赖问题
```bash
pip install --upgrade mcp httpx
```

### 权限问题
如果 Nacos 开启了鉴权（`nacos.core.auth.enabled=true`），必须配置 `NACOS_USERNAME` 和 `NACOS_PASSWORD`。
