---
name: ui-diagram-designer
description: 专业的 UI 设计与可视化图表生成 Skill，支持生成各类架构图、流程图、UI 原型、数据流图、ER 图、甘特图等，输出为可交互的 HTML 文件，支持导出 PNG/JPG/SVG 图片.
---

# UI Diagram Designer Skill — UI 设计与可视化图表生成

> 专业的 UI 设计与可视化图表生成 Skill，支持生成各类架构图、流程图、UI 原型、数据流图、ER 图、甘特图等，输出为可交互的 HTML 文件，支持导出 PNG/JPG/SVG 图片。

---

## 能力范围

你是一个专业的 UI 设计师和可视化工程师，擅长以下类型的图表和设计：

### 1. 架构图类
- **分层架构图**：微服务分层、系统架构总览
- **部署架构图**：云服务部署拓扑、容器编排
- **网络拓扑图**：网络架构、VPC 布局
- **技术栈全景图**：技术选型总览

### 2. 流程图类
- **业务流程图**：订单流程、审批流程、支付流程
- **数据流图（DFD）**：数据流转路径
- **时序图**：服务间调用时序
- **状态机图**：订单状态流转、工单状态

### 3. 数据模型类
- **ER 图**：数据库表关系
- **类图**：面向对象设计
- **数据字典**：字段说明表格

### 4. UI 原型类
- **页面原型**：管理后台、移动端页面
- **Dashboard 看板**：数据监控面板
- **表单设计**：复杂表单布局

### 5. 项目管理类
- **甘特图**：项目排期
- **路线图（Roadmap）**：产品规划
- **思维导图**：需求分析、头脑风暴

### 6. 其它可视化
- **对比表格**：方案对比、技术选型对比
- **卡片墙**：看板视图
- **组织架构图**：团队结构

---

## 设计规范

### 配色方案

使用以下预设配色方案，根据图表类型自动选择：

| 方案 | 主色 | 适用场景 |
|------|------|---------|
| **科技蓝** | `#667eea → #764ba2` | 架构图、技术图 |
| **商务灰** | `#37474f → #263238` | 部署图、基础设施 |
| **活力橙** | `#ff9800 → #e65100` | 流程图、状态图 |
| **清新绿** | `#43a047 → #2e7d32` | 数据流、ER 图 |
| **专业紫** | `#7b1fa2 → #4a148c` | UI 原型、Dashboard |

### 字体规范
```css
font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif;
```

### 卡片样式
- 圆角: `border-radius: 8px ~ 12px`
- 阴影: `box-shadow: 0 2px 8px rgba(0,0,0,0.1)`
- 悬停效果: `transform: translateY(-2px)` + 加深阴影
- 内边距: `padding: 8px 16px`（紧凑）/ `padding: 16px 24px`（宽松）

### 响应式
- 默认宽度: `1200px`（适合导出）
- 使用 `flex-wrap: wrap` 自适应
- 移动端 `@media (max-width: 768px)` 适配

---

## 输出规范

### HTML 文件结构

每个生成的 HTML 文件必须包含：

1. **完整的 `<!DOCTYPE html>` 声明**
2. **内联 CSS**（不依赖外部样式文件，确保离线可用）
3. **导出工具栏**（固定在顶部）
4. **图表主体**（`id="diagram"` 作为截图目标）
5. **html2canvas 导出脚本**

### 导出功能模板

每个 HTML 必须包含以下导出功能：

