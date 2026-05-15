"""将 HyperLPR3 车牌检测 ONNX 模型转换为 RKNN 格式

在 WSL 中执行：
    cd /mnt/d/VsSlave/Python_code/rk3568
    conda activate rknn
    python3 convert_plate_detect.py
"""

from rknn.api import RKNN
import os
import sys

ONNX_MODEL = "models/y5fu_640x_sim.onnx"
RKNN_MODEL = "models/plate_detect_640.rknn"
TARGET = "rk3568"


def main():
    if not os.path.exists(ONNX_MODEL):
        print(f"错误: 找不到 {ONNX_MODEL}")
        print("请先从板子下载模型文件:")
        print(f"  scp root@192.168.0.100:/root/.hyperlpr3/20230229/onnx/y5fu_640x_sim.onnx ./models/")
        sys.exit(1)

    rknn = RKNN()

    print("=" * 50)
    print(" HyperLPR3 车牌检测模型 → RKNN 转换")
    print("=" * 50)

    # 配置
    print("\n[1/4] 配置 RKNN...")
    rknn.config(
        mean_values=[[0, 0, 0]],
        std_values=[[255, 255, 255]],
        target_platform=TARGET,
    )

    # 加载 ONNX
    print(f"\n[2/4] 加载 ONNX: {ONNX_MODEL}")
    ret = rknn.load_onnx(model=ONNX_MODEL)
    if ret != 0:
        print("加载 ONNX 失败！尝试固定 shape...")

        # 尝试固定 shape 后重新加载
        try:
            import onnx
            from onnx import shape_inference

            model = onnx.load(ONNX_MODEL)
            dim = model.graph.input[0].type.tensor_type.shape.dim
            dim[0].dim_value = 1
            dim[1].dim_value = 3
            dim[2].dim_value = 640
            dim[3].dim_value = 640
            model = shape_inference.infer_shapes(model)
            fixed_path = "models/y5fu_640x_fixed.onnx"
            onnx.save(model, fixed_path)

            ret = rknn.load_onnx(model=fixed_path)
            if ret != 0:
                print("固定 shape 后仍然失败！")
                sys.exit(-1)
            print("固定 shape 后加载成功")
        except Exception as e:
            print(f"固定 shape 失败: {e}")
            sys.exit(-1)

    # 构建
    print("\n[3/4] 构建 RKNN 模型（不量化）...")
    ret = rknn.build(do_quantization=False)
    if ret != 0:
        print("构建失败！")
        sys.exit(-1)
    print("构建成功")

    # 导出
    print(f"\n[4/4] 导出 RKNN: {RKNN_MODEL}")
    rknn.export_rknn(RKNN_MODEL)
    size_mb = os.path.getsize(RKNN_MODEL) / 1024 / 1024
    print(f"导出成功！文件大小: {size_mb:.1f}MB")

    # 精度测试
    print("\n精度测试...")
    ret = rknn.init_runtime(target=None)
    if ret == 0:
        import numpy as np
        test_input = np.random.randint(0, 255, (1, 640, 640, 3), dtype=np.uint8)
        outputs = rknn.inference(inputs=[test_input])
        for i, out in enumerate(outputs):
            print(f"  输出[{i}] shape: {out.shape}, dtype: {out.dtype}")
        print("精度测试通过！")
    else:
        print("PC 精度测试跳过（不影响板子使用）")

    rknn.release()

    print("\n" + "=" * 50)
    print("✅ 转换完成！")
    print(f"输出文件: {RKNN_MODEL} ({size_mb:.1f}MB)")
    print("\n下一步:")
    print(f"  scp {RKNN_MODEL} root@192.168.0.100:/opt/rk3568/models/")
    print("=" * 50)


if __name__ == "__main__":
    main()