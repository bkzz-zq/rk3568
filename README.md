# RK3568 智能视觉识别系统

基于佩特 RK3568 核心板 + 海康威视摄像头的实时智能视觉识别系统，集成智能家居 IoT 服务器。

## 功能

- **行人检测**：基于 YOLOv8 + RKNN NPU 实时检测行人
- **车牌识别**：HyperLPR3 检测并识别中国车牌（蓝/黄/绿/白/新能源）
- **实时推送**：WebSocket 将检测框 JSON 推送给 PC 客户端
- **PC 客户端**：RTSP 直连视频 + WebSocket 检测框叠加显示
- **智能家居服务器**：FastAPI + MQTT 替代 OneNET 云服务器
- **用户管理**：JWT 认证，管理员 API，CLI 管理工具
- **内网穿透**：cpolar 支持外网 App 访问

## 系统架构

```
┌─── RK3568 边缘端（检测服务 + IoT 服务器）──────────────────────────────┐
│                                                                        │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐           │
│  │ 线程1: 解码    │     │ 线程2: 检测    │     │ 主线程: 推送   │           │
│  │              │     │              │     │              │           │
│  │ GStreamer    │     │ 取帧(缓存)    │     │ 读结果(缓存)  │           │
│  │   + MPP VPU  │────→│ resize 640px │────→│ WebSocket    │           │
│  │ 硬解码 RTSP   │ 帧缓存│ NPU 行人检测  │ 结果缓存│ JSON 推送    │           │
│  │ 1920x1080    │     │ CPU 车牌识别  │     │ FPS 统计     │           │
│  │              │     │ (并行线程池)   │     │              │           │
│  └──────────────┘     └──────────────┘     └──────┬───────┘           │
│                                                    │                   │
│  ┌─────────────────────────────────────────────────┼─────────────┐     │
│  │ 智能家居 IoT 服务                                │             │     │
│  │                                                 │             │     │
│  │  FastAPI (8000)  ←── cpolar 穿透 ──→ 手机 App   │             │     │
│  │  ├─ 用户认证 (JWT)                               │             │     │
│  │  ├─ 设备状态查询 / 控制                           │             │     │
│  │  ├─ AI 检测结果                                  │← AI 结果 ──┘     │
│  │  └─ 传感器历史数据                               │                   │
│  │                                                 │                   │
│  │  MQTT (1883) ←─ mosquitto broker ─→ STM32F407   │                   │
│  └─────────────────────────────────────────────────┼─────────────┘     │
│                                                    │ WebSocket         │
└────────────────────────────────────────────────────┼───────────────────┘
                                                     │ (JSON 检测框)
                                                     ↓
┌─── PC 接收端 ──────────────────────────────────────────────────────────┐
│                                                                        │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐           │
│  │ RTSP 直连     │     │ WebSocket    │     │ OpenCV 显示   │           │
│  │ 摄像头原始画质 │────→│ 接收检测框    │────→│ 检测框叠加    │           │
│  │ 零延迟        │ 视频帧│ 解析 JSON    │ 检测框│ PIL 中文文字  │           │
│  └──────────────┘     └──────────────┘     └──────────────┘           │
└────────────────────────────────────────────────────────────────────────┘
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
| 主线程 | 读缓存 → WebSocket 推送 → IoT 同步 | ~40fps | 否 |

## 项目结构

```
rk3568/
├── config/
│   └── config.yaml              # 配置文件（摄像头/检测/NPU/WebSocket/IoT）
├── models/                      # 模型文件目录
│   ├── yolov8n.rknn            # YOLOv8 行人检测 (NPU)
│   ├── plate_detect_640.rknn   # 车牌检测 (NPU, 备用)
│   ├── rpv3_mdict_160_r3.onnx  # 车牌号识别 (CPU)
│   └── litemodel_cls_96x_r1.onnx # 车牌颜色分类 (CPU)
├── src/
│   ├── main.py                  # 主入口（多线程流水线 + IoT）
│   ├── camera.py                # RTSP 视频流（GStreamer+MPP 硬解码）
│   ├── detector/
│   │   ├── person.py            # 行人检测 (YOLOv8 → RKNN NPU)
│   │   └── plate.py             # 车牌识别 (HyperLPR3 / NPU+ONNX)
│   ├── iot/
│   │   ├── server.py            # FastAPI 智能家居服务器
│   │   └── mqtt_client.py       # MQTT 客户端（桥接 FastAPI ↔ STM32）
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
│   ├── rk3568.service           # systemd 服务
│   └── mosquitto.conf           # MQTT broker 配置
├── manage.py                    # 用户管理 CLI 工具
├── convert_model.py             # ONNX → RKNN 转换
├── convert_plate_detect.py      # 车牌检测模型转换
├── requirements.txt
└── README.md
```

## 快速开始

### 1. RK3568 环境配置

```bash
# 创建虚拟环境
cd /opt/rk3568
python3 -m venv .venv
source .venv/bin/activate

# 安装核心依赖
pip install numpy pyyaml websockets hyperlpr3
pip install rknn-toolkit2  # 佩特板子预装

# 安装 IoT 依赖
pip install fastapi uvicorn paho-mqtt PyJWT

# 替换 OpenCV 为系统版本（支持 GStreamer 硬解码）
pip uninstall opencv-python opencv-python-headless -y
rm -rf .venv/lib/python3.10/site-packages/cv2
ln -sf /usr/lib/python3/dist-packages/cv2 .venv/lib/python3.10/site-packages/cv2
ln -sf /usr/lib/python3/dist-packages/cv2.cpython-310-aarch64-linux-gnu.so .venv/lib/python3.10/site-packages/

