#!/bin/bash
echo "============================================"
echo "  Grafana Loki MCP Server - 安装脚本"
echo "============================================"
echo ""

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] 未检测到 Python3，请先安装 Python 3.10+"
    exit 1
fi

# 安装依赖
echo "[1/3] 安装 Python 依赖..."
pip3 install mcp httpx -q
if [ $? -ne 0 ]; then
    echo "[ERROR] 依赖安装失败，请检查网络"
    exit 1
fi
echo "      ✓ mcp, httpx 已安装"

# 安装 Skill
echo "[2/3] 安装 Kiro Skill..."
SKILL_DIR="$HOME/.kiro/skills/grafana-loki-logs"
mkdir -p "$SKILL_DIR"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cp "$SCRIPT_DIR/SKILL.md" "$SKILL_DIR/SKILL.md"
echo "      ✓ Skill 已安装到 $SKILL_DIR"

# 提示配置
echo "[3/3] 配置 MCP Server..."
echo ""
echo "============================================"
echo "  请手动完成以下配置："
echo "============================================"
echo ""
echo "  1. 打开 .kiro/settings/mcp.json"
echo "  2. 添加以下配置（替换 <...> 部分）："
echo ""
cat << 'EOF'
  "grafana-loki": {
    "command": "python3",
    "args": ["<下载路径>/server.py"],
    "env": {
      "GRAFANA_URL": "<你的Grafana地址>",
      "GRAFANA_SESSION": "<你的Session Cookie>",
      "GRAFANA_ORG_ID": "<组织ID>",
      "LOKI_DATASOURCE_UID": "<Loki数据源UID>",
      "LOKI_DATASOURCE_ID": "<Loki数据源ID>"
    },
    "disabled": false,
    "autoApprove": ["query_logs","query_logs_volume","query_log_context","list_services","list_label_values","query_logs_by_logql"]
  }
EOF
echo ""
echo "============================================"
echo "  获取配置参数的方法："
echo "  - 登录 Grafana，F12 打开 DevTools"
echo "  - Cookies 中找 grafana_session"
echo "  - Explore 页面查看网络请求中的 datasource uid/id"
echo "============================================"
echo ""
echo "安装完成！重启 Kiro 后即可使用。"
