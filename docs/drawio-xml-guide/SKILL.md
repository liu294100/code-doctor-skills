---
name: drawio-xml-guide
description: 专业drawio-xml的写作，支持draw.io的图
inclusion: manual
---

# Draw.io XML 编写指南

## 概述

本指南用于指导 AI 生成符合 draw.io 标准的 `.drawio.xml` 文件，可直接在 draw.io / diagrams.net 中打开编辑。

## 文件基本结构

```xml
<?xml version="1.0" encoding="UTF-8"?>
<mxfile host="app.diagrams.net">
  <diagram name="图表名称" id="唯一ID">
    <mxGraphModel dx="1422" dy="762" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="1169" pageHeight="827" math="0" shadow="0">
      <root>
        <mxCell id="0" />
        <mxCell id="1" parent="0" />
        <!-- 图形元素从这里开始 -->
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
```

## 核心规则

### 1. ID 规则
- id="0" 是根节点，必须存在
- id="1" 是默认图层，parent="0"，必须存在
- 其他元素 id 使用有意义的前缀 + 序号，如 `node-1`, `edge-1`, `group-1`
- 避免使用纯数字 id（除 0 和 1 外）

### 2. 节点元素（mxCell vertex）

```xml
<mxCell id="node-1" parent="1" style="样式字符串" value="显示文本" vertex="1">
  <mxGeometry x="100" y="100" width="120" height="60" as="geometry" />
</mxCell>
```

### 3. 连线元素（mxCell edge）

```xml
<mxCell id="edge-1" parent="1" source="node-1" target="node-2" style="样式字符串" value="连线标签" edge="1">
  <mxGeometry relative="1" as="geometry" />
</mxCell>
```

### 4. 连线标签（edgeLabel）

```xml
<mxCell id="label-1" parent="edge-1" connectable="0" style="edgeLabel;html=1;align=center;verticalAlign=middle;resizable=0;points=[];" value="标签文字" vertex="1">
  <mxGeometry relative="1" x="0" y="0" as="geometry">
    <mxPoint as="offset" />
  </mxGeometry>
</mxCell>
```

### 5. 分组容器

```xml
<mxCell id="group-1" parent="1" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#FFF8E1;strokeColor=#F57F17;strokeWidth=2;verticalAlign=top;fontStyle=1;fontSize=14;dashed=1;arcSize=8;" value="分组名称" vertex="1">
  <mxGeometry x="100" y="100" width="400" height="300" as="geometry" />
</mxCell>
<!-- 子元素通过 parent 属性关联到分组，或直接放在同一 parent="1" 下通过坐标覆盖 -->
```

## 常用样式模板

### 服务节点（矩形圆角）
```
rounded=1;whiteSpace=wrap;html=1;fillColor=#FFE0B2;strokeColor=#E65100;fontSize=12;fontStyle=1;
```

### 数据库（圆柱形）
```
shape=cylinder;whiteSpace=wrap;html=1;boundedLbl=1;backgroundOutline=1;rounded=1;fontStyle=1;strokeColor=#E65100;fillColor=#DCEDC8;
```

### 消息队列（圆柱3D）
```
shape=cylinder3;whiteSpace=wrap;html=1;fillColor=#DCEDC8;strokeColor=#33691E;fontSize=12;fontStyle=1;size=10;
```

### 外部系统节点
```
rounded=1;whiteSpace=wrap;html=1;fillColor=#E1BEE7;strokeColor=#6A1B9A;fontSize=11;
```

### 风控/核心节点
```
rounded=1;whiteSpace=wrap;html=1;fillColor=#FFCDD2;strokeColor=#C62828;fontSize=11;fontStyle=1;
```

### 分组区域（虚线边框）
```
rounded=1;whiteSpace=wrap;html=1;fillColor=#FFF8E1;strokeColor=#F57F17;strokeWidth=2;verticalAlign=top;fontStyle=1;fontSize=14;dashed=1;arcSize=8;
```

### 客户端分组
```
rounded=1;whiteSpace=wrap;html=1;fillColor=#E3F2FD;strokeColor=#1565C0;strokeWidth=2;verticalAlign=top;fontStyle=1;fontSize=14;dashed=1;arcSize=8;
```

### 连线样式
```
edgeStyle=orthogonalEdgeStyle;rounded=1;strokeColor=#808080;strokeWidth=2;
```

## 颜色规范

