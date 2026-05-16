# 车牌检测 NPU 加速方案 - 完整操作指南

> 目标：将 HyperLPR3 的车牌检测模型转为 RKNN 格式，用 NPU 加速检测（~500ms → ~30ms）
> 
> ⚠️ **当前状态**：因 RK3568 只有单 NPU（0.8 TOPS），车牌 NPU 模式与行人检测冲突。
> 当前使用 HyperLPR3 CPU 模式（~120ms），待后续支持多模型 NPU 调度后启用。

---

## 架构对比

### 当前方案（HyperLPR3 端到端，CPU）
```
frame → HyperLPR3 检测+识别（CPU ~500ms）→ 车牌结果
```

### 优化后方案（NPU 检测 + CPU 识别）
```
frame → y5fu_640x RKNN 检测（NPU ~10ms）→ 裁剪车牌
     → rpv3_mdict ONNX 识别（CPU ~20ms）→ 车牌号+颜色
总耗时: ~30ms
```

---

## Step 1：从板子下载 ONNX 模型

### 方法 A：SCP 下载（推荐）

```powershell
# 在 PC PowerShell 中执行
cd d:\VsSlave\Python_code\rk3568

# 下载检测模型（3.9MB）
scp root@192.168.0.100:/root/.hyperlpr3/20230229/onnx/y5fu_640x_sim.onnx ./models/

# 下载识别模型（10MB，可选，后续集成用）
scp root@192.168.0.100:/root/.hyperlpr3/20230229/onnx/rpv3_mdict_160_r3.onnx ./models/

# 下载颜色分类模型（1.6MB，可选）
scp root@192.168.0.100:/root/.hyperlpr3/20230229/onnx/litemodel_cls_96x_r1.onnx ./models/
```

### 方法 B：板子启动 HTTP 服务器

```bash
# 在板子上执行（Ctrl+C 停止）
python3 -m http.server 8888 --directory /root/.hyperlpr3/20230229/onnx/
```

然后 PC 浏览器访问 `http://192.168.0.100:8888/`，点击下载。

---

## Step 2：在 WSL 中转换 RKNN

### 2.1 进入 WSL 并准备环境

```bash
# 进入 WSL
wsl

# 进入项目目录
cd /mnt/d/VsSlave/Python_code/rk3568

# 激活 rknn-toolkit2 环境（根据你的实际环境名）
#conda activate rknn
# 或
source ~/rknn_env/bin/activate

# 确认 rknn-toolkit2 可用
python3 -c "from rknn.api import RKNN; print('RKNN OK')"
```

### 2.2 转换检测模型（y5fu_640x_sim.onnx）

创建转换脚本：

```bash
cat > convert_plate_detect.py << 'EOF'
"""将 HyperLPR3 车牌检测 ONNX 模型转换为 RKNN 格式"""

from rknn.api import RKNN
import os

ONNX_MODEL = "models/y5fu_640x_sim.onnx"
RKNN_MODEL = "models/plate_detect_640.rknn"
TARGET = "rk3568"

if __name__ == "__main__":
    if not os.path.exists(ONNX_MODEL):
        print(f"错误: 找不到 {ONNX_MODEL}")
        print("请先从板子下载模型文件（参考 Step 1）")
        exit(1)

    rknn = RKNN()

    # 配置
    # HyperLPR3 的 YOLOv5 变体，输入是归一化后的浮点
    # 需要根据原始模型的预处理确定 mean_values 和 std_values
    print("配置 RKNN...")
    rknn.config(
        mean_values=[[0, 0, 0]],
        std_values=[[255, 255, 255]],
        target_platform=TARGET,
    )

    # 加载 ONNX
    print(f"加载 ONNX: {ONNX_MODEL}")
    ret = rknn.load_onnx(model=ONNX_MODEL)
    if ret != 0:
        print("加载 ONNX 失败！")
        exit(-1)
    print("加载成功")

    # 构建（先不量化，验证是否正常）
    print("构建 RKNN 模型（不量化）...")
    ret = rknn.build(do_quantization=False)
    if ret != 0:
        print("构建失败！")
        exit(-1)
    print("构建成功")

    # 导出
    print(f"导出 RKNN: {RKNN_MODEL}")
    rknn.export_rknn(RKNN_MODEL)
    print(f"导出成功！文件大小: {os.path.getsize(RKNN_MODEL) / 1024 / 1024:.1f}MB")

    # 精度测试（在 PC 上模拟）
    print("\n精度测试...")
    ret = rknn.init_runtime(target=None)  # PC 上模拟
    if ret == 0:
        import numpy as np
        # 创建随机测试输入
        test_input = np.random.randint(0, 255, (1, 640, 640, 3), dtype=np.uint8)
        outputs = rknn.inference(inputs=[test_input])
        print(f"输出形状: {[o.shape for o in outputs]}")
        print("精度测试通过！")
    else:
        print("PC 精度测试跳过（不影响板子使用）")

    rknn.release()
    print("\n✅ 转换完成！")
    print(f"输出文件: {RKNN_MODEL}")
    print(f"下一步: 上传到板子 models/ 目录")
EOF

python3 convert_plate_detect.py
```

