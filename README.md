# RK3568 智能视觉识别系统

基于佩特 RK3568 核心板 + 海康威视摄像头的实时智能视觉识别系统。

## 功能

- **行人检测**：基于 YOLOv8 + RKNN NPU 实时检测行人
- **车牌识别**：HyperLPR3 检测并识别中国车牌（蓝/黄/绿/白/新能源）
- **文字识别**：基于 PaddleOCR 的通用中英文文字识别
- **实时推送**：WebSocket 将检测框 JSON 推送给 PC 客户端
- **PC 客户端**：RTSP 直连视频 + WebSocket 检测框叠加显示

## 系统架构

```
┌─── RK3568 边缘端（检测服务）───────────────────────────────────────┐
│                                                                    │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐       │
│  │ 线程1: 解码    │     │ 线程2: 检测    │     │ 主线程: 推送   │       │
│  │              │     │              │     │              │       │
│  │ GStreamer    │     │ 取帧(缓存)    │     │ 读结果(缓存)  │       │
│  │   + MPP VPU  │────→│ resize 640px │────→│ WebSocket    │       │
│  │ 硬解码 RTSP   │ 帧缓存│ NPU 行人检测  │ 结果缓存│ JSON 推送    │       │
│  │ 1920x1080    │     │ CPU 车牌识别  │     │ FPS 统计     │       │
│  │              │     │ (并行线程池)   │     │              │       │
│  └──────────────┘     └──────────────┘     └──────┬───────┘       │
│                                                    │               │
└────────────────────────────────────────────────────┼───────────────┘
                                                     │ WebSocket
                                                     │ (JSON 检测框)
                                                     ↓
┌─── PC 接收端 ──────────────────────────────────────────────────────┐
│                                                                    │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐       │
│  │ RTSP 直连     │     │ WebSocket    │     │ OpenCV 显示   │       │
│  │ 摄像头原始画质 │────→│ 接收检测框    │────→│ 检测框叠加    │       │
│  │ 零延迟        │ 视频帧│ 解析 JSON    │ 检测框│ PIL 中文文字  │       │
│  │              │     │              │     │ 可调整窗口    │       │
│  └──────────────┘     └──────────────┘     └──────────────┘       │
│                                                                    │
│  tkinter 连接对话框 → 输入板子 IP / 端口 / RTSP → 配置自动保存       │
└────────────────────────────────────────────────────────────────────┘
```

## 多线程流水线

核心优化：解码、检测、推送三阶段完全解耦，互不阻塞。

```
时间线示意：

线程1(解码):   [帧1][帧2][帧3][帧4][帧5][帧6][帧7][帧8]...  持续 ~40fps
                  ↓ 最新帧覆盖
线程2(检测):   [---行人+NPU---][跳过][跳过][---行人+NPU---]...  每3帧检测一次
               [------车牌CPU----------]......[------车牌CPU----]...  每9帧检测一次
                  ↓ 结果缓存
主线程(推送):  [推送][推送][推送][推送][推送][推送][推送]...     ~40fps 不阻塞
```

| 线程 | 职责 | 频率 | 阻塞？ |
|------|------|------|--------|
| 解码线程 | GStreamer+MPP 硬解码读帧 | ~25fps | 否 |
| 检测线程 | resize + NPU行人 + CPU车牌并行 | 行人:每3帧, 车牌:每9帧 | 否 |
| 主线程 | 读缓存 → WebSocket 推送 | ~40fps | 否 |

## 项目结构

```
rk3568/
├── config/
│   └── config.yaml              # 配置文件（摄像头/检测/NPU/WebSocket）
├── models/                      # 模型文件目录
│   ├── yolov8n.rknn            # YOLOv8 行人检测 (NPU)
│   ├── plate_detect_640.rknn   # 车牌检测 (NPU, 备用)
│   ├── rpv3_mdict_160_r3.onnx  # 车牌号识别 (CPU)
│   └── litemodel_cls_96x_r1.onnx # 车牌颜色分类 (CPU)
├── src/
│   ├── main.py                  # 主入口（多线程流水线）
│   ├── camera.py                # RTSP 视频流（GStreamer+MPP 硬解码）
│   ├── detector/
│   │   ├── person.py            # 行人检测 (YOLOv8 → RKNN NPU)
│   │   ├── plate.py             # 车牌识别 (HyperLPR3 / NPU+ONNX)
│   │   └── ocr.py               # 通用文字识别 (PaddleOCR)
│   ├── pusher/
│   │   └── ws_pusher.py         # WebSocket 推送（仅 JSON）
│   ├── npu/
│   │   └── rknn_helper.py       # RKNN NPU 辅助工具
│   └── utils/
│       ├── config.py            # YAML 配置管理
│       ├── image.py             # 图像处理工具
│       └── logger.py            # 日志模块
├── pc_client/
│   ├── client.py                # PC 接收客户端
│   └── client_config.json       # 客户端连接配置（自动保存，已 gitignore）
├── deploy/
│   ├── deploy.sh                # 一键部署脚本
│   ├── start.sh / stop.sh       # 启停脚本
│   ├── update.sh                # 更新脚本
│   └── rk3568.service           # systemd 服务
├── convert_model.py             # ONNX → RKNN 转换
├── convert_plate_detect.py      # 车牌检测模型转换
├── requirements.txt
└── README.md
```