| 用途 | 填充色 | 边框色 |
|------|--------|--------|
| 核心服务 | #FFE0B2 | #E65100 |
| 客户端 | #E3F2FD / #BBDEFB | #1565C0 |
| 外部系统 | #F3E5F5 / #E1BEE7 | #6A1B9A |
| 数据存储 | #DCEDC8 | #33691E |
| 风控/关键 | #FFCDD2 | #C62828 |
| 业务领域 | #FFCDD2 | #2E7D32 |
| 分组容器 | #FFF8E1 | #F57F17 |
| 连线 | - | #808080 |

## 布局建议

### 坐标系
- 原点 (0,0) 在左上角
- x 轴向右增长，y 轴向下增长
- gridSize=10，坐标值尽量是 10 的倍数

### 间距规范
- 同级节点水平间距：30-50px
- 同级节点垂直间距：20-40px
- 分组内边距：上方留 40px（放标题），其他方向 20px
- 节点默认尺寸：宽 120-160px，高 40-60px

### 分层布局（推荐）
- 从左到右：客户端 → 网关 → 核心服务 → 执行层 → 外部系统
- 从上到下：入金流程在上，交易流程在中，结算流程在下

## 完整示例：微服务架构图

```xml
<?xml version="1.0" encoding="UTF-8"?>
<mxfile host="app.diagrams.net">
  <diagram name="Microservice Architecture" id="arch-001">
    <mxGraphModel dx="1422" dy="762" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="1169" pageHeight="827" math="0" shadow="0">
      <root>
        <mxCell id="0" />
        <mxCell id="1" parent="0" />
        <!-- 分组：API 网关层 -->
        <mxCell id="group-gw" parent="1" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#E3F2FD;strokeColor=#1565C0;strokeWidth=2;verticalAlign=top;fontStyle=1;fontSize=14;dashed=1;arcSize=8;" value="API Gateway Layer" vertex="1">
          <mxGeometry x="50" y="50" width="200" height="200" as="geometry" />
        </mxCell>
        <!-- 网关节点 -->
        <mxCell id="node-gw1" parent="1" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#FFE0B2;strokeColor=#E65100;fontSize=12;fontStyle=1;" value="API Gateway" vertex="1">
          <mxGeometry x="90" y="100" width="120" height="50" as="geometry" />
        </mxCell>
        <!-- 分组：核心服务层 -->
        <mxCell id="group-core" parent="1" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#FFF8E1;strokeColor=#F57F17;strokeWidth=2;verticalAlign=top;fontStyle=1;fontSize=14;dashed=1;arcSize=8;" value="Core Services" vertex="1">
          <mxGeometry x="320" y="50" width="500" height="200" as="geometry" />
        </mxCell>
        <!-- 服务节点 -->
        <mxCell id="node-oms" parent="1" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#FFE0B2;strokeColor=#E65100;fontSize=12;fontStyle=1;" value="Order Service" vertex="1">
          <mxGeometry x="350" y="100" width="130" height="50" as="geometry" />
        </mxCell>
        <mxCell id="node-asset" parent="1" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#FFCDD2;strokeColor=#2E7D32;fontSize=12;fontStyle=1;" value="Asset Service" vertex="1">
          <mxGeometry x="520" y="100" width="130" height="50" as="geometry" />
        </mxCell>
        <mxCell id="node-risk" parent="1" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#FFCDD2;strokeColor=#C62828;fontSize=11;fontStyle=1;" value="Risk Service" vertex="1">
          <mxGeometry x="690" y="100" width="100" height="50" as="geometry" />
        </mxCell>
        <!-- 数据库 -->
        <mxCell id="node-db" parent="1" style="shape=cylinder;whiteSpace=wrap;html=1;boundedLbl=1;backgroundOutline=1;rounded=1;fontStyle=1;strokeColor=#33691E;fillColor=#DCEDC8;" value="MySQL" vertex="1">
          <mxGeometry x="520" y="300" width="60" height="60" as="geometry" />
        </mxCell>
        <!-- 消息队列 -->
        <mxCell id="node-mq" parent="1" style="shape=cylinder3;whiteSpace=wrap;html=1;fillColor=#DCEDC8;strokeColor=#33691E;fontSize=12;fontStyle=1;size=10;" value="Kafka" vertex="1">
          <mxGeometry x="690" y="300" width="100" height="60" as="geometry" />
        </mxCell>
        <!-- 连线 -->
        <mxCell id="edge-1" parent="1" source="node-gw1" target="node-oms" style="edgeStyle=orthogonalEdgeStyle;rounded=1;strokeColor=#808080;strokeWidth=2;" edge="1">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="edge-2" parent="1" source="node-oms" target="node-asset" style="edgeStyle=orthogonalEdgeStyle;rounded=1;strokeColor=#808080;strokeWidth=1.5;" value="调用" edge="1">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="edge-3" parent="1" source="node-oms" target="node-risk" style="edgeStyle=orthogonalEdgeStyle;rounded=1;strokeColor=#808080;strokeWidth=1.5;" value="风控校验" edge="1">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="edge-4" parent="1" source="node-oms" target="node-db" style="edgeStyle=orthogonalEdgeStyle;rounded=1;strokeColor=#808080;strokeWidth=1.5;" edge="1">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="edge-5" parent="1" source="node-oms" target="node-mq" style="edgeStyle=orthogonalEdgeStyle;rounded=1;strokeColor=#808080;strokeWidth=1.5;" value="发送事件" edge="1">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
```