### 2.3 如果转换失败

**常见问题 1：ONNX opset 版本不兼容**

```bash
# 检查 ONNX 模型信息
python3 -c "
import onnx
model = onnx.load('models/y5fu_640x_sim.onnx')
print('Opset version:', model.opset_import[0].version)
print('Inputs:', [(i.name, i.type) for i in model.graph.input])
print('Outputs:', [(o.name, o.type) for o in model.graph.output])
"
```

**常见问题 2：动态 shape**

HyperLPR3 的检测模型可能有动态输入尺寸。如果报错，需要先固定 shape：

```python
# fix_onnx_shape.py
import onnx
from onnx import shape_inference

model = onnx.load("models/y5fu_640x_sim.onnx")

# 固定输入尺寸为 640x640
dim = model.graph.input[0].type.tensor_type.shape.dim
dim[0].dim_value = 1    # batch
dim[1].dim_value = 3    # channels
dim[2].dim_value = 640  # height
dim[3].dim_value = 640  # width

model = shape_inference.infer_shapes(model)
onnx.save(model, "models/y5fu_640x_fixed.onnx")
print("固定 shape 完成: models/y5fu_640x_fixed.onnx")
```

然后转换固定后的模型：
```bash
# 修改 convert_plate_detect.py 中的 ONNX_MODEL 路径
# ONNX_MODEL = "models/y5fu_640x_fixed.onnx"
python3 convert_plate_detect.py
```

---

## Step 3：上传 RKNN 模型到板子

```powershell
# 回到 PC PowerShell
scp models/plate_detect_640.rknn root@192.168.0.100:/opt/rk3568/models/

# 同时上传识别模型（后面集成用）
scp models/rpv3_mdict_160_r3.onnx root@192.168.0.100:/opt/rk3568/models/
scp models/litemodel_cls_96x_r1.onnx root@192.168.0.100:/opt/rk3568/models/
```

---

## Step 4：在板子上测试 RKNN 模型

```bash
# SSH 登录板子
ssh root@192.168.0.100

cd /opt/rk3568
source .venv/bin/activate

# 测试 RKNN 模型是否能正常加载和推理
python3 << 'EOF'
import numpy as np
from rknnlite.api import RKNNLite

rknn = RKNNLite()

# 加载模型
ret = rknn.load_rknn("models/plate_detect_640.rknn")
print(f"加载模型: {'成功' if ret == 0 else '失败'}")

if ret == 0:
    ret = rknn.init_runtime(target=None)
    print(f"初始化运行时: {'成功' if ret == 0 else '失败'}")

    if ret == 0:
        # 测试推理
        test = np.random.randint(0, 255, (1, 640, 640, 3), dtype=np.uint8)
        import time
        start = time.time()
        outputs = rknn.inference(inputs=[test])
        elapsed = (time.time() - start) * 1000
        print(f"推理耗时: {elapsed:.1f}ms")
        print(f"输出形状: {[o.shape for o in outputs]}")
        print(f"输出样例: {outputs[0].flatten()[:10]}")

    rknn.release()

print("\n✅ RKNN 模型测试完成")
EOF
```

**预期输出：**
```
加载模型: 成功
初始化运行时: 成功
推理耗时: ~10ms
输出形状: [(1, ...)]
✅ RKNN 模型测试完成
```

---

## Step 5：集成到系统

模型转换和测试通过后，需要修改 `plate.py`：

### 新架构代码逻辑

