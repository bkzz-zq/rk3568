#!/bin/bash
#===============================================================================
# RK3568 智能视觉识别系统 - 启动脚本
#===============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
VENV_DIR="$PROJECT_DIR/.venv"

# 检查虚拟环境
if [ ! -d "$VENV_DIR" ]; then
    echo "[ERROR] 虚拟环境不存在，请先运行部署脚本: sudo ./deploy.sh"
    exit 1
fi

# 激活虚拟环境
source "$VENV_DIR/bin/activate"

cd "$PROJECT_DIR"

echo "================================================"
echo "  RK3568 智能视觉识别系统 - 启动"
echo "================================================"
echo "项目目录: $PROJECT_DIR"
echo "Python: $(which python3)"
echo "================================================"

# 传递所有命令行参数
python3 src/main.py "$@"