## 关键模块说明

### camera.py — 视频流模块

```python
# 硬解码 pipeline（自动检测，失败回退软解码）
GStreamer Pipeline:
  rtspsrc → rtph264depay → h264parse → mppvideodec → videoconvert → appsink

# 自动检测流程:
# 1. 检查 OpenCV 是否有 GStreamer 后端
# 2. 检查 mppvideodec 插件是否可用
# 3. 都有 → GStreamer + MPP 硬解码
# 4. 缺一 → 回退 FFmpeg 软解码
```

| 解码模式 | CPU 占用 | 延迟 | 画质 |
|----------|---------|------|------|
| GStreamer + MPP (硬解码) | ~5% | ~5ms | 1080p |
| FFmpeg (软解码) | ~60% | ~50ms | 1080p |

### main.py — 多线程流水线

```
启动顺序:
  1. 加载配置 → 初始化摄像头（GStreamer 硬解码连接）
  2. 加载检测器（NPU 行人 + CPU 车牌）
  3. 启动 WebSocket 推送服务
  4. 启动摄像头读帧线程（线程1）
  5. 启动检测线程（线程2）
  6. 主循环：读缓存 → 推送 → FPS统计

数据流:
  CameraStream._frame  ←→  detection_loop()  ←→  cached_results  ←→  主循环
  (最新帧模式, 不积压)      (ThreadPoolExecutor)    (Lock 保护)
```

### pc_client/client.py — PC 接收客户端

```
架构:
  - 视频：PC 直连摄像头 RTSP（零延迟，原始画质）
  - 检测：RK3568 只发检测框 JSON（极低带宽 ~1KB/帧）
  - 渲染：PC 本地 OpenCV 叠加检测框显示

连接方式:
  方式1: python pc_client/client.py          # 弹出对话框输入 IP
  方式2: python pc_client/client.py --host 192.168.0.100  # 命令行指定
```

## 快速开始

### 1. RK3568 环境配置

```bash
# 创建虚拟环境
cd /opt/rk3568
python3 -m venv .venv
source .venv/bin/activate

# 安装依赖
pip install numpy==1.26.4 pyyaml websockets hyperlpr3 paddleocr paddlepaddle
pip install rknn-toolkit2  # 佩特板子预装

# 替换 OpenCV 为系统版本（支持 GStreamer 硬解码）
pip uninstall opencv-python opencv-python-headless -y
rm -rf .venv/lib/python3.10/site-packages/cv2
ln -sf /usr/lib/python3/dist-packages/cv2 .venv/lib/python3.10/site-packages/cv2
ln -sf /usr/lib/python3/dist-packages/cv2.cpython-310-aarch64-linux-gnu.so .venv/lib/python3.10/site-packages/

# 验证 GStreamer
python3 -c "import cv2; print(cv2.getBuildInformation())" | grep -i gstreamer
# 应显示: GStreamer: YES
```

### 2. 检查 GStreamer + MPP

```bash
# 检查 MPP 硬解码插件
gst-inspect-1.0 mppvideodec
# 应显示 Rockchip MPP video decoder

# 如未安装
apt install gstreamer1.0-plugins-base gstreamer1.0-plugins-good gstreamer1.0-rockchip
```

### 3. 运行系统

```bash
# RK3568 上运行检测服务
python3 src/main.py                    # 全功能模式
python3 src/main.py --no-ocr           # 禁用 OCR（推荐，提升帧率）
python3 src/main.py --no-plate         # 禁用车牌识别
python3 src/main.py --no-npu           # 纯 CPU 模式（调试用）

# PC 上运行客户端
python pc_client/client.py             # 弹出连接对话框
python pc_client/client.py --host 192.168.0.100  # 直接连接
```

