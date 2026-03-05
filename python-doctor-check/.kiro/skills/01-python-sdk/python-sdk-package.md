---
inclusion: manual
---

# Python SDK 打包与发布 Skill

指导用户完成 Python SDK 的构建、打包、发布全流程。

---

## 一、构建配置

### 1.1 pyproject.toml 完整配置
```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "my-sdk"
dynamic = ["version"]
description = "SDK 简短描述"
readme = "README.md"
license = { text = "MIT" }
requires-python = ">=3.9"
authors = [
    { name = "Author Name", email = "author@example.com" },
]
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Typing :: Typed",
]
dependencies = [
    "httpx>=0.24,<1.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "pytest-cov>=4.0",
    "mypy>=1.0",
    "ruff>=0.1",
    "build>=1.0",
    "twine>=4.0",
]

[project.urls]
Homepage = "https://github.com/org/my-sdk"
Documentation = "https://my-sdk.readthedocs.io"
Repository = "https://github.com/org/my-sdk"
Changelog = "https://github.com/org/my-sdk/blob/main/CHANGELOG.md"

[tool.hatch.version]
path = "src/my_sdk/__init__.py"
```

### 1.2 版本管理
- 版本号定义在 `src/my_sdk/__init__.py` 中：`__version__ = "1.0.0"`
- 遵循语义化版本（SemVer）
- 使用 `hatch version` 或手动更新版本号
- 每次发布前更新 CHANGELOG.md

---

## 二、打包前检查清单

### 2.1 代码质量检查
```bash
# 代码格式化
ruff format src/ tests/

# 代码检查
ruff check src/ tests/ --fix

# 类型检查
mypy src/

# 运行测试
pytest tests/ -v --cov=src/my_sdk --cov-report=term-missing

# 覆盖率要求 ≥ 80%
pytest tests/ --cov=src/my_sdk --cov-fail-under=80
```

### 2.2 文件完整性检查
- [ ] README.md 内容完整（安装、快速开始、API 概览）
- [ ] LICENSE 文件存在
- [ ] CHANGELOG.md 已更新当前版本
- [ ] pyproject.toml 元数据完整
- [ ] `py.typed` 标记文件存在（PEP 561 类型支持）
- [ ] `.gitignore` 包含 `dist/`、`build/`、`*.egg-info/`

### 2.3 py.typed 标记
在包目录下创建空文件 `src/my_sdk/py.typed`，声明包支持类型检查。

---

## 三、构建与发布

### 3.1 构建
```bash
# 安装构建工具
pip install build

# 构建 sdist 和 wheel
python -m build

# 检查构建产物
ls dist/
# my_sdk-1.0.0.tar.gz
# my_sdk-1.0.0-py3-none-any.whl
```

### 3.2 发布前验证
```bash
# 安装 twine
pip install twine

# 检查包的元数据和格式
twine check dist/*

# 本地安装测试
pip install dist/my_sdk-1.0.0-py3-none-any.whl
python -c "import my_sdk; print(my_sdk.__version__)"
```

### 3.3 发布到 TestPyPI（测试）
```bash
twine upload --repository testpypi dist/*

# 从 TestPyPI 安装验证
pip install --index-url https://test.pypi.org/simple/ my-sdk
```

### 3.4 发布到 PyPI（正式）
```bash
twine upload dist/*
```

### 3.5 使用私有仓库
```bash
# 发布到私有 PyPI（如 Nexus、Artifactory、devpi）
twine upload --repository-url https://pypi.internal.company.com/simple/ dist/*

# 配置 ~/.pypirc
# [distutils]
# index-servers = internal
#
# [internal]
# repository = https://pypi.internal.company.com/simple/
# username = __token__
# password = pypi-xxx
```

---

## 四、CI/CD 集成

### 4.1 GitHub Actions 示例
```yaml
name: Publish

on:
  release:
    types: [published]

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install build twine
      - run: python -m build
      - run: twine check dist/*
      - run: twine upload dist/*
        env:
          TWINE_USERNAME: __token__
          TWINE_PASSWORD: ${{ secrets.PYPI_TOKEN }}
```

### 4.2 多版本测试矩阵
```yaml
strategy:
  matrix:
    python-version: ["3.9", "3.10", "3.11", "3.12"]
    os: [ubuntu-latest, macos-latest, windows-latest]
```

---

## 五、打包问题排查

### 5.1 常见问题
| 问题 | 原因 | 解决方案 |
|------|------|---------|
| `ModuleNotFoundError` 安装后导入失败 | 包目录结构不正确或缺少 `__init__.py` | 检查 `src/` 布局和 `[tool.hatch.build]` 配置 |
| `twine check` 报 warning | README 格式不被 PyPI 支持 | 使用标准 Markdown 或 reStructuredText |
| 版本号不一致 | `__init__.py` 和 `pyproject.toml` 版本不同步 | 使用 `dynamic = ["version"]` 从代码读取 |
| 缺少依赖 | `dependencies` 未声明运行时依赖 | 检查 `pyproject.toml` 的 `dependencies` 字段 |
| 包含不需要的文件 | 未配置排除规则 | 在 `pyproject.toml` 中配置 `[tool.hatch.build]` 排除规则 |

---

## 六、输出格式

打包审查按以下格式输出：

```
【检查项】构建配置 / 文件完整性 / 版本管理 / 发布流程
【状态】✅ 通过 / ❌ 未通过 / ⚠️ 需注意
【说明】具体描述
【修复建议】如未通过，给出修复方案
```