## 多页图表

```xml
<?xml version="1.0" encoding="UTF-8"?>
<mxfile host="app.diagrams.net">
  <diagram name="Page 1 - Overview" id="page-1">
    <mxGraphModel ...>
      <root>...</root>
    </mxGraphModel>
  </diagram>
  <diagram name="Page 2 - Detail" id="page-2">
    <mxGraphModel ...>
      <root>...</root>
    </mxGraphModel>
  </diagram>
</mxfile>
```

## 特殊图形

### 菱形（判断/决策）
```
rhombus;whiteSpace=wrap;html=1;fillColor=#FFF9C4;strokeColor=#F57F17;
```

### 人形图标（Actor）
```
shape=mxgraph.basic.person;whiteSpace=wrap;html=1;fillColor=#E3F2FD;strokeColor=#1565C0;
```

### 云形（外部/云服务）
```
ellipse;shape=cloud;whiteSpace=wrap;html=1;fillColor=#F3E5F5;strokeColor=#6A1B9A;
```

### 文档形状
```
shape=document;whiteSpace=wrap;html=1;fillColor=#FFF8E1;strokeColor=#F57F17;
```

### 六边形
```
shape=hexagon;perimeter=hexagonPerimeter2;whiteSpace=wrap;html=1;fixedSize=1;fillColor=#DCEDC8;strokeColor=#33691E;
```

## 连线高级用法

### 带箭头方向的连线
```
edgeStyle=orthogonalEdgeStyle;rounded=1;strokeColor=#808080;strokeWidth=2;endArrow=classic;startArrow=none;
```

### 双向箭头
```
edgeStyle=orthogonalEdgeStyle;rounded=1;strokeColor=#808080;strokeWidth=2;endArrow=classic;startArrow=classic;
```

### 虚线连线
```
edgeStyle=orthogonalEdgeStyle;rounded=1;strokeColor=#808080;strokeWidth=1.5;dashed=1;
```

### 曲线连线
```
edgeStyle=entityRelationEdgeStyle;rounded=1;strokeColor=#808080;strokeWidth=1.5;
```

### 指定连线出入口方向
- `exitX=0` 左边出, `exitX=1` 右边出, `exitX=0.5` 中间出
- `exitY=0` 上边出, `exitY=1` 下边出, `exitY=0.5` 中间出
- entry 同理

```xml
<mxCell id="edge-x" parent="1" source="node-a" target="node-b" style="edgeStyle=orthogonalEdgeStyle;rounded=1;strokeColor=#808080;exitX=1;exitY=0.5;exitDx=0;exitDy=0;entryX=0;entryY=0.5;entryDx=0;entryDy=0;" edge="1">
  <mxGeometry relative="1" as="geometry" />
</mxCell>
```

## 注意事项

1. **必须包含 id="0" 和 id="1"** — 缺失会导致文件无法打开
2. **vertex="1"** 标记节点，**edge="1"** 标记连线 — 不能省略
3. **value 属性** 支持 HTML 标签（如 `<br>`），因为设置了 `html=1`
4. **style 是分号分隔的键值对**，最后一个分号可选
5. **mxGeometry** 的 `as="geometry"` 不能省略
6. **连线的 relative="1"** 表示使用相对坐标
7. **文件扩展名** 使用 `.drawio.xml` 以便 VS Code draw.io 插件识别
8. **编码** 必须是 UTF-8，中文直接写入 value 属性即可
9. **ID 唯一性** — 所有 mxCell 的 id 必须在整个文件中唯一