### 4. PC 端开发调试

```bash
# 安装依赖
pip install -r requirements.txt
pip install ultralytics paddleocr hyperlpr3 paddlepaddle

# CPU 模式运行（无 NPU）
python src/main.py --no-npu
```

## 配置说明

编辑 `config/config.yaml`：

```yaml
camera:
  main_stream: "rtsp://admin:pass@192.168.0.66:554/Streaming/Channels/101"  # 主码流
  sub_stream: "rtsp://admin:pass@192.168.0.66:554/Streaming/Channels/201"   # 子码流
  use_stream: "sub"           # sub=子码流(推荐), main=主码流
  fps_limit: 15               # 帧率限制
  hw_decode: true             # GStreamer+MPP 硬解码

person_detection:
  enabled: true
  confidence: 0.5             # 检测置信度
  model_path: "models/yolov8n.rknn"

plate_recognition:
  enabled: true
  confidence: 0.5
  roi: [0.1, 0.4, 0.9, 0.95] # ROI 区域 [左,上,右,下] 归一化坐标

websocket:
  host: "0.0.0.0"
  port: 8765
  send_image: false           # 仅发 JSON（推荐，极低带宽）

npu:
  enabled: true
  target: "rk3568"
```

## 模型准备

### YOLOv8 → RKNN 转换

```bash
# 1. 导出 ONNX
pip install ultralytics
yolo export model=yolov8n.pt format=onnx

# 2. 转换 RKNN（需要 rknn-toolkit2，在 PC 上执行）
python convert_model.py
```

### 车牌检测模型（可选）

```bash
python convert_plate_detect.py
```

## 命令行参数

### RK3568 端

```
python src/main.py [OPTIONS]

选项:
  --config PATH      配置文件路径（默认 config/config.yaml）
  --no-npu           禁用 NPU，使用 CPU
  --no-person        禁用行人检测
  --no-plate         禁用车牌识别
  --no-ocr           禁用文字识别
```

### PC 客户端

```
python pc_client/client.py [OPTIONS]

选项:
  --host IP          RK3568 IP 地址（跳过对话框）
  --port PORT        WebSocket 端口（默认 8765）
  --rtsp URL         RTSP 直连地址
```

## 性能参考

### RK3568 端（佩特电子 RK3568 核心板）

| 指标 | 软解码+串行 | 硬解码+流水线 |
|------|-----------|-------------|
| **系统 FPS** | ~3 | ~40 |
| **解码 CPU** | ~60% | ~5%（VPU） |
| **行人检测** | ~200ms (CPU) | ~50ms (NPU) |
| **车牌识别** | ~100ms | ~120ms (CPU) |
| **检测延迟** | ~350ms（串行阻塞） | ~200ms（并行不阻塞） |

### 检测模块耗时

| 模块 | 后端 | 耗时 |
|------|------|------|
| 视频解码 | VPU (GStreamer+MPP) | ~5ms, CPU≈0 |
| 硬件缩放 | videoscale (640x360) | ~3ms, CPU≈0 |
| 行人检测 | NPU (RKNN) | ~50ms |
| 车牌检测 | CPU (HyperLPR3) | ~120ms |
| 车牌号识别 | CPU (ONNX) | ~20ms/个 |
| 文字识别 | CPU (PaddleOCR) | ~150ms |

### 为什么车牌不用 NPU

RK3568 只有 **1 个 NPU**（0.8 TOPS），行人检测和车牌检测无法同时使用。如果两个模型都用 NPU，需要交替加载/卸载，严重拖慢推理。当前策略：NPU 给行人检测（高频），CPU 给车牌识别（低频）。

## 硬件环境

| 组件 | 型号 | 备注 |
|------|------|------|
| 核心板 | 佩特 RK3568 | 4核 A55, NPU 0.8T, VPU |
| 摄像头 | 海康威视 DS-2ZMN0409S3 | RTSP 主/子码流 |
| 网络 | 有线局域网 | 板子/摄像头/PC 同网段 |
| PC | Windows 11 | 接收显示客户端 |

## 后续优化方向

1. **YUV 直输入 NPU**：跳过 videoconvert + resize，省 ~15ms
2. **RGA 硬件缩放**：librga 替代 cv2.resize，CPU 零参与
3. **零拷贝 pipeline**：MPP 解码 → DMA → RGA 缩放 → RKNN 推理
4. **多模型 NPU 调度**：车牌检测也用 NPU（需解决单 NPU 争抢）