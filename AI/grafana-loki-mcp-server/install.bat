@echo off
chcp 65001 >nul
echo ============================================
echo   Grafana Loki MCP Server v2 - 安装脚本
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
echo [1/5] 安装 Python 依赖...
pip install mcp httpx -q
if errorlevel 1 (
    echo [ERROR] 依赖安装失败，请检查网络
    pause
    exit /b 1
)
echo       √ mcp, httpx 已安装

:: 下载最新 server.py
echo [2/5] 下载最新 server.py...
set DOWNLOAD_URL=https://raw.githubusercontent.com/liu294100/code-doctor-skills/refs/heads/main/AI/grafana-loki-mcp-server/server.py
set SERVER_DIR=%~dp0
curl -s -o "%SERVER_DIR%server.py" "%DOWNLOAD_URL%"
if errorlevel 1 (
    echo       ! 下载失败，将使用本地已有的 server.py
) else (
    echo       √ server.py 已更新到最新版
)

:: 安装 Skill
echo [3/5] 安装 Kiro Skill...
set SKILL_DIR=%USERPROFILE%\.kiro\skills\grafana-loki-logs
if not exist "%SKILL_DIR%" mkdir "%SKILL_DIR%"
copy /Y "%~dp0SKILL.md" "%SKILL_DIR%\SKILL.md" >nul
echo       √ Skill 已安装到 %SKILL_DIR%

:: 获取用户输入
echo [4/5] 配置 MCP Server...
echo.
echo   请输入 Grafana 配置信息：
echo   （团队默认值已预填，直接回车使用默认值）
echo.
set "GRAFANA_URL=https://grafana.xxx.com"
set /p "GRAFANA_URL=  Grafana URL [https://grafana.xxx.com]: "
set /p "GRAFANA_USERNAME=  Grafana 账号: "
set /p "GRAFANA_PASSWORD=  Grafana 密码: "
set "GRAFANA_ORG_ID=5"
set /p "GRAFANA_ORG_ID=  Organization ID [5]: "
set "LOKI_UID=ffkfi6twwk6wwf"
set /p "LOKI_UID=  Loki Datasource UID [ffkfi6twwk6wwf]: "
set "LOKI_ID=6"
set /p "LOKI_ID=  Loki Datasource ID [6]: "

:: 获取 server.py 路径（正斜杠）
set "SERVER_PATH=%~dp0server.py"
set "SERVER_PATH=%SERVER_PATH:\=/%"

:: 写入 MCP 配置
echo [5/5] 写入 MCP 配置...
set MCP_DIR=%USERPROFILE%\.kiro\settings
set MCP_FILE=%MCP_DIR%\mcp.json
if not exist "%MCP_DIR%" mkdir "%MCP_DIR%"

if exist "%MCP_FILE%" (
    echo.
    echo   已检测到现有 mcp.json，请手动将以下内容添加到 mcpServers 中：
    echo.
    echo   "grafana-loki": {
    echo     "command": "python",
    echo     "args": ["%SERVER_PATH%"],
    echo     "env": {
    echo       "GRAFANA_URL": "%GRAFANA_URL%",
    echo       "GRAFANA_USERNAME": "%GRAFANA_USERNAME%",
    echo       "GRAFANA_PASSWORD": "%GRAFANA_PASSWORD%",
    echo       "GRAFANA_ORG_ID": "%GRAFANA_ORG_ID%",
    echo       "LOKI_DATASOURCE_UID": "%LOKI_UID%",
    echo       "LOKI_DATASOURCE_ID": "%LOKI_ID%"
    echo     },
    echo     "disabled": false,
    echo     "autoApprove": ["query_logs","query_logs_volume","query_log_context","list_services","list_label_values","query_logs_by_logql"]
    echo   }
    echo.
) else (
    (
    echo {
    echo   "mcpServers": {
    echo     "grafana-loki": {
    echo       "command": "python",
    echo       "args": ["%SERVER_PATH%"],
    echo       "env": {
    echo         "GRAFANA_URL": "%GRAFANA_URL%",
    echo         "GRAFANA_USERNAME": "%GRAFANA_USERNAME%",
    echo         "GRAFANA_PASSWORD": "%GRAFANA_PASSWORD%",
    echo         "GRAFANA_ORG_ID": "%GRAFANA_ORG_ID%",
    echo         "LOKI_DATASOURCE_UID": "%LOKI_UID%",
    echo         "LOKI_DATASOURCE_ID": "%LOKI_ID%"
    echo       },
    echo       "disabled": false,
    echo       "autoApprove": ["query_logs","query_logs_volume","query_log_context","list_services","list_label_values","query_logs_by_logql"]
    echo     }
    echo   }
    echo }
    ) > "%MCP_FILE%"
    echo       √ MCP 配置已写入 %MCP_FILE%
)

echo.
echo ============================================
echo   安装完成！
echo ============================================
echo.
echo   使用方式：
echo   1. 重启 Kiro（或命令面板搜 MCP 重连）
echo   2. 在 Chat 中直接说："查一下 xxx 最近的 error 日志"
echo   3. AI 会自动通过 Loki 查询并返回结果
echo.
echo   下载地址（更新时用）：
echo   https://raw.githubusercontent.com/liu294100/code-doctor-skills/refs/heads/main/AI/grafana-loki-mcp-server/server.py
echo.
pause
