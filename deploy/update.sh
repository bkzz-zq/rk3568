#!/bin/bash
# RK3568 板子端一键更新脚本
# 用法: bash deploy/update.sh 或 ssh root@192.168.0.100 "cd /opt/rk3568 && bash deploy/update.sh"

set -e

echo "=========================================="
echo " RK3568 智能视觉系统 - 代码更新"
echo "=========================================="

cd /opt/rk3568

echo "[1/3] 拉取最新代码..."
git pull origin main

echo "[2/3] 安装依赖（如有变化）..."
if [ -f requirements.txt ]; then
    pip install -r requirements.txt -q 2>/dev/null || true
fi

echo "[3/3] 检查模型文件..."
mkdir -p models
if [ ! -f models/yolov8n.rknn ]; then
    echo "⚠️  YOLOv8 RKNN 模型不存在，需要手动上传: models/yolov8n.rknn"
fi

echo ""
echo "✅ 更新完成！"
echo "启动服务: cd /opt/rk3568 && python3 src/main.py --no-ocr"
echo "或使用 systemd: systemctl restart rk3568-vision"