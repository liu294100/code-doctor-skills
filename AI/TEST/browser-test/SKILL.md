---
name: browser-test
description: 基于 Playwright MCP 的浏览器自动化测试，支持页面交互、录制回放、接口验证、结合后端代码做端到端测试。当用户提到浏览器测试、页面测试、UI测试、录制操作、自动化测试、playwright 时激活。
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

**工作区配置**（推荐，仅对当前项目生效）：
文件路径：`项目根目录/.kiro/settings/mcp.json`

**用户全局配置**（对所有项目生效）：
文件路径：`~/.kiro/settings/mcp.json`（Windows: `C:\Users\<用户名>\.kiro\settings\mcp.json`）

在 `mcpServers` 中添加以下配置：

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

### 第三步：安装 Playwright 浏览器

首次使用前需下载 Chromium 浏览器内核（约 184MB）：

```bash
npx -y playwright install chromium
```

> 如果网络较慢，可设置国内镜像：
> ```bash
> # Windows CMD
> set PLAYWRIGHT_DOWNLOAD_HOST=https://npmmirror.com/mirrors/playwright
> npx -y playwright install chromium
>
> # PowerShell
> $env:PLAYWRIGHT_DOWNLOAD_HOST="https://npmmirror.com/mirrors/playwright"
> npx -y playwright install chromium
> ```

### 第四步：验证安装

重启 Kiro 或在命令面板搜索 "Reconnect MCP Server" 重新连接。
在 Kiro 的 MCP Server 面板中应能看到 `playwright` 状态为 running。

### 可选：连接已有 Chrome 浏览器（CDP 模式）

如果需要操作你正在使用的 Chrome 浏览器（观察你的手动操作）：

```bash
# Windows - 以调试模式启动 Chrome
"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222

# macOS
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222
```

然后 MCP 配置改为：
```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["-y", "@playwright/mcp@latest", "--cdp-endpoint", "http://localhost:9222"],
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

---

## 使用示例

```
#browser-test
打开 http://localhost:3000 首页，验证页面加载是否正常

#browser-test
登录管理后台，检查用户列表分页功能

#browser-test
录制一个 IPO 认购申请的操作流程，生成自动化测试脚本

#browser-test
打开 Swagger UI，测试 /api/users 接口返回是否正确

#browser-test
对比后端 UserController 代码逻辑，验证前端页面数据展示一致性
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
| 等待机制 | 等待元素出现/消失、等待指定时间 |
| 截图 | 全页截图、元素截图 |
| JavaScript | 在页面中执行任意 JS 代码 |
| 网络监控 | 查看请求列表、请求/响应详情 |
| 控制台 | 捕获 console.log/error 信息 |

### 2. 录制与回放（三种方式）

#### 方式一：Playwright Codegen 录制（推荐，最简单）

```bash
# 基本录制（生成 JavaScript 代码）
npx playwright codegen http://你的测试地址

# 生成 Java 代码
npx playwright codegen --target java http://你的测试地址

# 生成 Python 代码
npx playwright codegen --target python http://你的测试地址

# 模拟手机设备
npx playwright codegen --device="iPhone 14" http://你的测试地址

# 保存登录状态后续复用
npx playwright codegen --save-storage=auth.json http://你的测试地址
npx playwright codegen --load-storage=auth.json http://你的测试地址
```

运行后会打开两个窗口：
- 一个浏览器窗口供你手动操作
- 一个代码窗口实时生成对应的自动化代码

操作完成后复制代码给我，我可以帮你优化、添加断言、参数化。

#### 方式二：通过 MCP 逐步引导

1. 我通过 `browser_snapshot` 获取页面结构
2. 你描述操作步骤
3. 我用 MCP 工具执行操作并记录
4. 最后生成完整的自动化测试脚本

#### 方式三：CDP 连接观察你的操作

1. 你用调试模式启动 Chrome
2. MCP 连接到你的浏览器
3. 你正常操作，我通过 `browser_network_requests` 监控 API 调用
4. 根据捕获的请求参数和响应，生成接口测试用例

### 3. 结合后端代码验证

- 读取 Controller/Service 代码，理解接口逻辑和参数
- 在浏览器中触发对应操作，验证实际行为
- 对比接口文档（Apifox）与页面展示
- 检查前后端数据一致性

### 4. 生成测试脚本格式

| 格式 | 命令参数 | 适用场景 |
|------|---------|---------|
| JavaScript/TypeScript | `--target javascript` | 前端团队、Node.js 项目 |
| Java | `--target java` | Java 后端团队 |
| Python | `--target python` | 测试/运维团队 |
| C# | `--target csharp` | .NET 项目 |

---

## 工作流程

### 模式 A：直接自动化测试

```
用户描述测试目标
     ↓
1. 分析需求，确定测试步骤
2. browser_navigate 打开页面
3. browser_snapshot 获取页面结构
4. 执行交互操作（click/fill/select）
5. 验证结果（截图/snapshot/network）
6. 输出测试报告
```

### 模式 B：录制 → 优化 → 回放

```
用户运行 codegen 录制操作
     ↓
1. 用户复制录制的代码给我
2. 我优化脚本（添加等待、断言、参数化）
3. 封装成可重复执行的测试用例
4. 可选：通过 MCP 执行回放验证
```

### 模式 C：结合后端代码的端到端验证

