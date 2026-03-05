---
inclusion: manual
---

# Flask 应用打包与部署 Skill

指导用户完成 Flask 应用的打包、容器化、部署全流程。

---

## 一、打包配置

### 1.1 pyproject.toml
```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "my-flask-app"
version = "1.0.0"
requires-python = ">=3.9"
dependencies = [
    "flask>=3.0,<4.0",
    "flask-sqlalchemy>=3.1,<4.0",
    "flask-migrate>=4.0,<5.0",
    "gunicorn>=21.0,<23.0",
    "psycopg2-binary>=2.9,<3.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "pytest-cov>=4.0",
    "ruff>=0.1",
]
```

### 1.2 依赖锁定
```bash
# 生成精确依赖锁文件
pip freeze > requirements.lock

# 或使用 pip-tools
pip-compile pyproject.toml -o requirements.lock
```

---

## 二、打包前检查清单

### 2.1 代码质量
```bash
# 格式化
ruff format src/ tests/

# 检查
ruff check src/ tests/ --fix

# 测试
pytest tests/ -v --cov=src/my_app --cov-fail-under=80
```

### 2.2 配置检查
- [ ] `DEBUG = False` 在生产配置中
- [ ] `SECRET_KEY` 从环境变量读取
- [ ] 数据库 URI 从环境变量读取
- [ ] 日志级别配置正确
- [ ] CORS 配置收紧（非 `*`）
- [ ] 静态文件由 Nginx 服务（非 Flask）

---

## 三、Docker 容器化

### 3.1 Dockerfile
```dockerfile
FROM python:3.12-slim AS base

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 安装 Python 依赖
COPY requirements.lock .
RUN pip install --no-cache-dir -r requirements.lock

# 复制应用代码
COPY src/ src/
COPY migrations/ migrations/

# 非 root 用户运行
RUN useradd -m appuser
USER appuser

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "src.my_app:create_app()"]
```

### 3.2 docker-compose.yml
```yaml
services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - FLASK_ENV=production
      - DATABASE_URL=postgresql://user:pass@db:5432/myapp
      - SECRET_KEY=${SECRET_KEY}
    depends_on:
      db:
        condition: service_healthy

  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: myapp
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U user -d myapp"]
      interval: 5s
      timeout: 5s
      retries: 5

volumes:
  pgdata:
```

### 3.3 .dockerignore
```
.git
.env
__pycache__
*.pyc
.pytest_cache
.mypy_cache
dist/
build/
*.egg-info
tests/
docs/
```

---

## 四、部署方案

### 4.1 Gunicorn 配置
```python
# gunicorn.conf.py
import multiprocessing

bind = "0.0.0.0:8000"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "gevent"  # 或 "gthread"
timeout = 120
keepalive = 5
max_requests = 1000
max_requests_jitter = 50
accesslog = "-"
errorlog = "-"
loglevel = "info"
```

### 4.2 Nginx 反向代理
```nginx
upstream flask_app {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name example.com;

    location / {
        proxy_pass http://flask_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /app/static/;
        expires 30d;
    }
}
```

### 4.3 数据库迁移（部署时）
```bash
# 容器启动后执行迁移
flask db upgrade
```

---

## 五、健康检查与监控

### 5.1 健康检查端点
```python
@app.route("/health")
def health():
    try:
        db.session.execute(text("SELECT 1"))
        return jsonify({"status": "healthy"}), 200
    except Exception:
        return jsonify({"status": "unhealthy"}), 503
```

### 5.2 日志配置
```python
import logging
from logging.handlers import RotatingFileHandler

def configure_logging(app: Flask):
    handler = RotatingFileHandler("app.log", maxBytes=10_000_000, backupCount=5)
    handler.setFormatter(logging.Formatter(
        "[%(asctime)s] %(levelname)s in %(module)s: %(message)s"
    ))
    app.logger.addHandler(handler)
    app.logger.setLevel(logging.INFO)
```

---

## 六、输出格式

```
【检查项】打包配置 / Docker / 部署 / 安全 / 监控
【状态】✅ 通过 / ❌ 未通过 / ⚠️ 需注意
【说明】具体描述
【修复建议】如未通过，给出修复方案
```
