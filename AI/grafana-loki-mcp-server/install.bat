@echo off
chcp 65001 >nul
echo ============================================
echo   Grafana Loki MCP Server - 安装脚本
echo ============================================
echo.

:: 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] 未检测到 Python，请先安装 Python 3.10+
    pause
    exit /b 1
)

:: 安装依赖
echo [1/3] 安装 Python 依赖...
pip install mcp httpx -q
if errorlevel 1 (
    echo [ERROR] 依赖安装失败，请检查网络
    pause
    exit /b 1
)
echo       ✓ mcp, httpx 已安装

:: 安装 Skill
echo [2/3] 安装 Kiro Skill...
set SKILL_DIR=%USERPROFILE%\.kiro\skills\grafana-loki-logs
if not exist "%SKILL_DIR%" mkdir "%SKILL_DIR%"
copy /Y "%~dp0SKILL.md" "%SKILL_DIR%\SKILL.md" >nul
echo       ✓ Skill 已安装到 %SKILL_DIR%

:: 提示配置
echo [3/3] 配置 MCP Server...
echo.
echo ============================================
echo   请手动完成以下配置：
echo ============================================
echo.
echo   1. 打开 .kiro/settings/mcp.json
echo   2. 添加以下配置（替换 ^<...^> 部分）：
echo.
echo   "grafana-loki": {
echo     "command": "python",
echo     "args": ["%~dp0server.py"],
echo     "env": {
echo       "GRAFANA_URL": "^<你的Grafana地址^>",
echo       "GRAFANA_SESSION": "^<你的Session Cookie^>",
echo       "GRAFANA_ORG_ID": "^<组织ID^>",
echo       "LOKI_DATASOURCE_UID": "^<Loki数据源UID^>",
echo       "LOKI_DATASOURCE_ID": "^<Loki数据源ID^>"
echo     },
echo     "disabled": false,
echo     "autoApprove": ["query_logs","query_logs_volume","query_log_context","list_services","list_label_values","query_logs_by_logql"]
echo   }
echo.
echo ============================================
echo   获取配置参数的方法：
echo   - 登录 Grafana，F12 打开 DevTools
echo   - Cookies 中找 grafana_session
echo   - Explore 页面查看网络请求中的 datasource uid/id
echo ============================================
echo.
echo 安装完成！重启 Kiro 后即可使用。
pause
