---
name: setup-mcp
description: 快速安装mcp的skill
inclusion: manual
---

# 快速安装 MCP Server

从零开始安装和配置各类 MCP Server，包括环境依赖检查、安装命令、mcp.json 配置生成。

---

## 使用方式

在聊天中输入 `#setup-mcp`，然后告诉我要安装哪个 MCP Server（如 mysql、mssql、filesystem、gitlab、github 等）。

---

## 前置环境依赖

不同 MCP Server 需要不同的运行时，安装前需先确认环境：

| 运行时 | 检查命令 | 安装方式 |
|--------|---------|---------|
| Node.js 18+ | `node -v` | [https://nodejs.org/](https://nodejs.org/) |
| npx | `npx -v` | 随 Node.js 自带 |
| Python 3.10+ | `python --version` | [https://www.python.org/](https://www.python.org/) |
| uv / uvx | `uvx --version` | `pip install uv` 或 `brew install uv`，参考 [uv 安装指南](https://docs.astral.sh/uv/getting-started/installation/) |
| Docker | `docker -v` | [https://www.docker.com/](https://www.docker.com/) |

---

## 配置文件位置

Kiro 的 MCP 配置文件路径：

| 级别 | 路径 | 说明 |
|------|------|------|
| 用户级（全局） | `~/.kiro/settings/mcp.json` | 所有工作区共享 |
| 工作区级 | `.kiro/settings/mcp.json` | 仅当前工作区生效，优先级更高 |

配置合并优先级：用户级 < 工作区1 < 工作区2（后者覆盖前者）

---

## 一、MySQL MCP Server

### 依赖

- Node.js 18+（npx 方式）

### mcp.json 配置

```json
{
  "mcpServers": {
    "mysql": {
      "command": "npx",
      "args": [
        "-y",
        "@benborla29/mcp-server-mysql"
      ],
      "env": {
        "MYSQL_HOST": "127.0.0.1",
        "MYSQL_PORT": "3306",
        "MYSQL_USER": "root",
        "MYSQL_PASS": "<你的密码>",
        "MYSQL_DB": "<数据库名>"
      },
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

### 多数据库实例

如果需要连接多个 MySQL 实例，复制配置并修改 key 名和环境变量：

```json
{
  "mcpServers": {
    "mysql-dev": {
      "command": "npx",
      "args": ["-y", "@benborla29/mcp-server-mysql"],
      "env": {
        "MYSQL_HOST": "dev-db.example.com",
        "MYSQL_PORT": "3306",
        "MYSQL_USER": "dev_user",
        "MYSQL_PASS": "<密码>",
        "MYSQL_DB": "dev_db"
      }
    },
    "mysql-prod": {
      "command": "npx",
      "args": ["-y", "@benborla29/mcp-server-mysql"],
      "env": {
        "MYSQL_HOST": "prod-db.example.com",
        "MYSQL_PORT": "3306",
        "MYSQL_USER": "readonly_user",
        "MYSQL_PASS": "<密码>",
        "MYSQL_DB": "prod_db"
      }
    }
  }
}
```

---

## 二、MSSQL (SQL Server) MCP Server

### 方式 A：Node.js（npx）

```json
{
  "mcpServers": {
    "mssql": {
      "command": "npx",
      "args": [
        "-y",
        "@knight0zh/mssql-mcp-server"
      ],
      "env": {
        "MSSQL_HOST": "127.0.0.1",
        "MSSQL_PORT": "1433",
        "MSSQL_USER": "sa",
        "MSSQL_PASSWORD": "<你的密码>",
        "MSSQL_DATABASE": "<数据库名>"
      },
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

### 方式 B：Python（uvx）

依赖：Python 3.10+ 和 uv

```json
{
  "mcpServers": {
    "mssql": {
      "command": "uvx",
      "args": ["mssql-mcp-server"],
      "env": {
        "MSSQL_HOST": "127.0.0.1",
        "MSSQL_PORT": "1433",
        "MSSQL_USER": "sa",
        "MSSQL_PASSWORD": "<你的密码>",
        "MSSQL_DATABASE": "<数据库名>"
      },
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

---

## 三、Filesystem MCP Server

### 依赖

- Node.js 18+

### mcp.json 配置

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "<允许访问的目录路径1>",
        "<允许访问的目录路径2>"
      ],
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

### 示例：允许访问当前项目和文档目录

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "C:/Users/yourname/projects",
        "C:/Users/yourname/Documents"
      ]
    }
  }
}
```

> 注意：只有 args 中明确列出的目录才能被访问，这是安全边界。

---

## 四、GitLab MCP Server

### 方式 A：npx（推荐，社区维护）

依赖：Node.js 18+

```json
{
  "mcpServers": {
    "gitlab": {
      "command": "npx",
      "args": [
        "-y",
        "@zereight/mcp-gitlab"
      ],
      "env": {
        "GITLAB_PERSONAL_ACCESS_TOKEN": "<你的 GitLab Token>",
        "GITLAB_API_URL": "https://gitlab.com/api/v4"
      },
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

### 方式 B：Docker（官方 GitLab 镜像）

```json
{
  "mcpServers": {
    "gitlab": {
      "command": "docker",
      "args": [
        "run", "--rm", "-i",
        "-e", "GITLAB_PERSONAL_ACCESS_TOKEN",
        "-e", "GITLAB_API_URL",
        "mcp/gitlab"
      ],
      "env": {
        "GITLAB_PERSONAL_ACCESS_TOKEN": "<你的 GitLab Token>",
        "GITLAB_API_URL": "https://gitlab.com/api/v4"
      }
    }
  }
}
```

### 自建 GitLab 实例

将 `GITLAB_API_URL` 改为你的 GitLab 地址：

```
"GITLAB_API_URL": "https://your-gitlab.example.com/api/v4"
```

### Token 权限要求

GitLab Personal Access Token 需要以下 scope：
- `api`（完整 API 访问）
- 或按需选择：`read_api`、`read_repository`、`write_repository`

创建地址：GitLab → Settings → Access Tokens → Personal Access Tokens

---

## 五、GitHub MCP Server

### 方式 A：Docker（官方推荐）

依赖：Docker

```json
{
  "mcpServers": {
    "github": {
      "command": "docker",
      "args": [
        "run", "-i", "--rm",
        "-e", "GITHUB_PERSONAL_ACCESS_TOKEN",
        "ghcr.io/github/github-mcp-server"
      ],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "<你的 GitHub Token>"
      },
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

### 方式 B：远程服务器（无需安装，需 OAuth 支持）

```json
{
  "mcpServers": {
    "github": {
      "type": "http",
      "url": "https://api.githubcopilot.com/mcp/",
      "headers": {
        "Authorization": "Bearer <你的 GitHub Token>"
      }
    }
  }
}
```

### 只读模式

```json
{
  "mcpServers": {
    "github": {
      "command": "docker",
      "args": [
        "run", "-i", "--rm",
        "-e", "GITHUB_PERSONAL_ACCESS_TOKEN",
        "-e", "GITHUB_READ_ONLY=1",
        "ghcr.io/github/github-mcp-server"
      ],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "<你的 GitHub Token>"
      }
    }
  }
}
```

### 指定 Toolset（减少工具数量，提升 LLM 准确性）

```json
{
  "mcpServers": {
    "github": {
      "command": "docker",
      "args": [
        "run", "-i", "--rm",
        "-e", "GITHUB_PERSONAL_ACCESS_TOKEN",
        "-e", "GITHUB_TOOLSETS=repos,issues,pull_requests",
        "ghcr.io/github/github-mcp-server"
      ],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "<你的 GitHub Token>"
      }
    }
  }
}
```

### GitHub Enterprise Server

```json
{
  "mcpServers": {
    "github-enterprise": {
      "command": "docker",
      "args": [
        "run", "-i", "--rm",
        "-e", "GITHUB_PERSONAL_ACCESS_TOKEN",
        "-e", "GITHUB_HOST",
        "ghcr.io/github/github-mcp-server"
      ],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "<你的 Token>",
        "GITHUB_HOST": "https://github.your-company.com"
      }
    }
  }
}
```

### Token 权限要求

GitHub Personal Access Token (Fine-grained) 按需选择：
- `repo`（仓库读写）
- `read:org`（组织信息）
- `read:project`（项目信息）

创建地址：[https://github.com/settings/personal-access-tokens/new](https://github.com/settings/personal-access-tokens/new)

---

## 六、其他常用 MCP Server 速查

### Git（本地 Git 操作）

```json
{
  "mcpServers": {
    "git": {
      "command": "uvx",
      "args": ["mcp-server-git", "--repository", "<仓库路径>"]
    }
  }
}
```

### PostgreSQL

```json
{
  "mcpServers": {
    "postgres": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-postgres",
        "postgresql://user:password@localhost:5432/dbname"
      ]
    }
  }
}
```

### Redis

```json
{
  "mcpServers": {
    "redis": {
      "command": "npx",
      "args": ["-y", "@nicholasoxford/redis-mcp"],
      "env": {
        "REDIS_URL": "redis://localhost:6379"
      }
    }
  }
}
```

### MongoDB

```json
{
  "mcpServers": {
    "mongodb": {
      "command": "npx",
      "args": [
        "-y",
        "mongodb-mcp-server",
        "--connectionString",
        "mongodb://localhost:27017/dbname"
      ]
    }
  }
}
```

---

## 安装执行流程

当用户请求安装某个 MCP Server 时，按以下步骤执行：

### 1. 检查环境依赖

```bash
# 检查 Node.js
node -v

# 检查 Python / uv（如果需要 uvx 方式）
python --version
uvx --version

# 检查 Docker（如果需要 Docker 方式）
docker -v
```

### 2. 确认连接信息

向用户确认以下信息：
- 数据库类 MCP：Host、Port、User、Password、Database
- Git 类 MCP：Token、API URL（自建实例需要）
- Filesystem：允许访问的目录路径

### 3. 生成配置文件

根据用户选择的 MCP Server，生成对应的 mcp.json 配置，写入：
- 工作区级：`.kiro/settings/mcp.json`（推荐，仅当前项目生效）
- 用户级：`~/.kiro/settings/mcp.json`（全局生效）

### 4. 验证连接

配置写入后，MCP Server 会自动重连。可以通过以下方式验证：
- 在 Kiro 的 MCP Server 面板查看连接状态
- 或在命令面板搜索 `MCP` 查看相关命令

---

## 常见问题

### npx 首次运行慢

npx 首次运行会下载包，可能需要等待。如果超时，可以先手动安装：

```bash
npm install -g @benborla29/mcp-server-mysql
```

然后将 `command` 改为 `mcp-server-mysql`，去掉 npx 相关 args。

### uvx 未安装

```bash
# pip 安装
pip install uv

# 或 brew 安装（macOS）
brew install uv
```

安装后 uvx 命令即可用，无需额外安装 MCP Server 包。

### Docker 拉取镜像失败

```bash
# 如果 ghcr.io 拉取失败，先登出再重试
docker logout ghcr.io
docker pull ghcr.io/github/github-mcp-server
```

### 配置不生效

1. 检查 JSON 格式是否正确（逗号、引号）
2. 确认文件路径正确（`.kiro/settings/mcp.json`）
3. 在命令面板搜索 `MCP` 手动重连
4. 检查是否有工作区级配置覆盖了用户级配置

### 密码中有特殊字符

数据库密码中如果包含 `@`、`#`、`$` 等特殊字符，在 JSON 中直接写入即可（JSON 字符串会正确处理）。但在 URL 连接串中需要 URL 编码。
