#!/bin/bash
#===============================================================================
# RK3568 智能视觉识别系统 - 停止脚本
#===============================================================================

echo "================================================"
echo "  RK3568 智能视觉识别系统 - 停止"
echo "================================================"

# 停止 systemd 服务（如果在使用）
if systemctl is-active --quiet rk3568-vision 2>/dev/null; then
    echo "[INFO] 停止 systemd 服务..."
    sudo systemctl stop rk3568-vision
    echo "[INFO] systemd 服务已停止"
fi

# 查找并停止手动运行的进程
PIDS=$(pgrep -f "python3.*src/main.py" 2>/dev/null)
if [ -n "$PIDS" ]; then
    echo "[INFO] 发现运行中的进程: $PIDS"
    for PID in $PIDS; do
        echo "[INFO] 停止进程 $PID..."
        kill -SIGTERM "$PID" 2>/dev/null
    done

    # 等待进程退出
    sleep 2

    # 检查是否还在运行
    PIDS=$(pgrep -f "python3.*src/main.py" 2>/dev/null)
    if [ -n "$PIDS" ]; then
        echo "[WARN] 进程未响应，强制终止..."
        for PID in $PIDS; do
            kill -9 "$PID" 2>/dev/null
        done
    fi
    echo "[INFO] 进程已停止"
else
    echo "[INFO] 未发现运行中的进程"
fi

echo "================================================"