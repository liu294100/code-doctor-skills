# Nacos 3.x MCP Server

专为 Nacos 3.x 版本设计的 MCP Server，提供命名空间、服务发现、配置中心的查询功能。

## 特性

- ✅ 支持 Nacos 3.x v3 API
- ✅ 自动登录和 Token 缓存（无需手动配置 access_token）
- ✅ Token 自动刷新
- ✅ 完整的命名空间、服务、配置查询功能

## 依赖

```bash
pip install mcp httpx
```

## 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| NACOS_HOST | Nacos 服务器地址 | 127.0.0.1 |
| NACOS_PORT | Nacos 服务器端口 | 8080 |
| NACOS_USERNAME | 用户名 | - |
| NACOS_PASSWORD | 密码 | - |

> **注意**: Nacos 3.x 的 Console 默认端口是 **8080**，不是 8848！

## MCP 配置示例

```json
{
  "mcpServers": {
    "nacos3": {
      "command": "python",
      "args": ["D:/dev/AI/chief-trader-z-ai-tools/mcp/nacos3-mcp-server/server.py"],
      "env": {
        "NACOS_HOST": "127.0.0.1",
        "NACOS_PORT": "8080",
        "NACOS_USERNAME": "nacos",
        "NACOS_PASSWORD": "nacos",
        "NO_PROXY": "*",
        "HTTP_PROXY": "",
        "HTTPS_PROXY": ""
      },
      "disabled": false
    }
  }
}
```

## 可用工具

### 命名空间
- `list_namespaces` - 列出所有命名空间

### 服务发现
- `list_services` - 列出服务列表
- `get_service` - 获取服务详情
- `list_service_instances` - 列出服务实例
- `list_service_subscribers` - 列出服务订阅者

### 配置中心
- `list_configs` - 列出配置列表
- `get_config` - 获取配置详情
- `list_config_history` - 获取配置历史
- `get_config_history` - 获取历史版本详情
- `list_config_listeners` - 获取配置监听者

### 集群管理
- `get_server_state` - 获取服务器状态
- `list_cluster_nodes` - 列出集群节点

### 通用
- `execute_nacos_api` - 执行任意 Nacos API（高级用法）

## 使用示例

```
# 列出所有命名空间
list_namespaces

# 列出 test 命名空间下的服务
list_services namespace_id="test"

# 获取配置内容
get_config data_id="application.yml" group_name="DEFAULT_GROUP" namespace_id="test"

# 搜索配置
list_configs namespace_id="test" data_id="trader"
```

## 与官方 MCP Server 的区别

| 特性 | 本项目 | 官方 nacos-mcp-server |
|------|--------|----------------------|
| 认证方式 | 自动登录 + Token 缓存 | 需手动传入 access_token |
| Token 刷新 | 自动 | 手动 |
| API 版本 | v3 | v3 |
| 功能覆盖 | 完整 | 完整 |

## License

Apache 2.0
