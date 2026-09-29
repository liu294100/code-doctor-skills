# Kafbat UI MCP Server

通过 [Kafbat UI](https://github.com/kafbat/kafka-ui)（v1.x）REST API 管理 Kafka，替代旧的 `kafka-ui-mcp-server`。

## 与旧版差异

| 项目 | 旧 kafka-ui | Kafbat UI |
|------|------------|-----------|
| 认证 | 无 | 表单登录 `POST /login`，SESSION Cookie（自动登录、失效自动重登） |
| 消费消息 | `/messages?seekType=...` | `/messages/v2?mode=LATEST/EARLIEST/FROM_OFFSET/...` |
| 消息内容字段 | `content` | `value` |

## 安装

```bash
pip install -r requirements.txt
```

将 `example.mcp.json` 中的配置合并到 `~/.kiro/settings/mcp.json`。

## 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| KAFBAT_UI_URL | Kafbat UI 地址 | http://localhost:8080 |
| KAFBAT_UI_USERNAME / KAFBAT_UI_PASSWORD | 登录账号密码 | 空（不登录） |
| KAFBAT_UI_CLUSTER | 默认集群 | kafka-msk-test |
| KAFBAT_UI_VERIFY_SSL | 是否校验证书 | true |
| KAFBAT_UI_MAX_VALUE_LEN | 单条消息 value 最大返回长度，0 不截断 | 5000 |

## 工具列表

| 分类 | 工具 | 说明 |
|------|------|------|
| 集群 | list_clusters / list_brokers | 集群、Broker 信息 |
| Topic | list_topics / get_topic / get_topic_config | 查询 |
| Topic | create_topic / batch_create_topics / delete_topic | 管理（删除需 `confirm=true`） |
| 消息 | consume_messages | 支持 LATEST/EARLIEST/FROM_OFFSET/TO_OFFSET/FROM_TIMESTAMP/TO_TIMESTAMP、关键字过滤、指定分区 |
| 消息 | produce_message | 发送 String 消息，可带 Key、Headers |
| 消费组 | list_consumer_groups / get_consumer_group / get_topic_consumer_groups | 消费组及 Lag |

## 示例

- 查某订单最新推送：`consume_messages(topic_name="abc", filter_text="97650699")`
- 从某时间点开始查：`consume_messages(topic_name="abc", mode="FROM_TIMESTAMP", timestamp="2026-09-29 10:00:00")`
- 查 Topic 消费积压：`get_topic_consumer_groups(topic_name="abc")`
