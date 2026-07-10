---
name: browser-test
description: "基于 Playwright MCP 的浏览器自动化测试，支持页面交互、录制回放、接口验证、结合后端代码做端到端测试。当用户提到浏览器测试、页面测试、UI测试、录制操作、自动化测试、playwright 时激活。"
---

# 🌐 浏览器自动化测试 Skill (Browser Auto Test)

基于 Playwright MCP Server 的浏览器自动化测试工具，支持：
- 实时操作浏览器（导航、点击、填写、截图）
- 录制人工操作并生成自动化脚本
- 结合后端代码做端到端验证
- 监控网络请求验证接口调用

使用方式：在聊天中输入 `#browser-test` 并描述测试需求。

---

## 前置条件：安装 Playwright MCP

### 第一步：确认 Node.js 环境

```bash
node --version   # 需要 >= 18.x
npx --version    # 需要 >= 9.x
```

如果未安装 Node.js，从 https://nodejs.org/ 下载 LTS 版本安装。

### 第二步：配置 Playwright MCP Server

在 Kiro 的 MCP 配置文件中添加 Playwright Server。

**工作区配置**（推荐）：`项目根目录/.kiro/settings/mcp.json`
**用户全局配置**：`~/.kiro/settings/mcp.json`

在 `mcpServers` 中添加：

```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["-y", "@playwright/mcp@latest"],
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

### 第三步：安装浏览器

```bash
npx -y playwright install chromium
```

镜像加速：
```bash
# PowerShell
$env:PLAYWRIGHT_DOWNLOAD_HOST="https://npmmirror.com/mirrors/playwright"
npx -y playwright install chromium
```

### 第四步：验证

重启 Kiro 或重新连接 MCP Server，确认 playwright 状态为 running。

### 可选：CDP 连接已有 Chrome

```bash
# 以调试模式启动 Chrome
"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222
```

MCP 配置改为：
```json
"playwright": {
  "command": "npx",
  "args": ["-y", "@playwright/mcp@latest", "--cdp-endpoint", "http://localhost:9222"],
  "disabled": false,
  "autoApprove": []
}
```

---

## 核心能力

### 1. 实时浏览器操作

| 能力 | 说明 |
|------|------|
| 页面导航 | 打开 URL、前进后退、新标签页 |
| 元素交互 | 点击、双击、右键、拖拽、悬停 |
| 表单操作 | 输入文本、选择下拉框、勾选框、上传文件 |
| 键盘操作 | 按键、快捷键组合 |
| 等待 | 等待元素出现/消失、等待指定时间 |
| 截图 | 全页截图、元素截图 |
| JavaScript | 执行 JS（获取数据/注入 Token） |
| 网络监控 | 请求列表、请求/响应详情 |
| 控制台 | 捕获 console 信息和错误 |

### 2. 录制与回放

#### 方式一：Playwright Codegen 录制（推荐）

```bash
npx playwright codegen http://你的测试地址
npx playwright codegen --target java http://地址    # 生成Java代码
npx playwright codegen --target python http://地址  # 生成Python代码
npx playwright codegen --device="iPhone 14" http://地址  # 模拟手机
npx playwright codegen --save-storage=auth.json http://地址  # 保存登录状态
```

#### 方式二：MCP 逐步引导记录

我通过 snapshot 分析页面 → 你描述操作 → 我执行并记录 → 生成脚本

#### 方式三：CDP 观察 + 网络请求捕获

连接你的浏览器 → 你操作 → 我监控 API 调用 → 生成接口测试

### 3. 结合后端代码验证

读取 Controller/VO 代码 → 浏览器触发接口 → 对比返回数据与页面展示

---

## Playwright MCP 工具速查

| 工具 | 功能 |
|------|------|
| `browser_navigate` | 打开 URL |
| `browser_snapshot` | 页面结构快照 |
| `browser_find` | 搜索页面文本 |
| `browser_click` | 点击元素 |
| `browser_type` | 输入文本 |
| `browser_fill_form` | 批量填写表单 |
| `browser_select_option` | 选择下拉项 |
| `browser_hover` | 悬停 |
| `browser_drag` | 拖拽 |
| `browser_press_key` | 按键 |
| `browser_file_upload` | 上传文件 |
| `browser_take_screenshot` | 截图 |
| `browser_evaluate` | 执行 JS |
| `browser_wait_for` | 等待条件 |
| `browser_network_requests` | 网络请求列表 |
| `browser_network_request` | 请求详情 |
| `browser_console_messages` | 控制台消息 |
| `browser_handle_dialog` | 处理弹窗 |
| `browser_tabs` | 标签页管理 |
| `browser_close` | 关闭浏览器 |

---

## 测试报告格式

```markdown
# 浏览器测试报告
**目标：** xxx | **环境：** dev | **时间：** 2026-xx-xx

| # | 步骤 | 操作 | 预期 | 实际 | 状态 |
|---|------|------|------|------|------|
| 1 | 打开首页 | navigate | 200 | 200 | ✅ |

## 发现问题
| # | 问题 | 级别 | 文件 |
|---|------|------|------|

## 结论：测试通过/未通过
```

---

## 注意事项

1. 不要在生产环境执行写操作
2. 登录页面可通过 evaluate 注入 Token
3. SPA 页面需 wait_for 等待数据加载
4. 重要步骤截图存档
5. network_requests 验证 API 调用正确性
6. console_messages 检查 JS 报错

---

## 故障排查

| 问题 | 方案 |
|------|------|
| MCP 启动失败 | Node.js >= 18，`npx -y @playwright/mcp@latest --help` |
| 浏览器未装 | `npx -y playwright install chromium` |
| 下载慢 | 设置 PLAYWRIGHT_DOWNLOAD_HOST 镜像 |
| 元素找不到 | 用 browser_snapshot 查看结构 |
| CDP 连接失败 | 确保 Chrome 以 9222 端口启动 |
