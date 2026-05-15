"""车牌识别模块"""

import time
import numpy as np
import cv2
from src.utils.logger import setup_logger

logger = setup_logger("plate_detector")


class PlateDetector:
    """车牌检测与识别器"""

    def __init__(self, config: dict, npu_enabled: bool = False):
        self.config = config
        self.npu_enabled = npu_enabled
        self.confidence = config.get("confidence", 0.5)
        self.model = None
        self.ocr = None
        self._backend = None

        # ROI 感兴趣区域 [x1, y1, x2, y2] 归一化坐标 (0~1)
        self.roi = config.get("roi", None)
        if self.roi:
            logger.info(f"车牌检测 ROI 区域: {self.roi}")

        logger.info(f"车牌检测器初始化 (NPU={'开启' if npu_enabled else '关闭'})")

    def load_model(self) -> bool:
        """加载车牌检测和识别模型"""
        try:
            # 尝试使用 HyperLPR3
            try:
                from hyperlpr3 import LicensePlateCatcher

                self.model = LicensePlateCatcher()
                self._backend = "hyperlpr3"
                logger.info("HyperLPR3 车牌识别模型加载成功")
                return True
            except ImportError:
                logger.warning("HyperLPR3 未安装，尝试使用 PaddleOCR")
            except Exception as e:
                logger.warning(f"HyperLPR3 加载失败: {e}，尝试使用 PaddleOCR")

            # 回退到 PaddleOCR
            try:
                from paddleocr import PaddleOCR

                self.ocr = PaddleOCR(
                    use_angle_cls=True,
                    lang="ch",
                )
                self._backend = "paddleocr"
                logger.info("PaddleOCR 车牌识别模型加载成功")
                return True
            except ImportError:
                logger.error("PaddleOCR 也未安装，车牌识别功能不可用")
                return False

        except Exception as e:
            logger.error(f"加载车牌识别模型失败: {e}")
            return False

    def detect(self, frame: np.ndarray, vehicle_regions: list = None) -> list:
        """
        检测和识别车牌

        Args:
            frame: BGR 图像
            vehicle_regions: NPU 检测到的车辆区域 [{"bbox": [x1,y1,x2,y2], ...}, ...]
                            如果提供，只在车辆区域内搜索车牌（大幅加速）

        Returns:
            检测结果列表: [{"bbox": [x1,y1,x2,y2], "confidence": float, "label": "plate", "plate_number": "京A12345", "plate_color": "蓝"}]
        """
        if self.model is None and self.ocr is None:
            return []

        start_time = time.time()

        # 如果有车辆区域，只在车辆区域内检测车牌（大幅缩小搜索范围）
        if vehicle_regions and len(vehicle_regions) > 0:
            results = self._detect_in_vehicles(frame, vehicle_regions)
        else:
            # 回退到 ROI 全区域检测
            roi_frame, roi_offset = self._crop_roi(frame)

            if self._backend == "hyperlpr3":
                results = self._detect_hyperlpr3(roi_frame)
            else:
                results = self._detect_paddleocr(roi_frame)

            if roi_offset:
                for r in results:
                    r["bbox"] = [r["bbox"][0] + roi_offset[0], r["bbox"][1] + roi_offset[1],
                                  r["bbox"][2] + roi_offset[0], r["bbox"][3] + roi_offset[1]]

        elapsed = (time.time() - start_time) * 1000
        logger.info(f"车牌识别耗时: {elapsed:.1f}ms, 识别到 {len(results)} 个车牌"
                     f"{' (车辆辅助)' if vehicle_regions else ''}")

        return results

    def _detect_in_vehicles(self, frame: np.ndarray, vehicles: list) -> list:
        """在 NPU 检测到的车辆区域内搜索车牌（核心优化）"""
        all_results = []
        h, w = frame.shape[:2]

        for vehicle in vehicles:
            vx1, vy1, vx2, vy2 = vehicle["bbox"]

            # 车牌一般在车辆下半部分，聚焦该区域
            vehicle_h = vy2 - vy1
            vehicle_w = vx2 - vx1

            # 只取车辆下半部分（车牌位置），加一些余量
            plate_y1 = max(0, vy1 + int(vehicle_h * 0.4))
            plate_y2 = min(h, vy2 + int(vehicle_h * 0.1))
            plate_x1 = max(0, vx1 - int(vehicle_w * 0.05))
            plate_x2 = min(w, vx2 + int(vehicle_w * 0.05))

            crop = frame[plate_y1:plate_y2, plate_x1:plate_x2]
            if crop.size == 0 or crop.shape[0] < 10 or crop.shape[1] < 20:
                continue

            # 在裁剪区域内检测车牌
            if self._backend == "hyperlpr3":
                detections = self._detect_hyperlpr3(crop)
            else:
                detections = self._detect_paddleocr(crop)

            # 将坐标映射回原图
            for r in detections:
                r["bbox"] = [r["bbox"][0] + plate_x1, r["bbox"][1] + plate_y1,
                              r["bbox"][2] + plate_x1, r["bbox"][3] + plate_y1]
                all_results.append(r)

        # 如果车辆区域都没检测到，回退到 ROI 全区域检测（兜底）
        if not all_results:
            roi_frame, roi_offset = self._crop_roi(frame)
            if self._backend == "hyperlpr3":
                all_results = self._detect_hyperlpr3(roi_frame)
            else:
                all_results = self._detect_paddleocr(roi_frame)
            if roi_offset:
                for r in all_results:
                    r["bbox"] = [r["bbox"][0] + roi_offset[0], r["bbox"][1] + roi_offset[1],
                                  r["bbox"][2] + roi_offset[0], r["bbox"][3] + roi_offset[1]]

        return all_results

    def _crop_roi(self, frame: np.ndarray) -> tuple:
        """
        裁剪 ROI 感兴趣区域

        Returns:
            (roi_frame, offset): 裁剪后的图像和偏移量 (x_off, y_off)
        """
        if not self.roi or len(self.roi) != 4:
            return frame, None

        h, w = frame.shape[:2]
        x1 = int(self.roi[0] * w)
        y1 = int(self.roi[1] * h)
        x2 = int(self.roi[2] * w)
        y2 = int(self.roi[3] * h)

        # 边界检查
        x1 = max(0, min(x1, w - 1))
        y1 = max(0, min(y1, h - 1))
        x2 = max(0, min(x2, w))
        y2 = max(0, min(y2, h))

        roi_frame = frame[y1:y2, x1:x2]
        return roi_frame, (x1, y1)

    def _detect_hyperlpr3(self, frame: np.ndarray) -> list:
        """使用 HyperLPR3 进行车牌识别（含裁剪放大重识别）"""
        results = []
        try:
            # 第一次检测：全图检测
            # HyperLPR3 v0.1.x API: LicensePlateCatcher()(frame)
            # 返回格式: [(plate_number, confidence, plate_type, [x1, y1, x2, y2]), ...]
            detections = self.model(frame)
            logger.info(f"HyperLPR3 原始检测: {len(detections)} 个结果")

            for i, det in enumerate(detections):
                logger.info(f"  车牌[{i}]: 号牌={det[0]}, 置信度={det[1]:.3f}, 类型={det[2]}, bbox={det[3] if len(det) > 3 else 'N/A'}")

            for det in detections:
                plate_number = det[0]
                confidence = float(det[1])
                plate_type = det[2]  # 0: 蓝牌, 1: 黄牌, 2: 白牌, 3: 绿牌
                bbox = det[3] if len(det) > 3 else [0, 0, 0, 0]

                plate_color_map = {0: "蓝", 1: "黄", 2: "白", 3: "绿", 4: "黑"}

                x1, y1, x2, y2 = int(bbox[0]), int(bbox[1]), int(bbox[2]), int(bbox[3])

                # 注：裁剪放大重识别已禁用（耗时 300-600ms，严重影响帧率）
                # 如需启用，取消下方注释
                # if confidence < 0.9 and (x2 - x1) > 10 and (y2 - y1) > 5:
                #     refined = self._refine_plate(frame, x1, y1, x2, y2)
                #     if refined is not None and refined["confidence"] > confidence:
                #         plate_number = refined["plate_number"]
                #         confidence = refined["confidence"]
                #         plate_type = refined["plate_type"]
                #         x1, y1, x2, y2 = refined["bbox"]

                if confidence < self.confidence:
                    continue

                results.append({
                    "bbox": [x1, y1, x2, y2],
                    "confidence": round(confidence, 3),
                    "label": "plate",
                    "plate_number": plate_number,
                    "plate_color": plate_color_map.get(plate_type, "未知"),
                })

        except Exception as e:
            logger.error(f"HyperLPR3 识别失败: {e}")

        return results

    def _refine_plate(self, frame: np.ndarray, x1: int, y1: int, x2: int, y2: int) -> dict:
        """裁剪车牌区域放大后重新识别，提高准确率"""
        try:
            h, w = frame.shape[:2]

            # 扩大裁剪区域（包含一些背景，帮助检测）
            pad_x = max(10, int((x2 - x1) * 0.3))
            pad_y = max(5, int((y2 - y1) * 0.3))
            cx1 = max(0, x1 - pad_x)
            cy1 = max(0, y1 - pad_y)
            cx2 = min(w, x2 + pad_x)
            cy2 = min(h, y2 + pad_y)

            # 裁剪车牌区域
            crop = frame[cy1:cy2, cx1:cx2]
            if crop.size == 0:
                return None

            # 放大到至少 320 像素宽（提高识别精度）
            crop_h, crop_w = crop.shape[:2]
            scale = max(2.0, 320 / crop_w)
            if scale > 1.5:
                crop = cv2.resize(crop, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)

            # 在放大后的裁剪区域重新识别
            redetect = self.model(crop)
            if not redetect:
                return None

            # 取置信度最高的结果
            best = max(redetect, key=lambda d: float(d[1]))
            plate_number = best[0]
            confidence = float(best[1])
            plate_type = best[2]
            rbbox = best[3] if len(best) > 3 else [0, 0, 0, 0]

            # 将裁剪区域的坐标映射回原图
            rx1 = int(rbbox[0] / scale) + cx1
            ry1 = int(rbbox[1] / scale) + cy1
            rx2 = int(rbbox[2] / scale) + cx1
            ry2 = int(rbbox[3] / scale) + cy1

            return {
                "plate_number": plate_number,
                "confidence": confidence,
                "plate_type": plate_type,
                "bbox": [rx1, ry1, rx2, ry2],
            }

        except Exception as e:
            logger.debug(f"车牌裁剪重识别失败: {e}")
            return None

    def _detect_paddleocr(self, frame: np.ndarray) -> list:
        """使用 PaddleOCR 进行车牌识别"""
        results = []
        try:
            ocr_results = self.ocr.ocr(frame, cls=True)

            if ocr_results is None or len(ocr_results) == 0:
                return results

            for line in ocr_results:
                if line is None:
                    continue
                for item in line:
                    bbox_points = item[0]
                    text = item[1][0]
                    confidence = float(item[1][1])

                    if confidence < self.confidence:
                        continue

                    if self._is_plate_like(text):
                        xs = [p[0] for p in bbox_points]
                        ys = [p[1] for p in bbox_points]
                        x1, y1 = int(min(xs)), int(min(ys))
                        x2, y2 = int(max(xs)), int(max(ys))

                        results.append({
                            "bbox": [x1, y1, x2, y2],
                            "confidence": round(confidence, 3),
                            "label": "plate",
                            "plate_number": text,
                            "plate_color": "未知",
                        })

        except Exception as e:
            logger.error(f"PaddleOCR 车牌识别失败: {e}")

        return results

    @staticmethod
    def _is_plate_like(text: str) -> bool:
        """判断文本是否像车牌号"""
        if not text or len(text) < 7:
            return False

        clean = text.replace(" ", "").replace(".", "").replace("·", "")

        if len(clean) == 8:
            if clean[0] and clean[1].isalpha():
                return True

        if len(clean) == 7:
            if clean[0] and clean[1].isalpha():
                return True

        return False

    def release(self):
        """释放模型资源"""
        self.model = None
        self.ocr = None
        logger.info("车牌检测器已释放")