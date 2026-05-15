"""通用文字识别模块 - 基于 PaddleOCR"""

import time
import numpy as np
from src.utils.logger import setup_logger

logger = setup_logger("ocr_detector")


class OCRDetector:
    """通用文字识别器"""

    def __init__(self, config: dict):
        """
        初始化文字识别器

        Args:
            config: OCR 配置
        """
        self.config = config
        self.det_threshold = config.get("det_threshold", 0.5)
        self.rec_threshold = config.get("rec_threshold", 0.5)
        self.lang = config.get("lang", "ch")
        self.use_angle_cls = config.get("use_angle_cls", True)
        self.ocr = None

        logger.info("文字识别器初始化")

    def load_model(self) -> bool:
        """加载 PaddleOCR 模型"""
        try:
            from paddleocr import PaddleOCR

            self.ocr = PaddleOCR(
                use_angle_cls=self.use_angle_cls,
                lang=self.lang,
            )

            logger.info("PaddleOCR 文字识别模型加载成功")
            return True

        except ImportError:
            logger.error("PaddleOCR 未安装，请执行: pip install paddleocr")
            return False
        except Exception as e:
            logger.error(f"加载 PaddleOCR 模型失败: {e}")
            return False

    def detect(self, frame: np.ndarray, region: list = None) -> list:
        """
        识别图像中的文字

        Args:
            frame: BGR 图像
            region: 可选，指定识别区域 [x1, y1, x2, y2]

        Returns:
            识别结果列表: [{
                "bbox": [x1, y1, x2, y2],
                "confidence": float,
                "label": "text",
                "text": "识别的文字内容"
            }]
        """
        if self.ocr is None:
            return []

        # 如果指定了区域，裁剪图像
        if region is not None:
            x1, y1, x2, y2 = region
            frame = frame[y1:y2, x1:x2]

        start_time = time.time()
        results = []

        try:
            ocr_results = self.ocr.ocr(frame, cls=True)

            if ocr_results is None or len(ocr_results) == 0:
                return results

            for line in ocr_results:
                if line is None:
                    continue
                for item in line:
                    bbox_points = item[0]  # [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
                    text = item[1][0]  # 识别文字
                    confidence = float(item[1][1])  # 置信度

                    if confidence < self.rec_threshold:
                        continue

                    # 计算外接矩形
                    xs = [p[0] for p in bbox_points]
                    ys = [p[1] for p in bbox_points]
                    bx1, by1 = int(min(xs)), int(min(ys))
                    bx2, by2 = int(max(xs)), int(max(ys))

                    # 如果有区域偏移，调整坐标
                    if region is not None:
                        bx1 += region[0]
                        by1 += region[1]
                        bx2 += region[0]
                        by2 += region[1]

                    results.append({
                        "bbox": [bx1, by1, bx2, by2],
                        "confidence": round(confidence, 3),
                        "label": "text",
                        "text": text,
                    })

        except Exception as e:
            logger.error(f"文字识别失败: {e}")

        elapsed = (time.time() - start_time) * 1000
        logger.debug(f"文字识别耗时: {elapsed:.1f}ms, 识别到 {len(results)} 段文字")

        return results

    def detect_in_regions(self, frame: np.ndarray, regions: list) -> list:
        """
        在多个指定区域内进行文字识别

        Args:
            frame: BGR 图像
            regions: 区域列表，每个区域为 {"bbox": [x1, y1, x2, y2], ...}

        Returns:
            所有区域的文字识别结果
        """
        all_results = []

        for region in regions:
            bbox = region.get("bbox", [])
            if len(bbox) == 4:
                ocr_results = self.detect(frame, region=bbox)
                all_results.extend(ocr_results)

        return all_results

    def release(self):
        """释放模型资源"""
        self.ocr = None
        logger.info("文字识别器已释放")