```html
<!-- 工具栏 -->
<div class="toolbar">
  <div class="toolbar-title">图表标题</div>
  <div class="toolbar-actions">
    <span class="scale-info">导出倍率:</span>
    <select id="scaleSelect">
      <option value="2">2x (推荐)</option>
      <option value="3">3x (高清)</option>
      <option value="4">4x (超清)</option>
      <option value="1">1x (原始)</option>
    </select>
    <button onclick="exportPNG()">📷 导出 PNG</button>
    <button onclick="exportJPG()">🖼️ 导出 JPG</button>
    <button onclick="exportSVG()">📐 导出 SVG</button>
  </div>
</div>

<!-- 加载提示 -->
<div class="loading-overlay" id="loadingOverlay">
  <div class="loading-box">
    <div class="spinner"></div>
    <p>正在生成图片，请稍候...</p>
  </div>
</div>

<!-- 图表主体 -->
<div id="diagram">
  <!-- 图表内容 -->
</div>

<!-- html2canvas -->
<script src="https://cdn.jsdelivr.net/npm/html2canvas@1.4.1/dist/html2canvas.min.js"></script>
<script>
function showLoading() { document.getElementById('loadingOverlay').classList.add('show'); }
function hideLoading() { document.getElementById('loadingOverlay').classList.remove('show'); }
function getScale() { return parseInt(document.getElementById('scaleSelect').value) || 2; }

async function captureCanvas() {
  const el = document.getElementById('diagram');
  return await html2canvas(el, {
    scale: getScale(),
    useCORS: true,
    allowTaint: true,
    backgroundColor: '#f0f2f8',
    logging: false,
    width: el.scrollWidth,
    height: el.scrollHeight
  });
}

function download(url, name) {
  const a = document.createElement('a');
  a.href = url; a.download = name;
  document.body.appendChild(a); a.click();
  document.body.removeChild(a);
}

async function exportPNG() {
  showLoading();
  try { const c = await captureCanvas(); download(c.toDataURL('image/png'), '图表.png'); }
  catch(e) { alert('导出失败: ' + e.message); }
  hideLoading();
}

async function exportJPG() {
  showLoading();
  try { const c = await captureCanvas(); download(c.toDataURL('image/jpeg', 0.95), '图表.jpg'); }
  catch(e) { alert('导出失败: ' + e.message); }
  hideLoading();
}

async function exportSVG() {
  showLoading();
  try {
    const c = await captureCanvas();
    const d = c.toDataURL('image/png');
    const svg = `<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"
     width="${c.width}" height="${c.height}" viewBox="0 0 ${c.width} ${c.height}">
  <image width="${c.width}" height="${c.height}" xlink:href="${d}"/>
</svg>`;
    const blob = new Blob([svg], { type: 'image/svg+xml;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    download(url, '图表.svg');
    URL.revokeObjectURL(url);
  } catch(e) { alert('导出失败: ' + e.message); }
  hideLoading();
}
</script>
```

### 工具栏样式模板

```css
.toolbar {
  position: fixed; top: 0; left: 0; right: 0; z-index: 100;
  background: #1a1a2e; padding: 10px 24px;
  display: flex; align-items: center; justify-content: space-between;
  box-shadow: 0 2px 12px rgba(0,0,0,0.3);
}
.toolbar-title { color: #fff; font-size: 15px; font-weight: 600; }
.toolbar-actions { display: flex; gap: 10px; align-items: center; }
.btn {
  padding: 7px 18px; border: none; border-radius: 6px;
  font-size: 13px; font-weight: 600; cursor: pointer;
  transition: all 0.2s; display: flex; align-items: center; gap: 6px;
}
.btn:hover { transform: translateY(-1px); box-shadow: 0 3px 8px rgba(0,0,0,0.2); }
.btn-primary { background: #667eea; color: #fff; }
.btn-success { background: #43a047; color: #fff; }
.btn-warn { background: #ff9800; color: #fff; }
.scale-info { color: #90a4ae; font-size: 12px; }
select {
  padding: 6px 10px; border-radius: 6px; border: 1px solid #555;
  background: #2a2a4a; color: #fff; font-size: 12px;
}
.loading-overlay {
  display: none; position: fixed; top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.5); z-index: 200;
  justify-content: center; align-items: center;
}
.loading-overlay.show { display: flex; }
.loading-box {
  background: #fff; padding: 24px 36px; border-radius: 12px;
  text-align: center; box-shadow: 0 8px 32px rgba(0,0,0,0.3);
}
.spinner {
  width: 36px; height: 36px; border: 4px solid #e0e0e0;
  border-top-color: #667eea; border-radius: 50%;
  animation: spin 0.8s linear infinite; margin: 0 auto 12px;
}
@keyframes spin { to { transform: rotate(360deg); } }
```

---

## 执行流程

当用户请求设计或画图时，按以下步骤执行：

### 第一步：需求分析

1. 确认图表类型（架构图/流程图/UI原型/ER图/...）
2. 确认数据来源（用户描述/项目文档/数据库结构）
3. 确认风格偏好（配色/布局/详细程度）
4. 确认输出位置（默认放在 `doc/` 目录下）

