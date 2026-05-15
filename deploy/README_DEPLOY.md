# RK3568 部署指南

## 环境要求

| 项目 | 要求 |
|------|------|
| 硬件 | RK3568 核心板（佩特电子） |
| 系统 | Ubuntu 20.04 / 22.04 (aarch64) |
| Python | 3.8+ |
| 网络 | 与摄像头（192.168.0.66）同一局域网 |
| NPU 驱动 | rknpu 内核驱动已加载 |

## 快速部署

### 1. 传输项目到 RK3568

```bash
# 在 PC 上执行（将整个项目传到板子）
scp -r rk3568/ root@<RK3568_IP>:/opt/rk3568
```

### 2. 一键部署

```bash
# SSH 登录 RK3568
ssh root@<RK3568_IP>

# 进入部署目录
cd /opt/rk3568/deploy

# 添加执行权限
chmod +x deploy.sh start.sh stop.sh

# 执行一键部署（约 10-20 分钟）
sudo ./deploy.sh
```

部署脚本会自动完成：
- ✅ 配置阿里云 apt 镜像源
- ✅ 安装系统依赖（ffmpeg, libopencv 等）
- ✅ 下载并安装 RKNN NPU 运行时（librknnrt.so）
- ✅ 创建 Python 虚拟环境
- ✅ 配置清华大学 pip 镜像源
- ✅ 安装核心依赖（numpy, opencv, websockets）
- ✅ 安装 RKNNLite2
- ✅ 安装 PaddleOCR + PaddlePaddle (ARM版)
- ✅ 安装 HyperLPR3（车牌识别）
- ✅ 注册 systemd 开机自启服务

### 3. 配置修改

```bash
# 编辑配置文件（根据实际环境修改）
vi /opt/rk3568/config/config.yaml
```

需要确认的配置：
- **camera.rtsp**: 摄像头 RTSP 地址
- **websocket.host**: 默认 `0.0.0.0`（允许外部连接）
- **websocket.port**: 默认 `8765`

### 4. 运行测试

```bash
# 手动启动（前台运行，可看到日志输出）
cd /opt/rk3568/deploy
./start.sh

# 或使用指定参数
./start.sh --no-npu          # 不使用 NPU
./start.sh --no-person       # 不使用行人检测
./start.sh --no-plate        # 不使用车牌识别
./start.sh --no-ocr          # 不使用文字识别
```

### 5. PC 端连接

```bash
# 在 PC 上运行客户端
cd rk3568
.venv\Scripts\python.exe pc_client/client.py --host <RK3568_IP>
```

## 后台服务管理

```bash
# 启动后台服务
sudo systemctl start rk3568-vision

# 停止后台服务
sudo systemctl stop rk3568-vision

# 查看运行状态
sudo systemctl status rk3568-vision

# 设置开机自启
sudo systemctl enable rk3568-vision

# 取消开机自启
sudo systemctl disable rk3568-vision

# 实时查看日志
sudo journalctl -u rk3568-vision -f

# 查看最近 100 行日志
sudo journalctl -u rk3568-vision -n 100
```

## 手动安装（如果一键部署失败）

### 安装 NPU 运行时

```bash
# 从 rknpu2 仓库获取
wget https://github.com/rockchip-linux/rknpu2/raw/master/runtime/Linux/librknn_api/aarch64/librknnrt.so
sudo cp librknnrt.so /usr/lib/
sudo ldconfig
```

### 安装 Python 依赖

```bash
cd /opt/rk3568
python3 -m venv .venv
source .venv/bin/activate

# 配置清华镜像
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

# 核心依赖
pip install numpy opencv-python-headless pyyaml websockets

# RKNN
pip install rknnlite2

# AI 库
pip install paddlepaddle paddleocr hyperlpr3
```

## NPU 驱动检查

```bash
# 检查 NPU 内核驱动是否加载
dmesg | grep -i rknpu

# 正常输出示例:
# [  4.234286] [drm] Initialized rknpu 0.9.0 20230629 for fde40000.npu on minor 1

# 检查 RKNN 运行时是否可用
python3 -c "from rknnlite.api import RKNNLite; rknn = RKNNLite(); print('NPU OK')"
```

## 模型文件准备

### YOLOv8 行人检测（RKNN 格式）

需要在 PC 上转换模型：

```bash
# 1. 安装 rknn-toolkit2（PC 端）
pip install rknn-toolkit2

# 2. 下载 YOLOv8 模型
pip install ultralytics
yolo export model=yolov8n.pt format=onnx

# 3. 转换为 RKNN
python3 -c "
from src.npu.rknn_helper import RKNNHelper
RKNNHelper.convert_yolo_to_rknn('models/yolov8n.onnx', target='rk3568')
"

# 4. 传到板子
scp models/yolov8n.rknn root@<RK3568_IP>:/opt/rk3568/models/
```

### 车牌/文字识别

PaddleOCR 和 HyperLPR3 首次运行会自动下载模型，无需手动操作。

## 常见问题

### Q: librknnrt.so 下载失败
GitHub 在国内访问可能较慢，可以：
1. 手动从 Gitee 镜像下载
2. 从 Rockchip 官方 SDK 获取
3. 联系板卡厂商获取

### Q: PaddlePaddle ARM 版安装失败
```bash
# 尝试百度官方源
pip install paddlepaddle -i https://mirror.baidu.com/pypi/simple/

# 或参考官方文档
# https://www.paddlepaddle.org.cn/install/quick
```

### Q: OpenCV 无法打开 RTSP 流
```bash
# 检查 ffmpeg 是否安装
ffmpeg -version

# 测试 RTSP 连接
ffprobe "rtsp://admin:sdxyp123@192.168.0.66:554/Streaming/Channels/201"
```

### Q: 内存不足
```bash
# 检查内存使用
free -h

# 如果内存不足，可以：
# 1. 使用子码流（config.yaml 中 use_stream: "sub"）
# 2. 降低帧率（fps_limit: 10）
# 3. 关闭部分检测模块
```

### Q: 查看板子 IP 地址
```bash
ip addr show | grep "inet " | grep -v 127.0.0.1