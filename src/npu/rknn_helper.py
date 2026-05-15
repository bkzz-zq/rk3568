"""RKNN NPU 辅助模块 - 模型转换和推理工具"""

import os
import numpy as np
from src.utils.logger import setup_logger

logger = setup_logger("rknn_helper")


class RKNNHelper:
    """RKNN 模型管理工具"""

    @staticmethod
    def check_npu_available() -> bool:
        """检查 NPU 是否可用"""
        try:
            from rknnlite.api import RKNNLite

            rknn = RKNNLite()
            ret = rknn.init_runtime(target=None)
            if ret == 0:
                rknn.release()
                logger.info("NPU 可用")
                return True
            else:
                logger.warning("NPU 初始化失败")
                return False
        except ImportError:
            logger.warning("rknnlite2 未安装，NPU 不可用")
            return False
        except Exception as e:
            logger.error(f"NPU 检测失败: {e}")
            return False

    @staticmethod
    def convert_yolo_to_rknn(
        onnx_model_path: str,
        output_path: str = None,
        target: str = "rk3568",
    ) -> bool:
        """
        将 YOLOv8 ONNX 模型转换为 RKNN 格式

        注意：此操作需要在 PC 上使用 rknn-toolkit2 完成

        Args:
            onnx_model_path: ONNX 模型路径
            output_path: RKNN 模型输出路径
            target: 目标平台
        """
        try:
            from rknn.api import RKNN

            if output_path is None:
                output_path = onnx_model_path.replace(".onnx", ".rknn")

            rknn = RKNN()

            # 配置模型
            rknn.config(
                mean_values=[[0, 0, 0]],
                std_values=[[255, 255, 255]],
                target_platform=target,
            )

            # 加载 ONNX 模型
            ret = rknn.load_onnx(model=onnx_model_path)
            if ret != 0:
                logger.error(f"加载 ONNX 模型失败: {onnx_model_path}")
                return False

            # 构建 RKNN 模型
            ret = rknn.build(do_quantization=True, dataset=None)
            if ret != 0:
                logger.error("构建 RKNN 模型失败")
                return False

            # 保存模型
            ret = rknn.export_rknn(output_path)
            if ret != 0:
                logger.error(f"保存 RKNN 模型失败: {output_path}")
                return False

            # 精度分析（可选）
            ret = rknn.init_runtime(target=target)
            if ret == 0:
                rknn.release()

            logger.info(f"RKNN 模型转换成功: {output_path}")
            return True

        except ImportError:
            logger.error("rknn-toolkit2 未安装，请在 PC 上执行模型转换")
            logger.error("安装方式: pip install rknn-toolkit2")
            return False
        except Exception as e:
            logger.error(f"模型转换失败: {e}")
            return False

    @staticmethod
    def benchmark_model(model_path: str, iterations: int = 100) -> dict:
        """
        对 RKNN 模型进行性能基准测试

        Args:
            model_path: RKNN 模型路径
            iterations: 测试次数

        Returns:
            性能数据字典
        """
        try:
            import time
            from rknnlite.api import RKNNLite

            rknn = RKNNLite()
            ret = rknn.load_model(model_path)
            if ret != 0:
                logger.error(f"加载模型失败: {model_path}")
                return {}

            ret = rknn.init_runtime(target=None)
            if ret != 0:
                logger.error("初始化运行时失败")
                return {}

            # 预热
            dummy_input = np.random.randn(1, 640, 640, 3).astype(np.float32)
            for _ in range(10):
                rknn.inference(inputs=[dummy_input])

            # 基准测试
            times = []
            for _ in range(iterations):
                start = time.time()
                rknn.inference(inputs=[dummy_input])
                elapsed = (time.time() - start) * 1000
                times.append(elapsed)

            rknn.release()

            result = {
                "model": model_path,
                "iterations": iterations,
                "avg_ms": round(np.mean(times), 2),
                "min_ms": round(np.min(times), 2),
                "max_ms": round(np.max(times), 2),
                "fps": round(1000.0 / np.mean(times), 1),
            }

            logger.info(f"基准测试结果:")
            logger.info(f"  平均耗时: {result['avg_ms']}ms")
            logger.info(f"  最小耗时: {result['min_ms']}ms")
            logger.info(f"  最大耗时: {result['max_ms']}ms")
            logger.info(f"  推理 FPS: {result['fps']}")

            return result

        except ImportError:
            logger.error("rknnlite2 未安装")
            return {}
        except Exception as e:
            logger.error(f"基准测试失败: {e}")
            return {}


def check_system_info():
    """检查系统信息"""
    import platform

    logger.info("=== 系统信息 ===")
    logger.info(f"平台: {platform.platform()}")
    logger.info(f"架构: {platform.machine()}")
    logger.info(f"Python: {platform.python_version()}")

    # 检查 NPU
    npu_available = RKNNHelper.check_npu_available()
    logger.info(f"NPU: {'可用' if npu_available else '不可用'}")

    # 检查关键依赖
    dependencies = [
        ("cv2", "OpenCV"),
        ("numpy", "NumPy"),
        ("yaml", "PyYAML"),
        ("websockets", "WebSockets"),
        ("ultralytics", "Ultralytics YOLO"),
        ("paddleocr", "PaddleOCR"),
        ("hyperlpr3", "HyperLPR3"),
        ("rknnlite.api", "RKNNLite2"),
    ]

    logger.info("=== 依赖检查 ===")
    for module_name, display_name in dependencies:
        try:
            __import__(module_name)
            logger.info(f"  ✓ {display_name}")
        except ImportError:
            logger.info(f"  ✗ {display_name}")

    return npu_available


if __name__ == "__main__":
    check_system_info()