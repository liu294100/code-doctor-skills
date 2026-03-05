---
inclusion: fileMatch
fileMatchPattern: "**/*.py"
---

# Flask Web 应用开发 Skill

当用户开发 Flask Web 应用时，按照以下规范提供开发指导。

---

## 一、项目结构规范

### 1.1 应用工厂模式（推荐）
```
my-flask-app/
├── src/
│   └── my_app/
│       ├── __init__.py          # create_app() 工厂函数
│       ├── config.py            # 配置类（Dev/Test/Prod）
│       ├── extensions.py        # 扩展初始化（db, migrate, login_manager）
│       ├── models/              # 数据模型
│       │   ├── __init__.py
│       │   └── user.py
│       ├── api/                 # API 蓝图
│       │   ├── __init__.py
│       │   ├── auth.py
│       │   └── users.py
│       ├── services/            # 业务逻辑层
│       │   ├── __init__.py
│       │   └── user_service.py
│       ├── schemas/             # 请求/响应序列化（Marshmallow / Pydantic）
│       │   ├── __init__.py
│       │   └── user_schema.py
│       ├── utils/               # 工具函数
│       │   ├── __init__.py
│       │   └── decorators.py
│       └── templates/           # Jinja2 模板（如有前端）
│           └── base.html
├── tests/
│   ├── conftest.py
│   ├── test_auth.py
│   └── test_users.py
├── migrations/                  # Alembic 数据库迁移
├── pyproject.toml
├── README.md
└── .env.example
```

### 1.2 应用工厂函数
```python
from flask import Flask

def create_app(config_name: str = "development") -> Flask:
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # 初始化扩展
    register_extensions(app)
    # 注册蓝图
    register_blueprints(app)
    # 注册错误处理
    register_error_handlers(app)

    return app
```

---

## 二、路由与视图

### 2.1 蓝图组织
- 按功能模块划分蓝图（auth、users、orders）
- 蓝图使用 URL 前缀：`bp = Blueprint("users", __name__, url_prefix="/api/v1/users")`
- RESTful 风格：资源名用名词复数，HTTP 方法语义正确

### 2.2 请求处理
- 使用 `request.get_json()` 获取 JSON 数据，检查返回值是否为 None
- 使用 Marshmallow 或 Pydantic 做请求参数校验
- 文件上传检查类型、大小限制
- 分页参数设置默认值和最大值限制

### 2.3 响应格式
- 统一 JSON 响应格式：
```python
def success_response(data=None, message="ok", code=200):
    return jsonify({"code": code, "message": message, "data": data}), code

def error_response(message, code=400, errors=None):
    return jsonify({"code": code, "message": message, "errors": errors}), code
```
- HTTP 状态码使用正确：200/201/204/400/401/403/404/500

### 2.4 错误处理
```python
def register_error_handlers(app: Flask):
    @app.errorhandler(400)
    def bad_request(e):
        return error_response("Bad Request", 400)

    @app.errorhandler(404)
    def not_found(e):
        return error_response("Not Found", 404)

    @app.errorhandler(500)
    def internal_error(e):
        app.logger.error(f"Internal error: {e}")
        return error_response("Internal Server Error", 500)
```

---

## 三、数据库与 ORM

### 3.1 SQLAlchemy 模型规范
- 模型类继承 `db.Model`
- 表名使用小写复数：`__tablename__ = "users"`
- 主键使用自增 ID 或 UUID
- 必须有 `created_at`、`updated_at` 时间戳字段
- 外键和关系使用 `relationship` + `back_populates`
- 敏感字段（密码）不要出现在 `to_dict()` 方法中

### 3.2 数据库迁移
- 使用 Flask-Migrate（Alembic）管理迁移
- 每次模型变更生成迁移脚本并审查
- 迁移脚本提交到版本控制
- 生产环境迁移前先在测试环境验证

### 3.3 查询优化
- 避免 N+1 查询：使用 `joinedload` 或 `subqueryload`
- 大数据量使用分页查询（`paginate()`）
- 只查询需要的字段：`db.session.query(User.id, User.name)`
- 批量操作使用 `bulk_insert_mappings` / `bulk_update_mappings`

---

## 四、安全规范

### 4.1 认证与授权
- 使用 Flask-Login 或 JWT（Flask-JWT-Extended）
- 密码使用 `werkzeug.security.generate_password_hash` 加密
- Token 设置合理的过期时间
- 敏感接口添加权限装饰器

### 4.2 输入安全
- 所有用户输入做校验和清洗
- SQL 使用 ORM 参数化查询，禁止拼接 SQL
- XSS 防护：Jinja2 默认自动转义，API 返回 JSON 时注意
- CSRF 防护：使用 Flask-WTF 的 CSRFProtect
- CORS 配置：使用 Flask-CORS，不要使用 `origins="*"`

### 4.3 配置安全
- `SECRET_KEY` 使用强随机值，不要硬编码
- 生产环境关闭 `DEBUG` 模式
- 敏感配置通过环境变量注入
- `.env` 文件加入 `.gitignore`

---

## 五、性能优化

### 5.1 缓存
- 使用 Flask-Caching 缓存频繁访问的数据
- 静态资源设置缓存头
- 数据库查询结果缓存（注意缓存失效策略）

### 5.2 异步处理
- 耗时操作使用 Celery 异步任务
- 邮件发送、文件处理、报表生成等放入任务队列
- 任务需要幂等性设计

### 5.3 部署优化
- 使用 Gunicorn + Gevent/Uvicorn 作为 WSGI 服务器
- 配置合理的 worker 数量（`2 * CPU + 1`）
- 静态文件使用 Nginx 直接服务
- 启用 Gzip 压缩

---

## 六、开发建议输出格式

```
【建议分类】项目结构 / 路由设计 / 数据库 / 安全 / 性能 / 测试
【优先级】🔴 必须遵循 / 🟡 强烈建议 / 🔵 可选优化
【当前状态】描述当前代码的情况
【改进建议】具体的改进方案和示例代码
```
