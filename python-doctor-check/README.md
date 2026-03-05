# Python 开发 Kiro Skills 套件

面向 Python 开发者的 Kiro AI Skills 集合，覆盖 Python SDK、Flask Web 应用、GUI 桌面小工具三大场景，每个场景均包含开发指导、代码审查、打包发布三个维度的 Skill。

## 目录结构

```
.kiro/skills/
├── 01-python-sdk/              # Python SDK 开发
│   ├── python-sdk-dev.md       # SDK 开发规范与指导（自动触发）
│   ├── python-sdk-review.md    # SDK 代码审查（自动触发）
│   └── python-sdk-package.md   # SDK 打包与发布（手动触发）
├── 02-flask/                   # Flask Web 应用
│   ├── flask-dev.md            # Flask 开发规范与指导（自动触发）
│   ├── flask-review.md         # Flask 代码审查（自动触发）
│   └── flask-package.md        # Flask 打包与部署（手动触发）
└── 03-gui-toolkit/             # GUI 桌面小工具
    ├── gui-dev.md              # GUI 开发规范与指导（自动触发）
    ├── gui-review.md           # GUI 代码审查（自动触发）
    └── gui-package.md          # GUI 打包与分发（手动触发）
```

## Skills 说明

### 01 - Python SDK 开发

| Skill | 触发方式 | 说明 |
|-------|---------|------|
| python-sdk-dev | 自动（打开 .py 文件） | 项目结构、命名规范、类型注解、异常设计、客户端设计、依赖管理、测试规范 |
| python-sdk-review | 自动（打开 .py 文件） | PEP 8 规范、类型注解、健壮性、模块设计、API 设计、性能、安全，共 5 大维度审查 |
| python-sdk-package | 手动 `#python-sdk-package` | pyproject.toml 配置、构建检查清单、PyPI/私有仓库发布、CI/CD 集成 |

### 02 - Flask Web 应用

| Skill | 触发方式 | 说明 |
|-------|---------|------|
| flask-dev | 自动（打开 .py 文件） | 应用工厂模式、蓝图组织、路由设计、SQLAlchemy 规范、安全配置、性能优化 |
| flask-review | 自动（打开 .py 文件） | Flask 专项（配置/路由/上下文）、数据库、安全（注入/CSRF/CORS）、性能、测试审查 |
| flask-package | 手动 `#flask-package` | Docker 容器化、Gunicorn 配置、Nginx 反向代理、数据库迁移、健康检查与监控 |

### 03 - GUI 桌面小工具

| Skill | 触发方式 | 说明 |
|-------|---------|------|
| gui-dev | 自动（打开 .py 文件） | 框架选型（Tkinter/PyQt/Flet）、MVC 架构、线程安全、配置持久化、用户体验规范 |
| gui-review | 自动（打开 .py 文件） | 架构分离、线程安全、UI 更新安全、跨平台兼容、性能、可访问性审查 |
| gui-package | 手动 `#gui-package` | PyInstaller/Nuitka 打包、跨平台构建、资源文件处理、代码签名、CI/CD 自动打包 |

## 使用方式

### 自动触发
开发类（`*-dev`）和审查类（`*-review`）Skill 配置为 `fileMatch` 模式，打开任何 `.py` 文件时自动加载。在聊天中请求开发建议或代码审查即可。

### 手动引用
打包类（`*-package`）Skill 配置为 `manual` 模式，在聊天输入框中使用 `#` 引用：

```
# SDK 打包发布
输入：#python-sdk-package 帮我检查打包配置并发布到 PyPI

# Flask 部署
输入：#flask-package 帮我生成 Docker 部署配置

# GUI 打包
输入：#gui-package 帮我把这个工具打包成 Windows exe

# 组合使用
输入：#python-sdk-review #python-sdk-package 审查代码并准备发布
```

## 覆盖维度

| 维度 | Python SDK | Flask | GUI 小工具 |
|------|-----------|-------|-----------|
| 项目结构 | ✅ src 布局 | ✅ 工厂模式 | ✅ MVC 分层 |
| 编码规范 | ✅ PEP 8 / 类型注解 | ✅ Flask 最佳实践 | ✅ 线程安全 |
| 代码审查 | ✅ 5 大维度 | ✅ Flask 专项 | ✅ 跨平台审查 |
| 异常处理 | ✅ 异常体系设计 | ✅ 错误处理器 | ✅ 全局异常捕获 |
| 安全审查 | ✅ 注入/依赖安全 | ✅ CSRF/CORS/注入 | ✅ 输入/数据安全 |
| 性能优化 | ✅ 异步/缓存 | ✅ 查询/缓存/部署 | ✅ 启动/内存/渲染 |
| 测试规范 | ✅ pytest / mock | ✅ 集成测试 | ✅ 逻辑层测试 |
| 打包发布 | ✅ PyPI / 私有仓库 | ✅ Docker / Gunicorn | ✅ PyInstaller / 签名 |
| CI/CD | ✅ GitHub Actions | ✅ Docker 部署 | ✅ 多平台自动构建 |
