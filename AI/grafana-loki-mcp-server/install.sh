#!/bin/bash
echo "============================================"
echo "  Grafana Loki MCP Server v2 - 安装脚本"
echo "============================================"
echo ""

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] 未检测到 Python3，请先安装 Python 3.10+"
    exit 1
fi

# 安装依赖
echo "[1/5] 安装 Python 依赖..."
pip3 install mcp httpx -q
if [ $? -ne 0 ]; then
    echo "[ERROR] 依赖安装失败，请检查网络"
    exit 1
fi
echo "      √ mcp, httpx 已安装"

# 下载最新 server.py
echo "[2/5] 下载最新 server.py..."
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
DOWNLOAD_URL="https://raw.githubusercontent.com/liu294100/code-doctor-skills/refs/heads/main/AI/grafana-loki-mcp-server/server.py"
curl -s -o "${SCRIPT_DIR}/server.py" "${DOWNLOAD_URL}"
if [ $? -ne 0 ]; then
    echo "      ! 下载失败，将使用本地已有的 server.py"
else
    echo "      √ server.py 已更新到最新版"
fi

# 安装 Skill
echo "[3/5] 安装 Kiro Skill..."
SKILL_DIR="${HOME}/.kiro/skills/grafana-loki-logs"
mkdir -p "${SKILL_DIR}"
cp "${SCRIPT_DIR}/SKILL.md" "${SKILL_DIR}/SKILL.md"
echo "      √ Skill 已安装到 ${SKILL_DIR}"

# 获取用户输入
echo "[4/5] 配置 MCP Server..."
echo ""
echo "  请输入 Grafana 配置信息："
echo "  （团队默认值已预填，直接回车使用默认值）"
echo ""

read -p "  Grafana URL [https://grafana.xxx.com]: " GRAFANA_URL
GRAFANA_URL=${GRAFANA_URL:-https://grafana.xxx.com}

read -p "  Grafana 账号: " GRAFANA_USERNAME
read -sp "  Grafana 密码: " GRAFANA_PASSWORD
echo ""

read -p "  Organization ID [5]: " GRAFANA_ORG_ID
GRAFANA_ORG_ID=${GRAFANA_ORG_ID:-5}

read -p "  Loki Datasource UID [ffkfi6twwk6wwf]: " LOKI_UID
LOKI_UID=${LOKI_UID:-ffkfi6twwk6wwf}

read -p "  Loki Datasource ID [6]: " LOKI_ID
LOKI_ID=${LOKI_ID:-6}

SERVER_PATH="${SCRIPT_DIR}/server.py"

# 写入 MCP 配置
echo "[5/5] 写入 MCP 配置..."
MCP_DIR="${HOME}/.kiro/settings"
MCP_FILE="${MCP_DIR}/mcp.json"
mkdir -p "${MCP_DIR}"

if [ -f "${MCP_FILE}" ]; then
    echo ""
    echo "  已检测到现有 mcp.json，请手动将以下内容添加到 mcpServers 中："
    echo ""
    cat << EOF
  "grafana-loki": {
    "command": "python3",
    "args": ["${SERVER_PATH}"],
    "env": {
      "GRAFANA_URL": "${GRAFANA_URL}",
      "GRAFANA_USERNAME": "${GRAFANA_USERNAME}",
      "GRAFANA_PASSWORD": "${GRAFANA_PASSWORD}",
      "GRAFANA_ORG_ID": "${GRAFANA_ORG_ID}",
      "LOKI_DATASOURCE_UID": "${LOKI_UID}",
      "LOKI_DATASOURCE_ID": "${LOKI_ID}"
    },
    "disabled": false,
    "autoApprove": ["query_logs","query_logs_volume","query_log_context","list_services","list_label_values","query_logs_by_logql"]
  }
EOF
    echo ""
else
    cat > "${MCP_FILE}" << EOF
{
  "mcpServers": {
    "grafana-loki": {
      "command": "python3",
      "args": ["${SERVER_PATH}"],
      "env": {
        "GRAFANA_URL": "${GRAFANA_URL}",
        "GRAFANA_USERNAME": "${GRAFANA_USERNAME}",
        "GRAFANA_PASSWORD": "${GRAFANA_PASSWORD}",
        "GRAFANA_ORG_ID": "${GRAFANA_ORG_ID}",
        "LOKI_DATASOURCE_UID": "${LOKI_UID}",
        "LOKI_DATASOURCE_ID": "${LOKI_ID}"
      },
      "disabled": false,
      "autoApprove": ["query_logs","query_logs_volume","query_log_context","list_services","list_label_values","query_logs_by_logql"]
    }
  }
}
EOF
    echo "      √ MCP 配置已写入 ${MCP_FILE}"
fi

echo ""
echo "============================================"
echo "  安装完成！"
echo "============================================"
echo ""
echo "  使用方式："
echo "  1. 重启 Kiro（或命令面板搜 MCP 重连）"
echo "  2. 在 Chat 中直接说：\"查一下 xxx 最近的 error 日志\""
echo "  3. AI 会自动通过 Loki 查询并返回结果"
echo ""
echo "  下载地址（更新时用）："
echo "  https://raw.githubusercontent.com/liu294100/code-doctor-skills/refs/heads/main/AI/grafana-loki-mcp-server/server.py"
echo ""
