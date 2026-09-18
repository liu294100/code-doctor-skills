# Kafka UI API 接口文档

> 基于 Kafka UI (https://kafka-ui.test.xxx.com) 抓取的 REST API 接口

## 基础信息

- **Base URL**: `https://kafka-ui.test.xxx.com/api`
- **Content-Type**: `application/json`
- **集群名称**: `kafka-msk-test`（测试环境）

---

## 1. Topic 管理

### 1.1 创建 Topic

**请求**
```http
POST /api/clusters/{clusterName}/topics
Content-Type: application/json
```

**路径参数**
| 参数 | 说明 |
|------|------|
| clusterName | Kafka 集群名称，如 `kafka-msk-test` |

**请求体**
```json
{
  "name": "position-test-minISR-1",
  "partitions": 3,
  "replicationFactor": "3",
  "configs": {
    "cleanup.policy": "delete",
    "min.insync.replicas": "1"
  }
}
```

**字段说明**
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| name | string | 是 | Topic 名称 |
| partitions | int | 是 | 分区数 |
| replicationFactor | string | 是 | 副本因子 |
| configs | object | 否 | Topic 配置 |
| configs.cleanup.policy | string | 否 | 清理策略：delete / compact |
| configs.min.insync.replicas | string | 否 | 最小同步副本数 |

**响应示例**
```json
{
  "name": "position-test-minISR-1",
  "internal": false,
  "partitionCount": 3,
  "replicationFactor": 3,
  "replicas": 9,
  "inSyncReplicas": 9,
  "segmentSize": 0,
  "segmentCount": 0,
  "underReplicatedPartitions": 0,
  "cleanUpPolicy": "DELETE",
  "partitions": [
    {
      "partition": 0,
      "leader": 2,
      "replicas": [
        {"broker": 2, "leader": true, "inSync": true},
        {"broker": 1, "leader": false, "inSync": true},
        {"broker": 3, "leader": false, "inSync": true}
      ],
      "offsetMax": 0,
      "offsetMin": 0
    }
  ]
}
```

**cURL 示例**
```bash
curl -X POST 'https://kafka-ui.test.xxx.com/api/clusters/kafka-msk-test/topics' \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "position-test-minISR-1",
    "partitions": 3,
    "replicationFactor": "3",
    "configs": {
      "cleanup.policy": "delete",
      "min.insync.replicas": "1"
    }
  }'
```

---

### 1.2 查询 Topic 列表

**请求**
```http
GET /api/clusters/{clusterName}/topics?page=1&perPage=25&showInternal=true&search={keyword}
```

**查询参数**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| page | int | 否 | 页码，默认 1 |
| perPage | int | 否 | 每页数量，默认 25 |
| showInternal | boolean | 否 | 是否显示内部 Topic |
| search | string | 否 | 搜索关键字 |

**cURL 示例**
```bash
curl 'https://kafka-ui.test.xxx.com/api/clusters/kafka-msk-test/topics?page=1&perPage=25&showInternal=true'
```

---

### 1.3 查询 Topic 详情

**请求**
```http
GET /api/clusters/{clusterName}/topics/{topicName}
```

**响应示例**
```json
{
  "name": "position-test-minISR-1",
  "internal": false,
  "partitions": [...],
  "partitionCount": 3,
  "replicationFactor": 3,
  "replicas": 9,
  "inSyncReplicas": 9,
  "segmentSize": 0,
  "segmentCount": 0,
  "underReplicatedPartitions": 0,
  "cleanUpPolicy": "DELETE",
  "keySerde": null,
  "valueSerde": null
}
```

**cURL 示例**
```bash
curl 'https://kafka-ui.test.xxx.com/api/clusters/kafka-msk-test/topics/position-test-minISR-1'
```

---

### 1.4 查询 Topic 配置

**请求**
```http
GET /api/clusters/{clusterName}/topics/{topicName}/config
```

**响应示例**（部分）
```json
[
  {
    "name": "min.insync.replicas",
    "value": "2",
    "defaultValue": "1",
    "source": "DYNAMIC_TOPIC_CONFIG",
    "isSensitive": false,
    "isReadOnly": false,
    "synonyms": [...],
    "doc": "When a producer sets acks to \"all\"..."
  },
  {
    "name": "cleanup.policy",
    "value": "delete",
    "defaultValue": "delete",
    "source": "DYNAMIC_TOPIC_CONFIG",
    ...
  }
]
```

**cURL 示例**
```bash
curl 'https://kafka-ui.test.xxx.com/api/clusters/kafka-msk-test/topics/position-test-minISR-1/config'
```

---

### 1.5 删除 Topic

**请求**
```http
DELETE /api/clusters/{clusterName}/topics/{topicName}
```

**响应**
- 成功：HTTP 200，响应体为空

**cURL 示例**
```bash
curl -X DELETE 'https://kafka-ui.test.xxx.com/api/clusters/kafka-msk-test/topics/position-test-api-capture'
```

---

## 2. 消息管理

### 2.1 发送消息 (Produce Message)

**请求**
```http
POST /api/clusters/{clusterName}/topics/{topicName}/messages
Content-Type: application/json
```

**请求体**
```json
{
  "partition": 0,
  "key": "test-key-001",
  "content": "{\"message\":\"test message\",\"timestamp\":\"2026-09-18T15:35:00\"}",
  "keySerde": "String",
  "valueSerde": "String"
}
```

**字段说明**
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| partition | int | 否 | 目标分区，不指定则随机 |
| key | string | 否 | 消息 Key |
| content | string | 是 | 消息内容 |
| keySerde | string | 否 | Key 序列化方式，默认 String |
| valueSerde | string | 否 | Value 序列化方式，默认 String |
| headers | object | 否 | 消息头 |

**cURL 示例**
```bash
curl -X POST 'https://kafka-ui.test.xxx.com/api/clusters/kafka-msk-test/topics/position-test-minISR-1/messages' \
  -H 'Content-Type: application/json' \
  -d '{
    "partition": 0,
    "key": "test-key-001",
    "content": "{\"message\":\"hello world\"}",
    "keySerde": "String",
    "valueSerde": "String"
  }'
```

---

### 2.2 消费消息 (SSE 流式接口)

**请求**
```http
GET /api/clusters/{clusterName}/topics/{topicName}/messages?keySerde=String&valueSerde=String&limit=100&seekType=BEGINNING&seekDirection=FORWARD
Accept: text/event-stream
```

**查询参数**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| keySerde | string | 否 | Key 反序列化方式 |
| valueSerde | string | 否 | Value 反序列化方式 |
| limit | int | 否 | 最大返回消息数，默认 100 |
| seekType | string | 否 | 起始位置：BEGINNING / LATEST / OFFSET / TIMESTAMP |
| seekDirection | string | 否 | 读取方向：FORWARD / BACKWARD |
| filterQueryType | string | 否 | 过滤类型：STRING_CONTAINS 等 |
| page | int | 否 | 分页页码 |

**响应格式** (Server-Sent Events)
```
data:{"type":"PHASE","phase":{"name":"Consumer created"}}

data:{"type":"CONSUMING","consuming":{"bytesConsumed":88,"messagesConsumed":1}}

data:{"type":"MESSAGE","message":{"partition":0,"offset":0,"timestamp":"2026-09-18T07:37:28.262Z","key":"test-key-001","content":"{\"message\":\"test message\"}"}}

data:{"type":"DONE","consuming":{"bytesConsumed":88,"messagesConsumed":1}}
```

**消息类型说明**
| type | 说明 |
|------|------|
| PHASE | 消费阶段信息 |
| CONSUMING | 消费进度信息 |
| MESSAGE | 实际消息内容 |
| DONE | 消费完成 |

**cURL 示例**
```bash
curl 'https://kafka-ui.test.xxx.com/api/clusters/kafka-msk-test/topics/position-test-minISR-1/messages?keySerde=String&valueSerde=String&limit=100&seekType=BEGINNING' \
  -H 'Accept: text/event-stream'
```

---

## 3. 集群信息

### 3.1 获取集群列表

**请求**
```http
GET /api/clusters
```

**cURL 示例**
```bash
curl 'https://kafka-ui.test.xxx.com/api/clusters'
```

---

### 3.2 获取序列化器列表

**请求**
```http
GET /api/clusters/{clusterName}/topic/{topicName}/serdes?use=SERIALIZE
GET /api/clusters/{clusterName}/topic/{topicName}/serdes?use=DESERIALIZE
```

**cURL 示例**
```bash
curl 'https://kafka-ui.test.xxx.com/api/clusters/kafka-msk-test/topic/position-test-minISR-1/serdes?use=SERIALIZE'
```

---

## 4. 批量操作脚本示例

### 4.1 批量创建 Topic（Shell 脚本）

```bash
#!/bin/bash

BASE_URL="https://kafka-ui.test.xxx.com/api"
CLUSTER="kafka-msk-test"

# 创建测试 Topic 函数
create_topic() {
    local name=$1
    local partitions=$2
    local replicas=$3
    local min_isr=$4
    
    echo "Creating topic: $name (partitions=$partitions, replicas=$replicas, minISR=$min_isr)"
    
    curl -s -X POST "${BASE_URL}/clusters/${CLUSTER}/topics" \
        -H 'Content-Type: application/json' \
        -d "{
            \"name\": \"$name\",
            \"partitions\": $partitions,
            \"replicationFactor\": \"$replicas\",
            \"configs\": {
                \"cleanup.policy\": \"delete\",
                \"min.insync.replicas\": \"$min_isr\"
            }
        }" | jq .
}

# 创建 minISR 测试 Topic
create_topic "position-test-minISR-1" 3 3 1
create_topic "position-test-minISR-2" 3 3 2
create_topic "position-test-minISR-3" 3 3 3

echo "Done!"
```

### 4.2 批量发送测试消息（Shell 脚本）

```bash
#!/bin/bash

BASE_URL="https://kafka-ui.test.xxx.com/api"
CLUSTER="kafka-msk-test"
TOPICS=("position-test-minISR-1" "position-test-minISR-2" "position-test-minISR-3")

# 发送消息函数
send_message() {
    local topic=$1
    local key=$2
    local value=$3
    
    curl -s -X POST "${BASE_URL}/clusters/${CLUSTER}/topics/${topic}/messages" \
        -H 'Content-Type: application/json' \
        -d "{
            \"key\": \"$key\",
            \"content\": \"$value\",
            \"keySerde\": \"String\",
            \"valueSerde\": \"String\"
        }"
}

# 向每个 Topic 发送测试消息
for topic in "${TOPICS[@]}"; do
    timestamp=$(date -Iseconds)
    message="{\"topic\":\"$topic\",\"timestamp\":\"$timestamp\",\"test\":true}"
    
    echo "Sending to $topic..."
    send_message "$topic" "test-key-$(date +%s)" "$message"
done

echo "Done!"
```

### 4.3 批量删除 Topic（Shell 脚本）

```bash
#!/bin/bash

BASE_URL="https://kafka-ui.test.xxx.com/api"
CLUSTER="kafka-msk-test"
TOPICS=("position-test-minISR-1" "position-test-minISR-2" "position-test-minISR-3")

for topic in "${TOPICS[@]}"; do
    echo "Deleting topic: $topic"
    curl -s -X DELETE "${BASE_URL}/clusters/${CLUSTER}/topics/${topic}"
done

echo "Done!"
```

---

## 5. 注意事项

1. **消息消费接口**使用 SSE (Server-Sent Events) 流式返回，需要使用支持 SSE 的客户端
2. **创建 Topic** 时 `replicationFactor` 需要是字符串类型
3. **min.insync.replicas** 配置在 `configs` 对象中，值为字符串类型
4. 所有接口都不需要认证（测试环境）
5. 生产环境可能需要配置认证头

---

## 6. 常用接口速查表

| 操作 | 方法 | 路径 |
|------|------|------|
| 创建 Topic | POST | /api/clusters/{cluster}/topics |
| 查询 Topic 列表 | GET | /api/clusters/{cluster}/topics |
| 查询 Topic 详情 | GET | /api/clusters/{cluster}/topics/{topic} |
| 查询 Topic 配置 | GET | /api/clusters/{cluster}/topics/{topic}/config |
| 删除 Topic | DELETE | /api/clusters/{cluster}/topics/{topic} |
| 发送消息 | POST | /api/clusters/{cluster}/topics/{topic}/messages |
| 消费消息 | GET | /api/clusters/{cluster}/topics/{topic}/messages |
| 获取集群列表 | GET | /api/clusters |
