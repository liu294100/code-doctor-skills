---
inclusion: fileMatch
fileMatchPattern: "**/*.py"
---

# Python SDK 开发 Skill

当用户开发 Python SDK 项目时，按照以下规范提供开发指导和代码生成建议。

---

## 一、项目结构规范

### 1.1 标准 SDK 项目布局
```
my-sdk/
├── src/
│   └── my_sdk/
│       ├── __init__.py          # 版本号、公开 API 导出
│       ├── client.py            # 主客户端类
│       ├── models.py            # 数据模型（dataclass / Pydantic）
│       ├── exceptions.py        # 自定义异常体系
│       ├── auth.py              # 认证模块
│       ├── utils.py             # 工具函数
│       └── _internal/           # 内部实现（下划线前缀表示私有）
│           ├── __init__.py
│           ├── http.py          # HTTP 请求封装
│           └── retry.py         # 重试逻辑
├── tests/
│   ├── __init__.py
│   ├── conftest.py              # pytest fixtures
│   ├── test_client.py
│   └── test_models.py
├── docs/
│   └── api.md
├── pyproject.toml               # 项目元数据与构建配置（PEP 621）
├── README.md
├── LICENSE
└── CHANGELOG.md
```

### 1.2 命名规范
- 包名：全小写，下划线分隔，如 `my_sdk`
- 模块名：全小写，下划线分隔，如 `http_client.py`
- 类名：大驼峰（PascalCase），如 `ApiClient`、`OrderResponse`
- 函数/方法名：全小写下划线，如 `get_user_by_id`
- 常量：全大写下划线，如 `DEFAULT_TIMEOUT`、`MAX_RETRY_COUNT`
- 私有成员：单下划线前缀 `_internal_method`，名称修饰用双下划线 `__private`
- 类型变量：大驼峰，如 `ResponseT = TypeVar("ResponseT")`

---

## 二、编码规范

### 2.1 类型注解
- 所有公开 API 必须有完整的类型注解
- 使用 `from __future__ import annotations` 启用延迟求值
- 复杂类型使用 `typing` 模块：`Optional`、`Union`、`List`、`Dict`、`Callable`
- Python 3.10+ 可使用 `X | Y` 语法替代 `Union[X, Y]`
- 返回值类型不要用 `Any`，尽量精确
- 使用 `TypedDict` 定义字典结构，使用 `Protocol` 定义鸭子类型接口

### 2.2 文档字符串
- 所有公开类和方法必须有 docstring（Google 风格或 NumPy 风格，项目内统一）
- 包含 `Args`、`Returns`、`Raises` 段落
- 示例：
```python
def get_order(self, order_id: str) -> Order:
    """根据订单 ID 获取订单详情。

    Args:
        order_id: 订单唯一标识符。

    Returns:
        Order 对象，包含订单完整信息。

    Raises:
        NotFoundError: 订单不存在时抛出。
        AuthenticationError: 认证失败时抛出。
    """
```

### 2.3 异常设计
- 定义 SDK 基础异常类，所有自定义异常继承自它
- 异常体系示例：
```python
class SdkError(Exception):
    """SDK 基础异常"""

class AuthenticationError(SdkError):
    """认证失败"""

class NotFoundError(SdkError):
    """资源不存在"""

class RateLimitError(SdkError):
    """请求频率超限"""

class ServerError(SdkError):
    """服务端错误"""
```
- 异常消息包含上下文信息（请求 ID、状态码、错误详情）
- 不要吞掉异常，使用 `raise ... from e` 保留异常链

### 2.4 数据模型
- 优先使用 `dataclass` 或 `Pydantic BaseModel`
- 不可变数据使用 `frozen=True`
- 提供 `to_dict()` / `from_dict()` 序列化方法
- 字段使用描述性名称，避免缩写

### 2.5 客户端设计
- 支持同步和异步两种调用方式（`httpx` 同时支持）
- 支持上下文管理器（`with` 语句）管理连接生命周期
- 支持自定义配置（超时、重试、代理、base_url）
- 支持请求/响应拦截器或中间件
- 示例：
```python
class ApiClient:
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.example.com",
        timeout: float = 30.0,
        max_retries: int = 3,
    ) -> None: ...

    def __enter__(self) -> "ApiClient": ...
    def __exit__(self, *args) -> None: ...

    async def __aenter__(self) -> "ApiClient": ...
    async def __aexit__(self, *args) -> None: ...
```

---

## 三、依赖管理

### 3.1 pyproject.toml 配置
- 使用 PEP 621 标准声明项目元数据
- 明确 `requires-python` 版本范围
- 运行时依赖最小化，宽松版本约束（`>=1.0,<3.0`）
- 开发依赖放在 `[project.optional-dependencies]` 的 `dev` 组
- 示例：
```toml
[project]
name = "my-sdk"
version = "1.0.0"
requires-python = ">=3.9"
dependencies = [
    "httpx>=0.24,<1.0",
    "pydantic>=2.0,<3.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "pytest-asyncio>=0.21",
    "pytest-cov>=4.0",
    "mypy>=1.0",
    "ruff>=0.1",
]
```

### 3.2 版本策略
- 遵循语义化版本（SemVer）：MAJOR.MINOR.PATCH
- 版本号在 `__init__.py` 中定义 `__version__`
- CHANGELOG.md 记录每个版本的变更

---

## 四、测试规范

### 4.1 测试结构
- 使用 `pytest` 作为测试框架
- 测试文件与源文件一一对应
- 使用 `conftest.py` 管理共享 fixtures
- 异步测试使用 `pytest-asyncio`

### 4.2 测试覆盖
- 公开 API 100% 覆盖
- 异常路径必须测试
- 边界条件必须测试
- 使用 `pytest-cov` 生成覆盖率报告，目标 ≥ 80%

### 4.3 Mock 策略
- 外部 HTTP 调用使用 `respx`（httpx）或 `responses`（requests）mock
- 不要 mock 内部实现细节，只 mock 外部边界
- 使用 `pytest.fixture` 管理测试数据

---

## 五、开发建议输出格式

对每个开发建议，按以下格式输出：

```
【建议分类】项目结构 / 编码规范 / 类型注解 / 异常设计 / 客户端设计 / 测试 / 依赖管理
【优先级】🔴 必须遵循 / 🟡 强烈建议 / 🔵 可选优化
【当前状态】描述当前代码的情况
【改进建议】具体的改进方案和示例代码
```
