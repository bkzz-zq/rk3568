"""车牌识别模块 - NPU 检测加速版"""

import time
import copy
import numpy as np
import cv2
from src.utils.logger import setup_logger

logger = setup_logger("plate_detector")

# HyperLPR3 车牌字符集（78 字符，与 rpv3_mdict_160_r3.onnx 对应）
# 来源: hyperlpr3/common/tokenize.py
PLATE_CHARS = [
    # CTC blank (index 0), 省份 (1-31), 字母 (32-57), 数字 (58-67), 特殊 (68-77)
    "京", "沪", "津", "渝", "冀", "晋", "蒙", "辽", "吉", "黑",
    "苏", "浙", "皖", "闽", "赣", "鲁", "豫", "鄂", "湘", "粤",
    "桂", "琼", "川", "贵", "云", "藏", "陕", "甘", "青", "宁",
    "新",
    "A", "B", "C", "D", "E", "F", "G", "H", "J", "K",
    "L", "M", "N", "P", "Q", "R", "S", "T", "U", "V",
    "W", "X", "Y", "Z",
    "0", "1", "2", "3", "4", "5", "6", "7", "8", "9",
    "警", "学", "挂", "港", "澳", "领", "使", "临", "电",
]

# 颜色分类: 0=蓝, 1=黄, 2=白
PLATE_COLOR_MAP = {0: "蓝", 1: "黄", 2: "白"}


def letter_box(img, size=(640, 640)):
    """HyperLPR3 风格的 letterbox（与模型预处理一致）"""
    h, w, c = img.shape
    r = min(size[0] / h, size[1] / w)
    new_h, new_w = int(h * r), int(w * r)
    top = int((size[0] - new_h) / 2)
    left = int((size[1] - new_w) / 2)
    bottom = size[0] - new_h - top
    right = size[1] - new_w - left
    img_resize = cv2.resize(img, (new_w, new_h))
    img = cv2.copyMakeBorder(img_resize, top, bottom, left, right,
                             borderType=cv2.BORDER_CONSTANT, value=(0, 0, 0))
    return img, r, left, top


def xywh2xyxy(boxes):
    """xywh → xyxy"""
    xyxy = copy.deepcopy(boxes)
    xyxy[:, 0] = boxes[:, 0] - boxes[:, 2] / 2
    xyxy[:, 1] = boxes[:, 1] - boxes[:, 3] / 2
    xyxy[:, 2] = boxes[:, 0] + boxes[:, 2] / 2
    xyxy[:, 3] = boxes[:, 1] + boxes[:, 3] / 2
    return xyxy


def nms(boxes, iou_thresh):
    """非极大值抑制"""
    if len(boxes) == 0:
        return []
    index = np.argsort(boxes[:, 4])[::-1]
    keep = []
    while index.size > 0:
        i = index[0]
        keep.append(i)
        x1 = np.maximum(boxes[i, 0], boxes[index[1:], 0])
        y1 = np.maximum(boxes[i, 1], boxes[index[1:], 1])
        x2 = np.minimum(boxes[i, 2], boxes[index[1:], 2])
        y2 = np.minimum(boxes[i, 3], boxes[index[1:], 3])
        w = np.maximum(0, x2 - x1)
        h = np.maximum(0, y2 - y1)
        inter_area = w * h
        union_area = (boxes[i, 2] - boxes[i, 0]) * (boxes[i, 3] - boxes[i, 1]) + \
                     (boxes[index[1:], 2] - boxes[index[1:], 0]) * (boxes[index[1:], 3] - boxes[index[1:], 1])
        iou = inter_area / (union_area - inter_area + 1e-6)
        idx = np.where(iou <= iou_thresh)[0]
        index = index[idx + 1]
    return keep