```python
# plate.py 新架构（伪代码，完整版本待模型转换成功后提供）

class PlateDetector:
    def detect(self, frame, vehicle_regions=None):
        # 方案 1：NPU 检测 + onnxruntime 识别
        if self.use_npu_detection:
            # NPU 检测车牌区域 (~10ms)
            detections = self._detect_plate_npu(frame)
            # CPU 识别车牌号 (~20ms)
            for det in detections:
                crop = frame[det['y1']:det['y2'], det['x1']:det['x2']]
                plate_number = self._recognize_plate(crop)
                det['plate_number'] = plate_number
```

### 需要分析的模型信息

在板子上运行以下命令，分析检测模型的输入输出格式：

```bash
python3 << 'EOF'
import numpy as np
import cv2
from rknnlite.api import RKNNLite
import onnxruntime as ort

# 1. 分析检测模型输出格式
rknn = RKNNLite()
rknn.load_rknn("models/plate_detect_640.rknn")
rknn.init_runtime(target=None)

# 用摄像头抓一帧测试
cap = cv2.VideoCapture("rtsp://admin:password@192.168.0.66:554/Streaming/Channels/201")
ret, frame = cap.read()
cap.release()

if ret:
    # 缩放到 640x640
    img = cv2.resize(frame, (640, 640))
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = np.expand_dims(img, 0).astype(np.uint8)
    
    outputs = rknn.inference(inputs=[img])
    for i, out in enumerate(outputs):
        print(f"输出[{i}] shape: {out.shape}, dtype: {out.dtype}")
        print(f"  min: {out.min():.4f}, max: {out.max():.4f}")
        print(f"  前10个值: {out.flatten()[:10]}")

rknn.release()

# 2. 分析识别模型输入输出格式
rec_session = ort.InferenceSession("models/rpv3_mdict_160_r3.onnx")
for inp in rec_session.get_inputs():
    print(f"识别输入: name={inp.name}, shape={inp.shape}, type={inp.type}")
for out in rec_session.get_outputs():
    print(f"识别输出: name={out.name}, shape={out.shape}, type={out.type}")

# 3. 分析颜色分类模型
cls_session = ort.InferenceSession("models/litemodel_cls_96x_r1.onnx")
for inp in cls_session.get_inputs():
    print(f"分类输入: name={inp.name}, shape={inp.shape}, type={inp.type}")
for out in cls_session.get_outputs():
    print(f"分类输出: name={out.name}, shape={out.shape}, type={out.type}")

EOF
```

把输出发给我，我根据模型格式写完整的 plate.py 集成代码。

---

## 模型文件清单

| 文件 | 位置 | 用途 | 大小 |
|------|------|------|------|
| `y5fu_640x_sim.onnx` | 板子 `/root/.hyperlpr3/20230229/onnx/` | 车牌检测（转 RKNN） | 3.9MB |
| `y5fu_320x_sim.onnx` | 同上 | 车牌检测（小尺寸备选） | 2.3MB |
| `rpv3_mdict_160_r3.onnx` | 同上 | 车牌号识别 | 10MB |
| `litemodel_cls_96x_r1.onnx` | 同上 | 车牌颜色分类 | 1.6MB |
| `plate_detect_640.rknn` | 转换后生成 | NPU 车牌检测 | ~4MB |

---

## 预期性能

| 方案 | 检测 | 识别 | 总耗时 | FPS |
|------|------|------|--------|-----|
| 当前 HyperLPR3 | ~300ms (CPU) | ~200ms (CPU) | ~500ms | ~6 |
| 优化后 NPU+CPU | ~10ms (NPU) | ~20ms (CPU) | ~30ms | ~20 |

---

## 故障排查

### Q: rknn-toolkit2 未安装
```bash
# WSL 中安装
pip install rknn_toolkit2-2.3.2-cp312-cp312-manylinux_2_17_x86_64.manylinux2014_x86_64.whl
```

### Q: onnx 模块缺失
```bash
pip install onnx
```

### Q: 转换报 "Unsupported operator"
HyperLPR3 的检测模型是 YOLOv5 变体，大部分算子都支持。如果不支持，可能需要简化模型：
```python
import onnx
from onnx import optimizer
model = onnx.load("models/y5fu_640x_sim.onnx")
model = optimizer.optimize(model)
onnx.save(model, "models/y5fu_640x_optimized.onnx")
```

---

*文档结束 - 按步骤操作后，将模型输入输出信息发给开发者以完成集成*