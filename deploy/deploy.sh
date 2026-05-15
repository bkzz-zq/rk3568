#!/bin/bash
#===============================================================================
# RK3568 智能视觉识别系统 - 一键部署脚本
# 适用于 Ubuntu 系统，所有下载使用国内镜像源
#
# 使用方法:
#   sudo chmod +x deploy.sh
#   sudo ./deploy.sh
#===============================================================================

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info()  { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn()  { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_step()  { echo -e "\n${BLUE}==== $1 ====${NC}"; }

# 项目目录（脚本所在目录的上级）
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
VENV_DIR="$PROJECT_DIR/.venv"

echo "================================================"
echo "  RK3568 智能视觉识别系统 - 一键部署"
echo "================================================"
echo "项目目录: $PROJECT_DIR"
echo "虚拟环境: $VENV_DIR"
echo "================================================"

# 检查是否 root
if [ "$EUID" -ne 0 ]; then
    log_error "请使用 sudo 运行此脚本"
    exit 1
fi

#===============================================================================
# 第 1 步: 配置国内镜像源
#===============================================================================
log_step "第 1 步: 配置国内镜像源"

# 备份原始 sources.list
if [ ! -f /etc/apt/sources.list.bak ]; then
    cp /etc/apt/sources.list /etc/apt/sources.list.bak
    log_info "已备份 /etc/apt/sources.list"
fi

# 检测 Ubuntu 版本
UBUNTU_CODENAME=$(lsb_release -cs 2>/dev/null || echo "focal")
log_info "系统版本: Ubuntu $(lsb_release -rs 2>/dev/null) ($UBUNTU_CODENAME)"

# 配置阿里云镜像源（ARM64 使用 ubuntu-ports）
ARCH=$(dpkg --print-architecture 2>/dev/null || echo "arm64")
if [ "$ARCH" = "arm64" ] || [ "$ARCH" = "aarch64" ]; then
    APT_MIRROR="ubuntu-ports"
else
    APT_MIRROR="ubuntu"
fi
log_info "系统架构: $ARCH, 使用镜像路径: $APT_MIRROR"

if ! grep -q "mirrors.aliyun.com" /etc/apt/sources.list 2>/dev/null; then
    log_info "配置阿里云 apt 镜像源..."
    cat > /etc/apt/sources.list << EOF
deb http://mirrors.aliyun.com/${APT_MIRROR}/ ${UBUNTU_CODENAME} main restricted universe multiverse
deb http://mirrors.aliyun.com/${APT_MIRROR}/ ${UBUNTU_CODENAME}-security main restricted universe multiverse
deb http://mirrors.aliyun.com/${APT_MIRROR}/ ${UBUNTU_CODENAME}-updates main restricted universe multiverse
deb http://mirrors.aliyun.com/${APT_MIRROR}/ ${UBUNTU_CODENAME}-backports main restricted universe multiverse
EOF
    log_info "阿里云镜像源配置完成"
else
    log_info "阿里云镜像源已配置，跳过"
fi

#===============================================================================
# 第 2 步: 更新系统并安装基础依赖
#===============================================================================
log_step "第 2 步: 更新系统并安装基础依赖"

log_info "更新 apt..."
apt-get update -y

log_info "安装基础依赖..."
apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    ffmpeg \
    libopencv-dev \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    wget \
    curl \
    lsb-release \
    net-tools

log_info "基础依赖安装完成"

#===============================================================================
# 第 3 步: 安装 RKNN NPU 运行时
#===============================================================================
log_step "第 3 步: 安装 RKNN NPU 运行时"

# 检查 NPU 驱动
if dmesg | grep -qi "rknpu"; then
    NPU_DRIVER_VERSION=$(dmesg | grep "Initialized rknpu" | grep -oP '\d+\.\d+\.\d+' | head -1)
    log_info "NPU 驱动已加载: v${NPU_DRIVER_VERSION:-未知}"
else
    log_warn "未检测到 NPU 驱动，请确认内核是否支持 NPU"
    log_warn "继续安装，但 NPU 功能可能不可用"
fi

# 检查 librknnrt.so 是否已安装
if [ -f /usr/lib/librknnrt.so ]; then
    log_info "librknnrt.so 已安装，跳过"
else
    log_info "安装 RKNN 运行时库 (librknnrt.so)..."
    log_warn "===================================================="
    log_warn "  需要手动安装 librknnrt.so"
    log_warn "===================================================="
    log_warn "请从以下途径获取 librknnrt.so:"
    log_warn "  1. Rockchip 官方 SDK: rknn-toolkit2"
    log_warn "  2. 下载地址: https://github.com/rockchip-linux/rknpu2"
    log_warn "  3. 路径: rknpu2/runtime/Linux/librknn_api/aarch64/librknnrt.so"
    log_warn ""
    log_warn "安装方法:"
    log_warn "  cp librknnrt.so /usr/lib/"
    log_warn "  ldconfig"
    log_warn "===================================================="

    # 尝试从 GitHub 下载（国内可能需要代理）
    RKNNRT_URL="https://github.com/rockchip-linux/rknpu2/raw/master/runtime/Linux/librknn_api/aarch64/librknnrt.so"
    log_info "尝试下载 librknnrt.so..."
    if wget --timeout=30 -O /usr/lib/librknnrt.so "$RKNNRT_URL" 2>/dev/null; then
        chmod +x /usr/lib/librknnrt.so
        ldconfig
        log_info "librknnrt.so 下载安装成功"
    else
        log_warn "自动下载失败，请手动安装 librknnrt.so"
        log_warn "脚本继续执行，后续安装 rknnlite2 后再配置"
    fi
fi

#===============================================================================
# 第 4 步: 创建 Python 虚拟环境
#===============================================================================
log_step "第 4 步: 创建 Python 虚拟环境"

PYTHON_VERSION=$(python3 --version 2>&1 | grep -oP '\d+\.\d+')
log_info "Python 版本: $PYTHON_VERSION"

if [ -d "$VENV_DIR" ]; then
    log_info "虚拟环境已存在，跳过创建"
else
    log_info "创建虚拟环境..."
    python3 -m venv "$VENV_DIR"
    log_info "虚拟环境创建完成"
fi

# 激活虚拟环境
source "$VENV_DIR/bin/activate"

# 配置 pip 国内镜像源
log_info "配置 pip 清华大学镜像源..."
mkdir -p ~/.pip
cat > ~/.pip/pip.conf << 'EOF'
[global]
index-url = https://pypi.tuna.tsinghua.edu.cn/simple
trusted-host = pypi.tuna.tsinghua.edu.cn
EOF

log_info "pip 镜像源配置完成"

#===============================================================================
# 第 5 步: 安装 Python 依赖
#===============================================================================
log_step "第 5 步: 安装 Python 依赖"

log_info "升级 pip..."
pip install --upgrade pip

log_info "安装核心依赖..."
pip install --no-cache-dir \
    numpy \
    opencv-python-headless \
    pyyaml \
    websockets

log_info "核心依赖安装完成"

#===============================================================================
# 第 6 步: 安装 RKNNLite2
#===============================================================================
log_step "第 6 步: 安装 RKNNLite2"

if [ -f /usr/lib/librknnrt.so ]; then
    log_info "安装 rknnlite2..."
    pip install --no-cache-dir rknnlite2 || {
        log_warn "pip 安装 rknnlite2 失败，尝试从 GitHub 安装..."
        pip install --no-cache-dir \
            https://github.com/rockchip-linux/rknpu2/raw/master/runtime/Linux/librknn_api/aarch64/rknnlite2-2.0.0b0-cp39-cp39-linux_aarch64.whl 2>/dev/null || {
            log_error "rknnlite2 安装失败，请手动安装"
            log_error "下载地址: https://github.com/rockchip-linux/rknpu2"
        }
    }
else
    log_warn "librknnrt.so 未安装，跳过 rknnlite2 安装"
    log_warn "请先安装 librknnrt.so，然后运行: pip install rknnlite2"
fi

#===============================================================================
# 第 7 步: 安装 AI 推理库
#===============================================================================
log_step "第 7 步: 安装 AI 推理库 (PaddleOCR + HyperLPR3)"

# 安装 PaddlePaddle ARM 版
log_info "安装 PaddlePaddle (ARM64 版本)..."
log_info "注意: PaddlePaddle ARM 版本需要从百度镜像下载"

# 尝试安装 paddlepaddle（ARM 版）
pip install --no-cache-dir paddlepaddle || {
    log_warn "paddlepaddle 安装失败，尝试指定版本..."
    pip install --no-cache-dir \
        -i https://mirror.baidu.com/pypi/simple/ \
        paddlepaddle==2.5.2 || {
        log_error "PaddlePaddle 安装失败"
        log_error "请参考 https://www.paddlepaddle.org.cn/ 安装 ARM 版本"
    }
}

# 安装 PaddleOCR
log_info "安装 PaddleOCR..."
pip install --no-cache-dir paddleocr || {
    log_warn "PaddleOCR 安装失败，尝试百度镜像..."
    pip install --no-cache-dir \
        -i https://mirror.baidu.com/pypi/simple/ \
        paddleocr
}

# 安装 HyperLPR3（车牌识别）
log_info "安装 HyperLPR3..."
pip install --no-cache-dir hyperlpr3 || {
    log_warn "HyperLPR3 安装失败，尝试百度镜像..."
    pip install --no-cache-dir \
        -i https://mirror.baidu.com/pypi/simple/ \
        hyperlpr3
}

log_info "AI 推理库安装完成"

#===============================================================================
# 第 8 步: 验证安装
#===============================================================================
log_step "第 8 步: 验证安装"

log_info "检查 Python 依赖..."
python3 "$PROJECT_DIR/src/npu/rknn_helper.py" 2>/dev/null || {
    log_warn "系统检查脚本执行失败（部分依赖可能未安装）"
}

# 简单验证
VALIDATE_SCRIPT="
import sys
deps = [
    ('numpy', 'NumPy'),
    ('cv2', 'OpenCV'),
    ('yaml', 'PyYAML'),
    ('websockets', 'WebSockets'),
]
ai_deps = [
    ('rknnlite.api', 'RKNNLite2'),
    ('paddleocr', 'PaddleOCR'),
    ('hyperlpr3', 'HyperLPR3'),
]

print('=== 核心依赖 ===')
for mod, name in deps:
    try:
        __import__(mod)
        print(f'  ✓ {name}')
    except ImportError:
        print(f'  ✗ {name}')

print('=== AI 依赖 ===')
for mod, name in ai_deps:
    try:
        __import__(mod)
        print(f'  ✓ {name}')
    except ImportError:
        print(f'  ✗ {name} (未安装)')
"

python3 -c "$VALIDATE_SCRIPT"

#===============================================================================
# 第 9 步: 配置 systemd 服务（可选）
#===============================================================================
log_step "第 9 步: 配置 systemd 开机自启服务"

SERVICE_FILE="/etc/systemd/system/rk3568-vision.service"
if [ -f "$SERVICE_FILE" ]; then
    log_info "systemd 服务已存在，跳过"
else
    log_info "安装 systemd 服务..."
    cp "$SCRIPT_DIR/rk3568.service" "$SERVICE_FILE" 2>/dev/null || {
        # 如果服务文件不存在，直接创建
        cat > "$SERVICE_FILE" << SERVICEEOF
[Unit]
Description=RK3568 Smart Vision Detection System
After=network.target
Wants=network-online.target

[Service]
Type=simple
User=root
WorkingDirectory=$PROJECT_DIR
ExecStart=$VENV_DIR/bin/python3 $PROJECT_DIR/src/main.py
ExecStop=/bin/kill -SIGTERM \$MAINPID
Restart=on-failure
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
SERVICEEOF
    }

    systemctl daemon-reload
    log_info "systemd 服务安装完成"
    log_info "启动服务: sudo systemctl start rk3568-vision"
    log_info "开机自启: sudo systemctl enable rk3568-vision"
    log_info "查看日志: sudo journalctl -u rk3568-vision -f"
fi

#===============================================================================
# 部署完成
#===============================================================================
echo ""
echo "================================================"
log_info "🎉 部署完成！"
echo "================================================"
echo ""
echo "下一步操作:"
echo ""
echo "  1. 检查配置文件:"
echo "     vi $PROJECT_DIR/config/config.yaml"
echo ""
echo "  2. 手动运行测试:"
echo "     cd $PROJECT_DIR"
echo "     source .venv/bin/activate"
echo "     python3 src/main.py"
echo ""
echo "  3. 启动后台服务:"
echo "     sudo systemctl start rk3568-vision"
echo "     sudo systemctl enable rk3568-vision  # 开机自启"
echo ""
echo "  4. 查看运行日志:"
echo "     sudo journalctl -u rk3568-vision -f"
echo ""
echo "  5. PC 端连接:"
echo "     python pc_client/client.py --host <RK3568的IP>"
echo ""
echo "================================================"