```
用户指定要验证的 Controller/接口
     ↓
1. 读取 Controller 代码，提取接口路径和返回结构
2. 读取 Vo/DTO 定义，了解字段含义
3. 在浏览器中触发该接口调用
4. 对比页面展示与后端返回数据
5. 检查边界情况（空数据、分页、错误处理）
```

---

## Playwright MCP 工具速查表

| 工具名 | 功能 | 常用场景 |
|--------|------|---------|
| `browser_navigate` | 导航到 URL | 打开测试页面 |
| `browser_navigate_back` | 浏览器后退 | 返回上一页 |
| `browser_snapshot` | 页面可访问性快照 | 分析页面结构、查找元素 |
| `browser_find` | 搜索页面内容 | 查找特定文本/元素 |
| `browser_click` | 点击元素 | 按钮、链接、菜单项 |
| `browser_type` | 输入文本 | 搜索框、表单输入 |
| `browser_fill_form` | 填写多个表单字段 | 登录、注册表单 |
| `browser_select_option` | 选择下拉选项 | 下拉框选择 |
| `browser_hover` | 悬停在元素上 | hover 效果、菜单展开 |
| `browser_drag` | 拖拽元素 | 拖放排序 |
| `browser_press_key` | 按键 | Enter/Escape/Tab |
| `browser_file_upload` | 上传文件 | 文件上传功能 |
| `browser_take_screenshot` | 页面截图 | 视觉验证、存档 |
| `browser_evaluate` | 执行 JavaScript | 获取数据/注入Token/修改状态 |
| `browser_wait_for` | 等待条件 | 等待加载完成 |
| `browser_network_requests` | 网络请求列表 | 监控 API 调用 |
| `browser_network_request` | 请求详情 | 查看请求/响应内容 |
| `browser_console_messages` | 控制台消息 | 检查 JS 错误 |
| `browser_handle_dialog` | 处理弹窗 | alert/confirm/prompt |
| `browser_tabs` | 标签页管理 | 多页面测试 |
| `browser_close` | 关闭浏览器 | 测试结束清理 |

---

## 测试报告输出格式

```markdown
# 🌐 浏览器自动化测试报告

**测试目标：** [功能描述]
**测试环境：** [local/dev/test/prod]
**测试地址：** [URL]
**测试时间：** [日期时间]
**浏览器：** Chromium (Playwright)

---

## 📋 测试步骤与结果

| # | 步骤描述 | 操作 | 预期结果 | 实际结果 | 状态 |
|---|---------|------|---------|---------|------|
| 1 | 打开首页 | navigate | 页面正常加载 | HTTP 200 | ✅ |
| 2 | 点击登录 | click | 跳转登录页 | 跳转成功 | ✅ |

## 🔍 网络请求验证

| # | 接口 | 方法 | 状态码 | 响应时间 | 是否正常 |
|---|------|------|--------|---------|---------|
| 1 | /api/login | POST | 200 | 156ms | ✅ |

## ❌ 发现的问题

| # | 问题描述 | 严重级别 | 截图 | 相关代码 |
|---|---------|---------|------|---------|

## ✅ 结论
[测试通过 / 部分通过 / 未通过]
```

---

## 常见测试场景模板

### 场景一：登录流程测试

```
1. 导航到登录页
2. 填写用户名和密码
3. 点击登录按钮
4. 等待跳转完成
5. 验证登录后页面显示用户信息
6. 检查 localStorage/Cookie 中的 Token
```

### 场景二：列表分页测试

```
1. 打开列表页，验证默认第一页
2. 点击下一页/指定页码
3. 验证数据切换正确
4. 修改每页条数，验证列表数量变化
5. 检查网络请求中的分页参数
```

### 场景三：表单提交测试

```
1. 打开表单页面
2. 不填必填字段直接提交 → 验证错误提示
3. 填写无效数据 → 验证校验规则
4. 填写正确数据并提交
5. 验证成功提示和跳转
6. 检查网络请求的请求体
```

### 场景四：接口响应与页面渲染对比

```
1. 打开页面触发接口调用
2. 通过 network_requests 捕获目标接口
3. 检查请求参数是否符合预期
4. 验证响应数据与页面展示一致
5. 对比后端 VO 定义的字段
```

---

## 注意事项

1. **环境安全**：不要在生产环境执行写操作（下单、删除等）
2. **登录处理**：可通过 `browser_evaluate` 注入 Token 到 localStorage
3. **异步等待**：SPA 页面需要 `browser_wait_for` 确保数据加载完成
4. **截图存档**：重要步骤截图保存作为测试证据
5. **网络监控**：`browser_network_requests` 验证前端是否正确调用后端接口
6. **控制台错误**：`browser_console_messages` 检查 JS 报错
7. **多标签页**：复杂流程使用 `browser_tabs` 管理多个页面

---

## 故障排查

| 问题 | 解决方案 |
|------|---------|
| MCP Server 启动失败 | 确认 Node.js >= 18，运行 `npx -y @playwright/mcp@latest --help` 测试 |
| 浏览器未安装 | 运行 `npx -y playwright install chromium` |
| 下载浏览器很慢 | 设置 `PLAYWRIGHT_DOWNLOAD_HOST=https://npmmirror.com/mirrors/playwright` |
| 页面加载超时 | 检查目标 URL 是否可达，增加等待时间 |
| 元素找不到 | 使用 `browser_snapshot` 查看实际页面结构 |
| 需要代理 | MCP args 中添加 `--proxy-server=http://proxy:port` |
| CDP 连接失败 | 确保 Chrome 以 `--remote-debugging-port=9222` 启动，且端口未被占用 |