class PlateDetector:
    """车牌检测与识别器（NPU 加速版）"""

    def __init__(self, config: dict, npu_enabled: bool = False):
        self.config = config
        self.npu_enabled = npu_enabled
        self.confidence = config.get("confidence", 0.5)
        self.box_threshold = config.get("box_threshold", 0.3)
        self.nms_threshold = config.get("nms_threshold", 0.5)

        # 模型句柄
        self.det_model = None      # RKNN 检测模型 (NPU)
        self.rec_session = None    # ONNX 识别模型 (CPU)
        self.cls_session = None    # ONNX 颜色分类模型 (CPU)
        self.model = None          # HyperLPR3 后备
        self.ocr = None            # PaddleOCR 后备
        self._backend = None       # "npu" / "hyperlpr3" / "paddleocr"

        # ROI 感兴趣区域
        self.roi = config.get("roi", None)
        if self.roi:
            logger.info(f"车牌检测 ROI 区域: {self.roi}")

        logger.info(f"车牌检测器初始化 (NPU={'开启' if npu_enabled else '关闭'})")

    def load_model(self) -> bool:
        """加载车牌检测和识别模型"""
        # 优先尝试 NPU 模式
        if self.npu_enabled:
            if self._load_npu_models():
                self._backend = "npu"
                return True
            logger.warning("NPU 模型加载失败，回退到 HyperLPR3")

        # 回退到 HyperLPR3
        try:
            from hyperlpr3 import LicensePlateCatcher
            self.model = LicensePlateCatcher()
            self._backend = "hyperlpr3"
            logger.info("HyperLPR3 车牌识别模型加载成功（后备模式）")
            return True
        except ImportError:
            logger.warning("HyperLPR3 未安装")
        except Exception as e:
            logger.warning(f"HyperLPR3 加载失败: {e}")

        # 回退到 PaddleOCR
        try:
            from paddleocr import PaddleOCR
            self.ocr = PaddleOCR(use_angle_cls=True, lang="ch")
            self._backend = "paddleocr"
            logger.info("PaddleOCR 车牌识别模型加载成功")
            return True
        except ImportError:
            logger.error("PaddleOCR 也未安装，车牌识别功能不可用")
            return False

    def _load_npu_models(self) -> bool:
        """加载 NPU 检测模型 + CPU 识别模型"""
        try:
            import onnxruntime as ort

            # 1. 加载 RKNN 检测模型
            from rknnlite.api import RKNNLite
            det_model_path = self.config.get("det_model_path", "models/plate_detect_640.rknn")
            self.det_model = RKNNLite()
            ret = self.det_model.load_rknn(det_model_path)
            if ret != 0:
                logger.error(f"加载 RKNN 车牌检测模型失败: {det_model_path}")
                return False
            ret = self.det_model.init_runtime(target=None)
            if ret != 0:
                logger.error("初始化 RKNN 车牌检测运行时失败")
                return False
            logger.info(f"RKNN 车牌检测模型加载成功: {det_model_path}")

            # 2. 加载 ONNX 识别模型
            rec_model_path = self.config.get("rec_model_path", "models/rpv3_mdict_160_r3.onnx")
            self.rec_session = ort.InferenceSession(rec_model_path, providers=['CPUExecutionProvider'])
            logger.info(f"ONNX 车牌识别模型加载成功: {rec_model_path}")

            # 3. 加载 ONNX 颜色分类模型
            cls_model_path = self.config.get("cls_model_path", "models/litemodel_cls_96x_r1.onnx")
            self.cls_session = ort.InferenceSession(cls_model_path, providers=['CPUExecutionProvider'])
            logger.info(f"ONNX 车牌颜色分类模型加载成功: {cls_model_path}")

            logger.info("✓ NPU 车牌检测加速模式就绪")
            return True

        except Exception as e:
            logger.error(f"NPU 模型加载失败: {e}")
            self.det_model = None
            self.rec_session = None
            self.cls_session = None
            return False

    def detect(self, frame: np.ndarray, vehicle_regions: list = None) -> list:
        """
        检测和识别车牌

        Args:
            frame: BGR 图像
            vehicle_regions: 车辆区域（保留接口兼容）

        Returns:
            [{"bbox": [x1,y1,x2,y2], "confidence": float, "label": "plate",
              "plate_number": "湘AU5555", "plate_color": "蓝"}]
        """
        if self._backend is None:
            return []

        start_time = time.time()

        if self._backend == "npu":
            results = self._detect_npu(frame)
        elif self._backend == "hyperlpr3":
            results = self._detect_hyperlpr3(frame)
        else:
            roi_frame, roi_offset = self._crop_roi(frame)
            results = self._detect_paddleocr(roi_frame)
            if roi_offset:
                for r in results:
                    r["bbox"] = [r["bbox"][0] + roi_offset[0], r["bbox"][1] + roi_offset[1],
                                 r["bbox"][2] + roi_offset[0], r["bbox"][3] + roi_offset[1]]

        elapsed = (time.time() - start_time) * 1000
        logger.info(f"车牌识别耗时: {elapsed:.1f}ms, 识别到 {len(results)} 个车牌 [{self._backend}]")

        return results

    # ==================== NPU 加速模式 ====================

    def _detect_npu(self, frame: np.ndarray) -> list:
        """NPU 检测 + CPU 识别 全流程"""
        # 1. 裁剪 ROI
        roi_frame, roi_offset = self._crop_roi(frame)

        # 2. NPU 检测车牌区域
        detections = self._detect_plate_rknn(roi_frame)
        if not detections:
            return []

        # 3. 坐标映射回原图
        if roi_offset:
            for det in detections:
                det["bbox"] = [det["bbox"][0] + roi_offset[0], det["bbox"][1] + roi_offset[1],
                               det["bbox"][2] + roi_offset[0], det["bbox"][3] + roi_offset[1]]

        # 4. 对每个检测到的车牌做识别
        results = []
        for det in detections:
            x1, y1, x2, y2 = det["bbox"]
            h, w = frame.shape[:2]
            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(w, x2), min(h, y2)

            crop = frame[y1:y2, x1:x2]
            if crop.size == 0 or crop.shape[0] < 5 or crop.shape[1] < 10:
                continue

            # 识别车牌号
            plate_number = self._recognize_plate(crop)
            if not plate_number:
                continue

            # 识别颜色
            plate_color = self._classify_color(crop)

            results.append({
                "bbox": [x1, y1, x2, y2],
                "confidence": det["confidence"],
                "label": "plate",
                "plate_number": plate_number,
                "plate_color": plate_color,
            })

        return results

    def _detect_plate_rknn(self, frame: np.ndarray) -> list:
        """使用 RKNN NPU 进行车牌检测"""
        try:
            h, w = frame.shape[:2]
            det_start = time.time()

            # 预处理: letterbox 640x640 → BGR 转 RGB → NHWC uint8
            img_u8, r, left, top = letter_box(frame, (640, 640))
            img_u8 = cv2.cvtColor(img_u8, cv2.COLOR_BGR2RGB)
            img_u8 = np.expand_dims(img_u8, 0).astype(np.uint8)

            outputs = self.det_model.inference(inputs=[img_u8])
            dets = outputs[0]  # (1, 25200, 15)
            if len(dets.shape) == 3:
                dets = dets[0]  # (25200, 15)

            # 后处理 (与 HyperLPR3 multitask_detect.py 一致)
            # 过滤低置信度
            choice = dets[:, 4] > self.box_threshold
            dets = dets[choice]

            if len(dets) == 0:
                return []

            # 类别分数 = objectness × class_score
            dets[:, 13:15] *= dets[:, 4:5]
            box = dets[:, :4]
            boxes = xywh2xyxy(box)
            score = np.max(dets[:, 13:15], axis=-1, keepdims=True)

            # 组合: [x1,y1,x2,y2, score, ...corners, class_idx]
            output = np.concatenate((boxes, score, dets[:, 5:13]), axis=1)

            # NMS
            reserve = nms(output, self.nms_threshold)
            output = output[reserve]

            # 坐标还原
            output[:, [0, 2, 5, 7, 9, 11]] -= left
            output[:, [1, 3, 6, 8, 10, 12]] -= top
            output[:, [0, 2, 5, 7, 9, 11]] /= r
            output[:, [1, 3, 6, 8, 10, 12]] /= r

            # 转为结果列表
            results = []
            for row in output:
                x1 = max(0, int(row[0]))
                y1 = max(0, int(row[1]))
                x2 = min(w, int(row[2]))
                y2 = min(h, int(row[3]))
                conf = float(row[4])

                if conf < self.confidence:
                    continue
                if (x2 - x1) < 10 or (y2 - y1) < 5:
                    continue

                results.append({
                    "bbox": [x1, y1, x2, y2],
                    "confidence": round(conf, 3),
                })

            det_ms = (time.time() - det_start) * 1000
            if results:
                logger.info(f"NPU 车牌检测: {len(results)} 个, 耗时: {det_ms:.0f}ms")

            return results

        except Exception as e:
            logger.error(f"NPU 车牌检测失败: {e}")
            return []

    def _recognize_plate(self, crop: np.ndarray) -> str:
        """使用 ONNX 识别模型识别车牌号"""
        try:
            # 预处理: 缩放到 160x48, BGR→RGB, 归一化
            img = cv2.resize(crop, (160, 48))
            img = img[:, :, ::-1].transpose(2, 0, 1).copy().astype(np.float32)
            img = img / 255.0
            img = img.reshape(1, *img.shape)

            # 推理
            input_name = self.rec_session.get_inputs()[0].name
            output = self.rec_session.run(None, {input_name: img})[0]  # (1, 20, 78)

            # CTC 解码
            plate = self._ctc_decode(output[0])
            return plate

        except Exception as e:
            logger.debug(f"车牌识别失败: {e}")
            return ""

    def _ctc_decode(self, pred: np.ndarray) -> str:
        """CTC 解码: pred shape (20, 78) → 车牌号字符串"""
        chars = []
        prev_idx = -1
        for t in range(pred.shape[0]):
            idx = np.argmax(pred[t])
            if idx != 0 and idx != prev_idx:  # 0 = CTC blank
                if idx < len(PLATE_CHARS):
                    chars.append(PLATE_CHARS[idx - 1])  # chars 从 index 1 开始
            prev_idx = idx

        plate = "".join(chars)
        return plate

    def _classify_color(self, crop: np.ndarray) -> str:
        """使用 ONNX 分类模型识别车牌颜色"""
        try:
            img = cv2.resize(crop, (96, 96))
            img = img[:, :, ::-1].transpose(2, 0, 1).copy().astype(np.float32)
            img = img / 255.0
            img = img.reshape(1, *img.shape)

            input_name = self.cls_session.get_inputs()[0].name
            output = self.cls_session.run(None, {input_name: img})[0]  # (1, 3)
            color_idx = np.argmax(output[0])
            return PLATE_COLOR_MAP.get(int(color_idx), "未知")

        except Exception as e:
            logger.debug(f"车牌颜色分类失败: {e}")
            return "未知"

    # ==================== HyperLPR3 后备模式 ====================

    def _detect_hyperlpr3(self, frame: np.ndarray) -> list:
        """使用 HyperLPR3 端到端识别"""
        results = []
        try:
            roi_frame, roi_offset = self._crop_roi(frame)
            detections = self.model(roi_frame)
            if detections:
                logger.info(f"HyperLPR3 原始检测: {len(detections)} 个结果")
            else:
                logger.debug("HyperLPR3 原始检测: 0 个结果")

            for det in detections:
                plate_number = det[0]
                confidence = float(det[1])
                plate_type = det[2]
                bbox = det[3] if len(det) > 3 else [0, 0, 0, 0]
                plate_color_map = {0: "蓝", 1: "黄", 2: "白", 3: "绿", 4: "黑"}

                x1, y1, x2, y2 = int(bbox[0]), int(bbox[1]), int(bbox[2]), int(bbox[3])

                if roi_offset:
                    x1 += roi_offset[0]
                    y1 += roi_offset[1]
                    x2 += roi_offset[0]
                    y2 += roi_offset[1]

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

    # ==================== PaddleOCR 后备模式 ====================

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
                    text = item[1][0]
                    confidence = float(item[1][1])

                    if confidence < self.confidence:
                        continue
                    if self._is_plate_like(text):
                        bbox_points = item[0]
                        xs = [p[0] for p in bbox_points]
                        ys = [p[1] for p in bbox_points]
                        results.append({
                            "bbox": [int(min(xs)), int(min(ys)), int(max(xs)), int(max(ys))],
                            "confidence": round(confidence, 3),
                            "label": "plate",
                            "plate_number": text,
                            "plate_color": "未知",
                        })

        except Exception as e:
            logger.error(f"PaddleOCR 车牌识别失败: {e}")

        return results

    # ==================== 工具方法 ====================

    def _crop_roi(self, frame: np.ndarray) -> tuple:
        """裁剪 ROI 感兴趣区域"""
        if not self.roi or len(self.roi) != 4:
            return frame, None

        h, w = frame.shape[:2]
        x1 = max(0, min(int(self.roi[0] * w), w - 1))
        y1 = max(0, min(int(self.roi[1] * h), h - 1))
        x2 = max(0, min(int(self.roi[2] * w), w))
        y2 = max(0, min(int(self.roi[3] * h), h))

        return frame[y1:y2, x1:x2], (x1, y1)

    @staticmethod
    def _is_plate_like(text: str) -> bool:
        """判断文本是否像车牌号"""
        if not text or len(text) < 7:
            return False
        clean = text.replace(" ", "").replace(".", "").replace("·", "")
        if len(clean) in (7, 8) and clean[1].isalpha():
            return True
        return False

    def release(self):
        """释放模型资源"""
        if self.det_model is not None:
            self.det_model.release()
            self.det_model = None
        self.rec_session = None
        self.cls_session = None
        self.model = None
        self.ocr = None
        logger.info("车牌检测器已释放")