# 验证 GStreamer
python3 -c "import cv2; print(cv2.getBuildInformation())" | grep -i gstreamer
# 应显示: GStreamer: YES
```

### 2. 安装 MQTT Broker

```bash
apt install mosquitto
cp deploy/mosquitto.conf /etc/mosquitto/conf.d/smart_home.conf
systemctl restart mosquitto
```

### 3. 安装内网穿透（cpolar）

```bash
# 安装
curl -L https://www.cpolar.com/static/downloads/install-release-cpolar.sh | sudo bash

# 认证（去 https://dashboard.cpolar.com 注册获取 token）
cpolar authtoken <你的token>

# 启动穿透
cpolar http 8000

# 设为开机自启
systemctl enable cpolar
systemctl start cpolar
```

### 4. 注册系统服务（开机自启）

```bash
cp deploy/rk3568.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable rk3568
systemctl start rk3568
```

### 5. PC 端开发调试

```bash
# 安装依赖
pip install -r requirements.txt
pip install ultralytics hyperlpr3

# CPU 模式运行（无 NPU）
python src/main.py --no-npu

# PC 客户端
python pc_client/client.py --host 192.168.0.100
```

## 服务管理命令

### systemctl 常用操作

```bash
# 查看所有服务状态
systemctl status rk3568 cpolar mosquitto

# 启动/停止/重启
systemctl start rk3568
systemctl stop rk3568
systemctl restart rk3568       # 修改代码后执行

# 查看实时日志
journalctl -u rk3568 -f --no-pager

# 查看最近 50 行日志
journalctl -u rk3568 -n 50 --no-pager
```

### 修改代码后更新

```bash
# 1. Windows 上传文件
scp src/main.py root@192.168.0.100:/opt/rk3568/src/main.py

# 2. 重启服务
systemctl restart rk3568

# 3. 查看日志确认
journalctl -u rk3568 -f
```

### 用户管理 CLI

```bash
cd /opt/rk3568
source .venv/bin/activate

# 创建管理员
python manage.py create-admin <用户名> <密码>

# 创建普通用户
python manage.py create-user <用户名> <密码>

# 列出所有用户
python manage.py list-users

# 删除用户
python manage.py delete-user <用户名>

# 修改密码
python manage.py change-password <用户名> <新密码>

# 启用/禁用用户
python manage.py toggle-active <用户名>
```

默认管理员：`admin / admin123`（首次启动自动创建）

### API 测试

```bash
# 登录获取 token
curl -X POST http://localhost:8000/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# 查询设备状态
curl http://localhost:8000/thingmodel/query-device-property \
  -H "Authorization: Bearer <TOKEN>"

# 控制设备
curl -X POST http://localhost:8000/thingmodel/set-device-property \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"device_name":"esp8266","params":{"led":true}}'

# AI 检测结果
curl http://localhost:8000/api/ai/detection \
  -H "Authorization: Bearer <TOKEN>"

# 模拟 STM32 发送传感器数据
mosquitto_pub -t "device/esp8266/property/post" \
  -m '{"id":"1","params":{"tremp":{"value":25.5},"hum":{"value":60}}}'
```

### API 文档

浏览器打开 `http://192.168.0.100:8000/docs`（Swagger UI）

## 配置说明

编辑 `config/config.yaml`：

```yaml
camera:
  main_stream: "rtsp://admin:pass@192.168.0.66:554/Streaming/Channels/101"
  sub_stream: "rtsp://admin:pass@192.168.0.66:554/Streaming/Channels/201"
  use_stream: "sub"
  fps_limit: 15
  hw_decode: true

person_detection:
  enabled: true
  confidence: 0.5
  model_path: "models/yolov8n.rknn"

plate_recognition:
  enabled: true
  confidence: 0.5
  roi: [0.1, 0.4, 0.9, 0.95]

iot:
  enabled: true
  mqtt:
    host: "127.0.0.1"
    port: 1883
  server:
    host: "0.0.0.0"
    port: 8000
  sensor_collect_interval: 180

websocket:
  host: "0.0.0.0"
  port: 8765
  send_image: false

npu:
  enabled: true
  target: "rk3568"
```

## 智能家居 API 接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/login` | POST | 用户登录 |
| `/api/verify-token` | POST | 验证 Token |
| `/api/admin/create-user` | POST | 创建用户（管理员） |
| `/api/admin/users` | GET | 用户列表（管理员） |
| `/api/admin/users/{id}` | DELETE | 删除用户（管理员） |
| `/api/admin/users/{id}/toggle-active` | PUT | 启用/禁用用户 |
| `/api/admin/users/{id}/change-password` | PUT | 修改用户密码 |
| `/thingmodel/query-device-property` | GET | 查询设备属性 |
| `/thingmodel/set-device-property` | POST | 控制设备 |
| `/api/sensor-data` | GET | 传感器历史数据 |
| `/api/ai/detection` | GET | AI 视觉检测结果 |
| `/health` | GET | 健康检查 |

所有 API（除登录外）需要 JWT Token 认证。

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

### 为什么车牌不用 NPU

RK3568 只有 **1 个 NPU**（0.8 TOPS），行人检测和车牌检测无法同时使用。当前策略：NPU 给行人检测（高频），CPU 给车牌识别（低频）。

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