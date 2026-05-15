# RK3568 智能视觉识别系统

基于佩特 RK3568 核心板 + 海康威视摄像头的实时智能视觉识别系统。

## 功能

- **行人识别**：基于 YOLOv8 实时检测视频中的行人
- **车牌识别**：检测并识别中国车牌（蓝牌/黄牌/绿牌/白牌/新能源）
- **文字识别**：基于 PaddleOCR 的通用中英文文字识别
- **实时推送**：通过 WebSocket 将识别结果实时推送给 PC 客户端

## 系统架构

```
RK3568 (边缘端)                          PC (接收端)
┌─────────────────────┐                 ┌──────────────────┐
│  海康 RTSP 视频流     │                 │                  │
│       ↓              │   WebSocket     │  接收识别结果      │
│  OpenCV 逐帧抓取     │ ────────────→  │  显示/告警        │
│       ↓              │                 │                  │
│  YOLOv8n (RKNN NPU)  │                 │                  │
│  行人/车辆检测        │                 │                  │
│       ↓              │                 │                  │
│  PaddleOCR / HyperLPR│                 │                  │
│  文字/车牌识别        │                 │                  │
└─────────────────────┘                 └──────────────────┘
```

## 项目结构

```
rk3568/
├── config/
│   └── config.yaml           # 配置文件
├── models/                   # 模型文件目录
├── src/
│   ├── main.py               # 主入口（RK3568 端）
│   ├── camera.py             # RTSP 视频流获取
│   ├── detector/
│   │   ├── person.py         # 行人检测 (YOLOv8)
│   │   ├── plate.py          # 车牌识别 (HyperLPR3/PaddleOCR)
│   │   └── ocr.py            # 通用文字识别 (PaddleOCR)
│   ├── pusher/
│   │   └── ws_pusher.py      # WebSocket 推送
│   ├── npu/
│   │   └── rknn_helper.py    # RKNN NPU 辅助工具
│   └── utils/
│       ├── config.py         # 配置管理
│       ├── image.py          # 图像处理工具
│       └── logger.py         # 日志模块
├── pc_client/
│   └── client.py             # PC 端接收客户端
├── logs/                     # 日志目录
├── requirements.txt
└── README.md
```

## 快速开始

### 1. PC 端开发调试

```bash
# 安装依赖
pip install -r requirements.txt
pip install ultralytics paddleocr hyperlpr3 paddlepaddle

# 运行系统（CPU 模式）
python src/main.py --no-npu
```

### 2. RK3568 部署

```bash
# 在 RK3568 上安装依赖
pip install numpy opencv-python pyyaml websockets
pip install rknnlite2
pip install paddleocr paddlepaddle

# 运行系统（NPU 加速）
python src/main.py
```

### 3. PC 端接收结果

```bash
# 在 PC 上运行客户端，连接 RK3568
python pc_client/client.py --host 192.168.1.100 --port 8765
```

## 配置说明

编辑 `config/config.yaml`：

- **camera**: RTSP 地址、码流选择、帧率限制
- **person_detection**: 行人检测置信度、模型路径
- **plate_recognition**: 车牌识别置信度
- **ocr**: 文字识别语言、阈值
- **npu**: NPU 开关、目标平台
- **websocket**: 推送端口、图片质量、频率

## 模型准备

### YOLOv8 行人检测模型

```bash
# 下载 YOLOv8n 预训练模型
pip install ultralytics
yolo export model=yolov8n.pt format=onnx

# 转换为 RKNN 格式（在 PC 上使用 rknn-toolkit2）
python -c "from src.npu.rknn_helper import RKNNHelper; RKNNHelper.convert_yolo_to_rknn('models/yolov8n.onnx')"
```

### 车牌/文字识别

- HyperLPR3 和 PaddleOCR 首次运行会自动下载模型

## 命令行参数

```
python src/main.py [OPTIONS]

选项:
  --config PATH    配置文件路径
  --no-npu         禁用 NPU，使用 CPU
  --no-person      禁用行人检测
  --no-plate       禁用车牌识别
  --no-ocr         禁用文字识别
```

## 硬件要求

- RK3568 核心板（佩特电子）
- 海康威视 DS-2ZMN0409S3 摄像头
- 网络：RK3568 与摄像头同一局域网
- PC：用于接收和显示识别结果

## 性能参考

| 模块 | CPU 模式 | NPU 模式 |
|------|---------|---------|
| 行人检测 (YOLOv8n) | ~200ms | ~30ms |
| 车牌识别 | ~100ms | ~20ms |
| 文字识别 (PaddleOCR) | ~150ms | ~40ms |