---
inclusion: manual
---

# Python GUI 小工具打包与分发 Skill

指导用户将 Python GUI 应用打包为独立可执行文件，支持 Windows/macOS/Linux 分发。

---

## 一、打包工具选型

### 1.1 PyInstaller（推荐，最成熟）
- 支持 Windows / macOS / Linux
- 支持单文件（`--onefile`）和目录模式
- 支持自定义图标、版本信息
- 社区活跃，兼容性好

### 1.2 Nuitka（编译型，性能更好）
- 将 Python 编译为 C，运行速度更快
- 打包体积可能更小
- 适合对性能有要求的场景

### 1.3 cx_Freeze
- 跨平台支持
- 配置相对简单
- 适合简单项目

---

## 二、PyInstaller 打包

### 2.1 基础打包
```bash
# 安装
pip install pyinstaller

# 单文件打包
pyinstaller --onefile --windowed --name "MyTool" --icon=resources/icon.ico src/my_tool/__main__.py

# 目录模式打包（启动更快）
pyinstaller --windowed --name "MyTool" --icon=resources/icon.ico src/my_tool/__main__.py
```

### 2.2 spec 文件配置（推荐）
```python
# build.spec
# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['src/my_tool/__main__.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('src/my_tool/resources', 'my_tool/resources'),  # 打包资源文件
    ],
    hiddenimports=[],  # 动态导入的模块
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['pytest', 'mypy', 'ruff'],  # 排除开发依赖
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,      # 单文件模式包含这些
    a.datas,          # 单文件模式包含这些
    [],
    name='MyTool',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,         # UPX 压缩
    console=False,    # 无控制台窗口
    icon='resources/icon.ico',
    # Windows 版本信息
    version='version_info.txt',
)
```

```bash
# 使用 spec 文件打包
pyinstaller build.spec
```

### 2.3 资源文件处理
```python
import sys
from pathlib import Path

def get_resource_path(relative_path: str) -> Path:
    """获取资源文件路径，兼容开发环境和打包后环境。"""
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller 打包后的临时目录
        base_path = Path(sys._MEIPASS)
    else:
        base_path = Path(__file__).parent
    return base_path / relative_path
```

### 2.4 常见问题排查
| 问题 | 原因 | 解决方案 |
|------|------|---------|
| 打包后找不到资源文件 | 未在 `datas` 中声明 | 在 spec 文件的 `datas` 中添加资源路径 |
| 打包后 import 失败 | 动态导入未被检测到 | 在 `hiddenimports` 中添加模块名 |
| 杀毒软件误报 | 单文件模式的解压行为触发 | 使用目录模式，或对 exe 签名 |
| 打包体积过大 | 包含了不必要的依赖 | 使用虚拟环境，在 `excludes` 中排除 |
| macOS 无法打开 | 未签名或公证 | 使用 `codesign` 签名 + `notarytool` 公证 |

---

## 三、跨平台打包

### 3.1 Windows
```bash
# 打包为 exe
pyinstaller --onefile --windowed --icon=resources/icon.ico --name "MyTool" src/my_tool/__main__.py

# 可选：使用 Inno Setup 制作安装包
# 生成 setup.iss 配置后运行 Inno Setup 编译
```

### 3.2 macOS
```bash
# 打包为 .app
pyinstaller --onefile --windowed --icon=resources/icon.icns --name "MyTool" src/my_tool/__main__.py

# 签名（需要 Apple Developer 证书）
codesign --deep --force --sign "Developer ID Application: Name" dist/MyTool.app

# 公证
xcrun notarytool submit dist/MyTool.zip --apple-id "email" --team-id "TEAM_ID" --password "app-specific-password"
```

### 3.3 Linux
```bash
# 打包为可执行文件
pyinstaller --onefile --name "mytool" src/my_tool/__main__.py

# 可选：制作 AppImage
# 使用 appimage-builder 或 linuxdeploy
```

---

## 四、CI/CD 自动打包

### 4.1 GitHub Actions 多平台打包
```yaml
name: Build

on:
  release:
    types: [published]

jobs:
  build:
    strategy:
      matrix:
        include:
          - os: windows-latest
            artifact: MyTool.exe
          - os: macos-latest
            artifact: MyTool.app
          - os: ubuntu-latest
            artifact: mytool

    runs-on: ${{ matrix.os }}

    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - run: pip install -e ".[dev]" pyinstaller

      - run: pytest tests/ -v

      - run: pyinstaller build.spec

      - uses: actions/upload-artifact@v4
        with:
          name: ${{ matrix.os }}-build
          path: dist/
```

---

## 五、打包前检查清单

### 5.1 功能检查
- [ ] 所有功能在打包后正常工作
- [ ] 资源文件（图标、配置、数据）正确加载
- [ ] 文件读写路径使用用户目录（非安装目录）
- [ ] 日志文件写入用户数据目录

### 5.2 体积优化
- [ ] 使用独立虚拟环境打包（避免包含无关依赖）
- [ ] `excludes` 中排除了开发工具（pytest、mypy、ruff）
- [ ] 启用 UPX 压缩（`upx=True`）
- [ ] 大型资源文件考虑外置而非打包

### 5.3 安全检查
- [ ] 代码中无硬编码的密钥或密码
- [ ] 打包产物经过杀毒扫描
- [ ] Windows exe 已签名（可选但推荐）
- [ ] macOS app 已签名和公证（分发必须）

---

## 六、输出格式

```
【检查项】打包配置 / 资源文件 / 跨平台 / 体积优化 / 签名分发
【状态】✅ 通过 / ❌ 未通过 / ⚠️ 需注意
【说明】具体描述
【修复建议】如未通过，给出修复方案
```
