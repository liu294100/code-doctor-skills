# Nacos 2.x MCP Server

基于 Nacos Open API 实现的 MCP (Model Context Protocol) 服务器，使 AI 助手能够直接管理 Nacos 配置中心和服务发现。

## 功能

### 配置管理
- `get_config` - 获取配置内容
- `publish_config` - 发布/更新配置
- `delete_config` - 删除配置
- `list_configs` - 列出命名空间下所有配置
- `get_config_history` - 查询配置历史版本

### 服务发现
- `register_instance` - 注册服务实例
- `deregister_instance` - 注销服务实例
- `query_instances` - 查询服务实例列表
- `query_instance_detail` - 查询实例详情
- `list_services` - 查询服务列表
- `query_service` - 查询服务详情

### 命名空间管理
- `list_namespaces` - 查询所有命名空间
- `get_namespace` - 查询命名空间详情
- `create_namespace` - 创建命名空间
- `delete_namespace` - 删除命名空间

### 集群与系统
- `get_cluster_nodes` - 查询集群节点
- `get_node_health` - 查询节点健康状态
- `get_system_metrics` - 查询系统指标
- `get_system_switches` - 查询系统开关

## 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `NACOS_HOST` | Nacos 服务器地址 | `127.0.0.1` |
| `NACOS_PORT` | Nacos 服务器端口 | `8848` |
| `NACOS_USERNAME` | 认证用户名（可选） | 空 |
| `NACOS_PASSWORD` | 认证密码（可选） | 空 |

## 安装与使用

### 方式一：直接运行

```bash
pip install mcp httpx
python server.py
```

### 方式二：通过 Kiro MCP 配置

在 `.kiro/settings/mcp.json` 中添加：

```json
{
  "mcpServers": {
    "nacos": {
      "command": "python",
      "args": ["D:/dev/code/chief-purchasing-power-center/tools/nacos-mcp-server/server.py"],
      "env": {
        "NACOS_HOST": "your-nacos-host",
        "NACOS_PORT": "8848",
        "NACOS_USERNAME": "nacos",
        "NACOS_PASSWORD": "nacos"
      }
    }
  }
}
```

## 兼容性

- Nacos 2.x（兼容 1.x Open API）
- Python 3.8+
- MCP SDK 1.0+
