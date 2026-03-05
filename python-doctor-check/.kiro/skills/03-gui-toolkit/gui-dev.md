---
inclusion: fileMatch
fileMatchPattern: "**/*.py"
---

# Python GUI 小工具开发 Skill

当用户开发 Python GUI 桌面小工具时，按照以下规范提供开发指导。支持 Tkinter、PyQt/PySide、Flet 等框架。

---

## 一、项目结构规范

### 1.1 标准 GUI 项目布局
```
my-gui-tool/
├── src/
│   └── my_tool/
│       ├── __init__.py          # 版本号
│       ├── __main__.py          # 入口：python -m my_tool
│       ├── app.py               # 应用主窗口
│       ├── views/               # 视图/页面
│       │   ├── __init__.py
│       │   ├── main_view.py
│       │   └── settings_view.py
│       ├── models/              # 数据模型
│       │   ├── __init__.py
│       │   └── config.py
│       ├── services/            # 业务逻辑（与 UI 解耦）
│       │   ├── __init__.py
│       │   └── file_service.py
│       ├── widgets/             # 自定义控件
│       │   ├── __init__.py
│       │   └── status_bar.py
│       ├── resources/           # 图标、图片、样式
│       │   ├── icon.ico
│       │   └── style.qss
│       └── utils/
│           ├── __init__.py
│           └── platform.py      # 跨平台兼容
├── tests/
├── pyproject.toml
├── README.md
└── build.spec                   # PyInstaller 打包配置
```

### 1.2 入口文件 `__main__.py`
```python
"""允许通过 python -m my_tool 启动应用。"""
from my_tool.app import main

if __name__ == "__main__":
    main()
```

---

## 二、框架选型指南

### 2.1 Tkinter（内置，轻量小工具）
- 优点：Python 内置，无需安装，打包体积小
- 适合：文件处理工具、配置编辑器、简单表单工具
- 美化方案：`ttkbootstrap`、`customtkinter`
- 注意：主线程运行 UI，耗时操作必须放到子线程

### 2.2 PyQt6 / PySide6（功能丰富）
- 优点：控件丰富、跨平台一致性好、支持 QSS 样式
- 适合：复杂桌面应用、数据可视化工具、多窗口应用
- 注意：GPL（PyQt6）vs LGPL（PySide6）许可证差异
- 信号槽机制处理事件，`QThread` 处理后台任务

### 2.3 Flet（现代 UI，Flutter 风格）
- 优点：声明式 UI、现代外观、支持 Web/桌面/移动端
- 适合：快速原型、现代风格工具、需要跨平台的场景
- 注意：相对较新，社区资源较少

---

## 三、核心开发规范

### 3.1 UI 与逻辑分离（MVC/MVP）
- 视图层（View）：只负责 UI 展示和用户交互
- 业务层（Service）：核心逻辑，不依赖任何 UI 框架
- 数据层（Model）：数据结构和持久化
- 好处：业务逻辑可独立测试，UI 框架可替换

### 3.2 线程安全
- GUI 框架的 UI 更新必须在主线程执行
- 耗时操作（文件 I/O、网络请求、计算）放到后台线程
- Tkinter：使用 `threading.Thread` + `root.after()` 回调更新 UI
- PyQt：使用 `QThread` + 信号（Signal）更新 UI
- 禁止在子线程直接操作 UI 控件

```python
# Tkinter 线程安全示例
import threading

def long_task():
    result = do_heavy_work()
    root.after(0, lambda: update_ui(result))  # 回调到主线程

threading.Thread(target=long_task, daemon=True).start()
```

### 3.3 配置持久化
- 使用 `json` 或 `toml` 存储用户配置
- 配置文件路径：
  - Windows: `%APPDATA%/my_tool/config.json`
  - macOS: `~/Library/Application Support/my_tool/config.json`
  - Linux: `~/.config/my_tool/config.json`
- 使用 `platformdirs` 库获取跨平台路径
- 配置读写做异常处理，损坏时使用默认值

### 3.4 国际化（i18n）
- 使用 `gettext` 或简单的字典映射
- UI 文本不要硬编码，统一管理
- 支持中英文切换

### 3.5 日志记录
- 使用 `logging` 模块，不要用 `print`
- 日志文件存储在用户数据目录
- 提供日志级别切换（Debug 模式）

---

## 四、用户体验规范

### 4.1 窗口管理
- 设置合理的默认窗口大小和最小尺寸
- 记住窗口位置和大小（持久化到配置）
- 设置应用图标（`.ico` for Windows，`.icns` for macOS）
- 窗口标题包含应用名称和版本号

### 4.2 交互反馈
- 耗时操作显示进度条或加载动画
- 操作完成后给出成功/失败提示
- 危险操作（删除、覆盖）弹出确认对话框
- 输入校验实时反馈（红色边框、提示文字）

### 4.3 快捷键
- 常用操作绑定快捷键（Ctrl+S 保存、Ctrl+Q 退出）
- 提供菜单栏显示快捷键
- 支持 Tab 键在控件间切换

### 4.4 错误处理
- 全局异常捕获，弹出错误对话框而非直接崩溃
- 错误信息对用户友好，技术细节写入日志
```python
import sys
import traceback

def exception_hook(exc_type, exc_value, exc_tb):
    error_msg = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    logging.error(error_msg)
    # 弹出错误对话框
    show_error_dialog(f"发生错误：{exc_value}")

sys.excepthook = exception_hook
```

---

## 五、开发建议输出格式

```
【建议分类】项目结构 / 框架选型 / UI 设计 / 线程安全 / 用户体验 / 跨平台
【优先级】🔴 必须遵循 / 🟡 强烈建议 / 🔵 可选优化
【当前状态】描述当前代码的情况
【改进建议】具体的改进方案和示例代码
```
