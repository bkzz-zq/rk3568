"""
YOLOv8 ONNX -> RKNN 模型转换脚本
在 RK3568 板子上运行
"""

import os
import sys

MODEL_DIR = "models"
ONNX_PATH = os.path.join(MODEL_DIR, "yolov8n.onnx")
RKNN_PATH = os.path.join(MODEL_DIR, "yolov8n.rknn")
PT_PATH = os.path.join(MODEL_DIR, "yolov8n.pt")


def step1_export_onnx():
    """步骤1: 导出 YOLOv8n 为 ONNX 格式"""
    if os.path.exists(ONNX_PATH):
        print(f"[跳过] ONNX 文件已存在: {ONNX_PATH}")
        return

    print("=" * 50)
    print("步骤1: 导出 YOLOv8n.pt -> ONNX")
    print("=" * 50)

    from ultralytics import YOLO

    # 下载 YOLOv8n 并导出 ONNX
    model = YOLO("yolov8n.pt")
    model.export(
        format="onnx",
        imgsz=640,
        opset=12,
        simplify=True,
    )

    # 移动到 models 目录
    src = "yolov8n.onnx"
    if os.path.exists(src) and not os.path.exists(ONNX_PATH):
        os.rename(src, ONNX_PATH)

    print(f"✓ ONNX 导出完成: {ONNX_PATH}")


def step2_convert_rknn():
    """步骤2: ONNX -> RKNN 转换"""
    if not os.path.exists(ONNX_PATH):
        print(f"[错误] ONNX 文件不存在: {ONNX_PATH}")
        sys.exit(1)

    print("=" * 50)
    print("步骤2: ONNX -> RKNN 转换 (目标: RK3568)")
    print("=" * 50)

    from rknn.api import RKNN

    rknn = RKNN(verbose=True)

    # 配置
    print("\n--- 配置 RKNN ---")
    rknn.config(
        mean_values=[[0, 0, 0]],
        std_values=[[255, 255, 255]],
        target_platform="rk3568",
        # optimization_level=3,
        # quantized_dtype="asymmetric_quantized-8",  # INT8 量化（需要校准数据）
        # quantized_algorithm="normal",
        # float_dtype="float16",  # FP16
    )

    # 加载 ONNX
    print("\n--- 加载 ONNX 模型 ---")
    ret = rknn.load_onnx(model=ONNX_PATH)
    if ret != 0:
        print(f"[错误] 加载 ONNX 失败: {ret}")
        sys.exit(1)
    print("✓ ONNX 加载成功")

    # 构建（不做量化，使用 FP16）
    print("\n--- 构建 RKNN 模型 ---")
    ret = rknn.build(do_quantization=False)
    if ret != 0:
        print(f"[错误] 构建 RKNN 失败: {ret}")
        sys.exit(1)
    print("✓ RKNN 构建成功")

    # 导出
    print("\n--- 导出 RKNN 文件 ---")
    ret = rknn.export_rknn(RKNN_PATH)
    if ret != 0:
        print(f"[错误] 导出 RKNN 失败: {ret}")
        sys.exit(1)
    print(f"✓ RKNN 导出完成: {RKNN_PATH}")

    # 释放
    rknn.release()

    # 打印文件大小
    size_mb = os.path.getsize(RKNN_PATH) / (1024 * 1024)
    print(f"\n模型文件大小: {size_mb:.1f} MB")


def step3_test_rknn():
    """步骤3: 在 NPU 上测试 RKNN 模型"""
    if not os.path.exists(RKNN_PATH):
        print(f"[错误] RKNN 文件不存在: {RKNN_PATH}")
        sys.exit(1)

    print("=" * 50)
    print("步骤3: 在 NPU 上测试 RKNN 模型")
    print("=" * 50)

    from rknnlite.api import RKNNLite
    import numpy as np

    rknn = RKNNLite()

    # 加载模型
    ret = rknn.load_rknn(RKNN_PATH)
    if ret != 0:
        print(f"[错误] 加载 RKNN 失败: {ret}")
        sys.exit(1)

    # 初始化运行时（NPU）
    ret = rknn.init_runtime(target=None)  # None = 本机 NPU
    if ret != 0:
        print(f"[错误] 初始化运行时失败: {ret}")
        sys.exit(1)

    # 用随机数据测试
    import time
    dummy_input = np.random.randint(0, 255, (640, 640, 3), dtype=np.uint8)

    # 预热
    rknn.inference(inputs=[dummy_input])

    # 计时
    times = []
    for i in range(10):
        start = time.time()
        outputs = rknn.inference(inputs=[dummy_input])
        elapsed = time.time() - start
        times.append(elapsed)

    avg_ms = sum(times) / len(times) * 1000
    print(f"✓ NPU 推理测试通过!")
    print(f"  平均耗时: {avg_ms:.1f} ms")
    print(f"  输出形状: {[o.shape for o in outputs]}")

    rknn.release()


if __name__ == "__main__":
    os.makedirs(MODEL_DIR, exist_ok=True)

    print("YOLOv8 -> RKNN 模型转换工具")
    print("目标平台: RK3568\n")

    step1_export_onnx()
    step2_convert_rknn()
    step3_test_rknn()

    print("\n" + "=" * 50)
    print("🎉 全部完成!")
    print(f"模型文件: {RKNN_PATH}")
    print("现在可以运行: python3 src/main.py --no-ocr")
    print("=" * 50)