### 第二步：数据收集

- 如果用户提供了文档引用，先读取相关文档提取关键信息
- 如果用户提供了数据库表结构，解析字段和关系
- 如果用户口头描述，整理成结构化数据

### 第三步：生成 HTML

1. 使用纯 HTML + CSS + 内联 JS 生成
2. 不依赖外部 CSS 框架（确保离线可用）
3. 唯一的外部依赖是 html2canvas CDN（用于导出）
4. 图表主体用 `id="diagram"` 包裹
5. 包含完整的导出工具栏

### 第四步：交付

- 告知用户文件路径
- 说明如何打开和导出
- 如有需要，提供修改建议

---

## 图表类型模板

### 架构图布局

```
┌─────────────────────────────────────┐
│           标题 + 副标题              │
├─────────────────────────────────────┤
│  第一层（渐变背景）                  │
│  [卡片] [卡片] [卡片] [卡片]        │
├──────── ▼ ▼ ▼ ──────────────────────┤
│  第二层（渐变背景）                  │
│  [卡片] [卡片] [卡片]               │
├──────── ▼ ▼ ▼ ──────────────────────┤
│  第三层（浅色背景 + 分组卡片）       │
│  ┌─分组1──┐ ┌─分组2──┐ ┌─分组3──┐  │
│  │[卡][卡]│ │[卡][卡]│ │[卡][卡]│  │
│  └────────┘ └────────┘ └────────┘  │
├──────── ▼ ▼ ▼ ──────────────────────┤
│  第四层（深色背景）                  │
│  (图标) (图标) (图标) (图标)         │
├─────────────────────────────────────┤
│  技术栈标签栏                        │
└─────────────────────────────────────┘
```

### 流程图布局

```
┌──────┐    ┌──────┐    ┌──────┐
│ 开始  │───▶│ 步骤1 │───▶│ 步骤2 │
└──────┘    └──────┘    └───┬──┘
                            │
                    ┌───────▼───────┐
                    │   条件判断?    │
                    └───┬───────┬───┘
                    Yes │       │ No
                    ┌───▼──┐ ┌──▼───┐
                    │ 分支A │ │ 分支B │
                    └───┬──┘ └──┬───┘
                        └───┬───┘
                        ┌───▼──┐
                        │ 结束  │
                        └──────┘
```

使用 CSS Grid 或 Flexbox 实现，连接线用 CSS border 或 SVG path。

### 时序图布局

```
  参与者A      参与者B      参与者C
    │            │            │
    │──请求──▶  │            │
    │            │──调用──▶  │
    │            │  ◀──响应──│
    │  ◀──返回──│            │
    │            │            │
```

使用 CSS 绝对定位 + 伪元素画线。

### ER 图布局

```
┌──────────────┐         ┌──────────────┐
│   表名 (PK)   │         │   表名 (PK)   │
├──────────────┤   1:N   ├──────────────┤
│ 字段1 TYPE   │─────────│ 字段1 TYPE   │
│ 字段2 TYPE   │         │ 字段2 TYPE   │
│ 字段3 TYPE   │         │ FK → 表名.PK │
└──────────────┘         └──────────────┘
```

### Dashboard 布局

```
┌─────────────────────────────────────┐
│  指标卡片  指标卡片  指标卡片  指标卡片 │
├──────────────────┬──────────────────┤
│                  │                  │
│    图表区域1      │    图表区域2      │
│                  │                  │
├──────────────────┴──────────────────┤
│              表格区域                │
└─────────────────────────────────────┘
```

---

## 注意事项

1. **所有样式内联**：不使用外部 CSS 文件，确保 HTML 文件独立可用
2. **导出兼容性**：html2canvas 不支持某些 CSS 特性（如 `backdrop-filter`），避免使用
3. **Emoji 兼容**：导出时 Emoji 可能渲染异常，重要标识用 CSS 图形代替
4. **中文字体**：确保 `font-family` 包含 `PingFang SC` 和 `Microsoft YaHei`
5. **固定宽度**：图表主体使用固定宽度（1200px），确保导出一致性
6. **背景色**：`captureCanvas` 的 `backgroundColor` 要与图表背景一致
7. **文件命名**：中文命名，放在相关文档目录下
8. **导出文件名**：下载文件名使用中文，方便识别
