# Kafka UI MCP Server

通过 Kafka UI REST API 管理 Kafka Topic 和消息的 MCP Server。

## 功能

- **Topic 管理**: 创建、查询、删除 Topic
- **消息管理**: 发送消息、消费消息
- **批量操作**: 批量创建 Topic
- **集群信息**: 查询集群列表

## 安装

```bash
pip install mcp httpx
```

## 配置

### 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| KAFKA_UI_URL | Kafka UI 地址 | http://localhost:8080 |
| KAFKA_UI_CLUSTER | 默认集群名称 | kafka-msk-test |

### Kiro MCP 配置

编辑 `.kiro/settings/mcp.json`：

```json
{
  "mcpServers": {
    "kafka-ui": {
      "command": "python",
      "args": ["D:/dev/AI/chief-trader-z-ai-tools/mcp/kafka-ui-mcp-server/server.py"],
      "env": {
        "KAFKA_UI_URL": "https://kafka-ui.test.stx365.com",
        "KAFKA_UI_CLUSTER": "kafka-msk-test"
      }
    }
  }
}
```

## 可用工具

### 1. list_clusters
列出所有 Kafka 集群。

### 2. list_topics
列出 Topic 列表。

**参数**:
- `cluster`: 集群名称（可选）
- `page`: 页码，默认 1
- `per_page`: 每页数量，默认 25
- `show_internal`: 是否显示内部 Topic，默认 True
- `search`: 搜索关键字（可选）

### 3. get_topic
获取 Topic 详情。

**参数**:
- `topic_name`: Topic 名称
- `cluster`: 集群名称（可选）

### 4. get_topic_config
获取 Topic 配置（min.insync.replicas、cleanup.policy 等）。

**参数**:
- `topic_name`: Topic 名称
- `cluster`: 集群名称（可选）

### 5. create_topic
创建 Topic。

**参数**:
- `topic_name`: Topic 名称
- `partitions`: 分区数，默认 3
- `replication_factor`: 副本因子，默认 3
- `min_insync_replicas`: 最小同步副本数，默认 1
- `cleanup_policy`: 清理策略（delete/compact），默认 delete
- `cluster`: 集群名称（可选）

### 6. delete_topic
删除 Topic。

**参数**:
- `topic_name`: Topic 名称
- `cluster`: 集群名称（可选）

### 7. produce_message
发送消息到 Topic。

**参数**:
- `topic_name`: Topic 名称
- `content`: 消息内容
- `key`: 消息 Key（可选）
- `partition`: 目标分区，-1 表示自动（可选）
- `cluster`: 集群名称（可选）

### 8. consume_messages
消费 Topic 中的消息。

**参数**:
- `topic_name`: Topic 名称
- `limit`: 最大消息数，默认 10
- `seek_type`: 起始位置，BEGINNING 或 LATEST，默认 BEGINNING
- `cluster`: 集群名称（可选）

### 9. batch_create_topics
批量创建 Topic。

**参数**:
- `topics_config`: Topic 配置 JSON 数组
- `cluster`: 集群名称（可选）

**示例**:
```json
[
  {"name": "test-topic-1", "partitions": 3, "replicas": 3, "minISR": 1},
  {"name": "test-topic-2", "partitions": 3, "replicas": 3, "minISR": 2}
]
```

## 使用示例

### 创建 minISR 测试 Topic

```
create_topic topic_name="position-test-minISR-1" partitions=3 replication_factor=3 min_insync_replicas=1
create_topic topic_name="position-test-minISR-2" partitions=3 replication_factor=3 min_insync_replicas=2
create_topic topic_name="position-test-minISR-3" partitions=3 replication_factor=3 min_insync_replicas=3
```

### 批量创建

```
batch_create_topics topics_config='[{"name":"test-1","partitions":3,"replicas":3,"minISR":1},{"name":"test-2","partitions":3,"replicas":3,"minISR":2}]'
```

### 发送测试消息

```
produce_message topic_name="position-test-minISR-1" content='{"test":"message"}' key="test-key-001"
```

### 消费消息

```
consume_messages topic_name="position-test-minISR-1" limit=10
```

## 基于的 API

本 MCP Server 基于 Kafka UI REST API 实现，详见: [Kafka-UI-API接口文档.md](../../chief-trader-position/doc/design/Kafka-UI-API接口文档.md)

## License

MIT
