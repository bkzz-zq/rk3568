# Bug 排查与修复记录

> 记录开发过程中遇到的所有 bug、排查过程和解决方案。

---

## Bug 1: paho-mqtt 2.x 兼容性错误

### 现象
```
TypeError: __init__() missing 1 required positional argument: 'callback_api_version'
```

### 原因
pip 安装了 paho-mqtt 2.x，其 API 与 1.x 不兼容。`Client()` 构造函数新增了 `callback_api_version` 必填参数。

### 解决方案
在创建 Client 时兼容两个版本：

```python
import paho.mqtt.client as mqtt

try:
    from paho.mqtt.enums import CallbackAPIVersion
    client = mqtt.Client(callback_api_version=CallbackAPIVersion.VERSION1)
except ImportError:
    client = mqtt.Client()
```

### 涉及文件
- `src/iot/mqtt_client.py`

---

## Bug 2: main.py running 变量作用域错误

### 现象
信号处理函数中修改 `running` 变量不生效，导致程序无法正常退出。

### 原因
Python 中 `global` 关键字只能在模块级别使用，不能在嵌套函数中使用 `global` 引用外层函数的局部变量。

### 解决方案
使用 `nonlocal` 替代 `global`（`running` 是 `main()` 函数的局部变量）：

```python
def main():
    running = True

    def signal_handler(sig, frame):
        nonlocal running  # 不是 global
        running = False
```

### 涉及文件
- `src/main.py`

---

## Bug 3: uvicorn 日志配置冲突

### 现象
```
ValueError: Unable to configure formatter 'default'
```

### 原因
uvicorn 默认使用自己的日志配置，与项目自定义的 logging 配置冲突。

### 解决方案
在 `run_server()` 中禁用 uvicorn 默认日志配置：

```python
uvicorn.run(app, host=host, port=port, log_level="warning", log_config=None)
```

`log_config=None` 让 uvicorn 不加载自己的日志配置。

### 涉及文件
- `src/iot/server.py`

---

## Bug 4: systemctl 启动时车牌识别始终为 0

### 现象
- `systemctl start rk3568`：车牌识别始终"识别到 0 个车牌"
- 手动运行 `python3 src/main.py`：正常识别到车牌

### 排查过程

1. **初步猜测**：虚拟环境问题 → 改用 bash 激活 venv 启动 → 无效
2. **分辨率猜测**：640x360 太低 → 添加 2x 上采样 → 无效
3. **环境变量对比**：
   ```bash
   # 获取 systemctl 进程环境
   PID=$(pgrep -f "main.py")
   cat /proc/$PID/environ | tr '\0' '\n' | sort > /tmp/systemctl_env.txt
   # 获取手动运行环境
   env | sort > /tmp/manual_env.txt
   # 对比
   diff /tmp/manual_env.txt /tmp/systemctl_env.txt
   ```
4. **发现差异**：systemctl 环境缺少 `HOME`、`DISPLAY`、GStreamer 等关键环境变量

### 原因
systemd 服务环境变量最小化，缺少 `HOME=/root` 和 GStreamer 相关变量，导致 HyperLPR3 内部的 ONNX Runtime 行为异常。

### 解决方案
在 `rk3568.service` 中添加环境变量：

```ini
Environment=HOME=/root
Environment=DISPLAY=:0
Environment=XDG_RUNTIME_DIR=/run/user/0
Environment=DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/0/bus
Environment=GST_GL_API=gles2
Environment=GST_GL_PLATFORM=egl
Environment=GST_VIDEO_CONVERT_USE_RGA=1
Environment=GST_VIDEO_FLIP_USE_RGA=1
Environment=GST_VIDEO_CONVERT_PREFERRED_FORMAT=NV12:NV16:I420:YUY2
Environment=GST_V4L2_USE_LIBV4L2=1
Environment=GST_MPP_VP8ENC_FAKE_VP8ENC=1
```

### 涉及文件
- `deploy/rk3568.service`

### 教训
> systemd 服务的环境变量与交互式 shell 差异很大。遇到"手动运行正常，systemctl 不正常"的问题时，**第一步就对比环境变量**。

---

## Bug 5: systemctl stop 超时

### 现象
```
State 'stop-sigterm' timed out. Killing.
Main process exited, code=killed, status=9/KILL
Failed with result 'timeout'.
```

### 原因
程序退出时需要释放 NPU 模型、关闭 GStreamer 管道等，默认超时时间（90秒）不够。GStreamer 的 rtpjitterbuffer 线程可能阻塞退出。

### 解决方案
1. 在 service 文件中设置停止超时：

```ini
TimeoutStopSec=30
```

2. 确保信号处理函数正确设置 `running = False`（参见 Bug 2）

### 涉及文件
- `deploy/rk3568.service`
- `src/main.py`

---

## Bug 6: MJPEG 视频流帧率低

### 现象
浏览器访问 `/video/stream` 帧率很低，画面卡顿。

### 原因
初始实现中使用 `async def` 生成器 + `run_in_executor` + `time.sleep(0.1)`，async 开销 + sleep 导致帧率只有 ~5fps。

### 解决方案
1. 改回同步生成器（`def generate()`），Starlette 会自动在线程中运行
2. 去掉 `time.sleep`，让帧率由编码速度自然决定
3. 去掉 `frame.copy()`，直接在帧上画检测框
4. 去掉不必要的 resize

```python
@app.get("/video/stream")
def video_stream():  # 同步，不是 async
    def generate():
        while True:
            frame = _camera.get_frame()
            # 直接画框（不 copy）
            # 编码 JPEG
            yield (b"--frame\r\n" ...)
            # 不 sleep
    return StreamingResponse(generate(), ...)
```

### 涉及文件
- `src/iot/server.py`

---

## Bug 7: 车牌识别检测率低

### 现象
即使环境正常，车牌识别也只有约 15% 的检测率（每 7 次检测到 1 次）。

### 原因
1. 子码流分辨率 640x360，车牌太小（约 20-30 像素宽）
2. 检测间隔太长（每 9 帧才检测一次）

### 解决方案
1. 车牌检测前 2x 上采样（640x360 → 1280x720）
2. 减小检测间隔（PLATE_INTERVAL 从 9 改为 3）

```python
PLATE_INTERVAL = 3        # 每 3 帧检测一次
PLATE_UPSAMPLE = 2.0      # 2x 上采样

# 车牌检测前上采样
plate_frame = cv2.resize(frame, None, fx=PLATE_UPSAMPLE, fy=PLATE_UPSAMPLE)
```

### 涉及文件
- `src/main.py`

---

## 常用排查命令

```bash
# 查看 systemctl 服务状态
systemctl status rk3568

# 查看实时日志
journalctl -u rk3568 -f --no-pager

# 过滤车牌相关日志
journalctl -u rk3568 --no-pager | grep "plate_detector"

# 查看进程环境变量
PID=$(pgrep -f "main.py")
cat /proc/$PID/environ | tr '\0' '\n' | sort

# 重启服务
systemctl daemon-reload
systemctl restart rk3568

# 测试 MQTT
mosquitto_sub -t "device/+/property/post" -v
mosquitto_pub -t "device/esp8266/property/post" -m '{"id":"1","params":{"tremp":{"value":25.5}}}'

# 查看 Swagger API 文档
# 浏览器打开 http://192.168.0.100:8000/docs