---
name: read-drawio
description: 读取并解析 draw.io（.drawio）文件，提取图表中的节点、连接线、文本内容和层级关系，以结构化文本形式呈现图表内容，支持图表摘要、元素查找和内容分析。
---

# Draw.io 图表读取 Skill

读取 `.drawio` 文件并解析其 XML 内容，将图表中的节点、连接关系、文本标签以结构化的方式呈现出来，方便理解图表内容而无需打开图形编辑器。

使用方式：在聊天中输入 `#read-drawio` 并提供 `.drawio` 文件路径。

---

## 使用示例

```
#read-drawio
帮我读取 doc/design/order-flow.drawio，告诉我里面画了什么

#read-drawio
解析 doc/design/system-architecture.drawio，列出所有模块和它们之间的调用关系

#read-drawio
读取 doc/design/er-diagram.drawio，提取所有表名和字段信息

#read-drawio
对比 doc/design/v1.drawio 和 doc/design/v2.drawio 两个版本的差异
```

---

## 解析步骤

当用户提供 `.drawio` 文件路径时，按以下步骤执行：

### 第一步：读取文件

使用 readFile 工具读取 `.drawio` 文件的完整 XML 内容。

### 第二步：识别图表类型

根据节点样式和布局判断图表类型：

| 特征 | 图表类型 |
|------|---------|
| 矩形节点 + 垂直分层排列 | 架构图 |
| 圆角矩形 + 菱形判断 + 箭头连接 | 流程图 |
| 水平排列参与者 + 垂直生命线 | 时序图 |
| cylinder 样式节点 + 字段列表 | ER 图 |
| 带方法/属性的矩形 + 继承箭头 | 类图 |
| 云/服务器图标 + 网络连接 | 部署图 |

### 第三步：提取元素

从 XML 中提取以下信息：

#### 节点（vertex）
```
解析每个 vertex="1" 的 mxCell：
- id：节点唯一标识
- value：节点显示文本（可能包含 HTML 标签，需清理）
- style：节点样式（形状、颜色、字体等）
- geometry：位置（x, y）和尺寸（width, height）
- parent：父节点 ID（用于识别分组/容器）
```

#### 连接线（edge）
```
解析每个 edge="1" 的 mxCell：
- id：连接线唯一标识
- value：连接线标签文本（如"调用"、"1:N"）
- source：起始节点 ID
- target：目标节点 ID
- style：线条样式（实线/虚线、箭头类型）
```

#### 分组/容器
```
解析 parent 不为 "1" 的节点，识别分组关系：
- 容器节点：style 中包含 "group" 或 "swimlane"
- 子节点：parent 指向容器节点的 ID
```

### 第四步：清理 HTML 标签

节点 value 中可能包含 HTML 格式：
```
<b>OrderController</b><br><i>adapter/restful</i>
→ 提取为：OrderController (adapter/restful)
```

清理规则：
- 移除 `<b>`、`<i>`、`<br>`、`<div>`、`<font>` 等 HTML 标签
- 保留纯文本内容
- `<br>` 和 `<div>` 转换为换行

---

## 输出格式

### 架构图输出格式

```
## 图表摘要

**文件：** doc/design/system-architecture.drawio
**类型：** 架构图
**节点数：** 12
**连接数：** 15

### 层级结构

┌─ 接入层
│  ├── OrderController
│  └── FeeController
├─ 业务层
│  ├── OrderApplicationService
│  └── FeeCalculationService
├─ 数据层
│  ├── OrderMapper
│  └── FeeMapper
└─ 存储层
   └── MySQL

### 调用关系

OrderController → OrderApplicationService (HTTP)
OrderApplicationService → FeeCalculationService (调用)
OrderApplicationService → OrderMapper (数据访问)
FeeCalculationService → FeeMapper (数据访问)
OrderMapper → MySQL (SQL)
```

### 流程图输出格式

```
## 图表摘要

**文件：** doc/design/order-flow.drawio
**类型：** 流程图
**步骤数：** 8

### 流程步骤

1. [开始] 用户下单
2. [处理] 参数校验
3. [判断] 校验通过？
   ├─ 是 → 4. 费用计算
   └─ 否 → 7. 返回错误
4. [处理] 费用计算
5. [处理] 创建订单
6. [处理] 推送消息
7. [结束] 返回结果
```

### ER 图输出格式

```
## 图表摘要

**文件：** doc/design/er-diagram.drawio
**类型：** ER 图
**表数：** 3

### 表结构

tb_order
├── 🔑 id (BIGINT)
├── order_no (VARCHAR)
├── account_id (VARCHAR)
├── status (VARCHAR)
├── create_time (DATETIME)
└── update_time (DATETIME)

tb_order_fees_record
├── 🔑 id (BIGINT)
├── order_id (BIGINT) → tb_order.id
├── fee_id (VARCHAR)
├── fee_amount (DECIMAL)
└── create_time (DATETIME)

### 表关系

tb_order 1:N tb_order_fees_record (order_id)
tb_order 1:N tb_order_fill_detail (order_id)
```

### 时序图输出格式

```
## 图表摘要

**文件：** doc/design/order-sequence.drawio
**类型：** 时序图
**参与者：** 4

### 参与者

1. Client
2. OrderController
3. OrderService
4. Database

### 消息序列

1. Client → OrderController: POST /api/v1/orders
2. OrderController → OrderService: createOrder(req)
3. OrderService → Database: INSERT INTO tb_order
4. Database → OrderService: orderId
5. OrderService → OrderController: OrderVO
6. OrderController → Client: WebResponse<OrderVO>
```

---

## 对比分析

当用户要求对比两个 `.drawio` 文件时：

1. 分别读取两个文件
2. 提取各自的节点和连接线
3. 对比差异：
   - 新增的节点/连接线
   - 删除的节点/连接线
   - 修改的节点（文本变化、位置变化、样式变化）
4. 输出差异报告

```
## 对比报告

**文件A：** doc/design/v1.drawio
**文件B：** doc/design/v2.drawio

### 新增（B 中有，A 中无）
+ 节点：RiskCheckService
+ 连接：OrderService → RiskCheckService

### 删除（A 中有，B 中无）
- 节点：OldValidationService
- 连接：OrderController → OldValidationService

### 修改
~ OrderService: 文本从 "订单服务" 改为 "订单业务服务"
```
