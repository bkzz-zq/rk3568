"""行人检测模块 - 基于 YOLOv8"""

import time
import numpy as np
import cv2
from src.utils.logger import setup_logger
from src.utils.image import letterbox

logger = setup_logger("person_detector")

# COCO 数据集中相关类别 ID
PERSON_CLASS_ID = 0
VEHICLE_CLASS_IDS = [2, 5, 7]  # car=2, bus=5, truck=7


class PersonDetector:
    """行人检测器"""

    def __init__(self, config: dict, npu_enabled: bool = False):
        """
        初始化行人检测器

        Args:
            config: 行人检测配置
            npu_enabled: 是否使用 NPU 加速
        """
        self.config = config
        self.npu_enabled = npu_enabled
        self.confidence = config.get("confidence", 0.5)
        self.nms_threshold = config.get("nms_threshold", 0.4)
        self.vehicle_confidence = config.get("vehicle_confidence", 0.4)
        self.model = None
        self.input_size = (640, 640)

        # 缓存最近一次车辆检测结果（供车牌检测使用）
        self._last_vehicles = []

        logger.info(f"行人检测器初始化 (NPU={'开启' if npu_enabled else '关闭'})")

    def load_model(self) -> bool:
        """加载模型"""
        try:
            if self.npu_enabled:
                return self._load_rknn_model()
            else:
                return self._load_onnx_model()
        except Exception as e:
            logger.error(f"加载行人检测模型失败: {e}")
            return False

    def _load_rknn_model(self) -> bool:
        """加载 RKNN 模型（NPU 加速）"""
        try:
            from rknnlite.api import RKNNLite

            model_path = self.config.get("model_path", "models/yolov8n.rknn")
            self.model = RKNNLite()
            ret = self.model.load_rknn(model_path)
            if ret != 0:
                logger.error(f"加载 RKNN 模型失败: {model_path}")
                return False

            ret = self.model.init_runtime(target=None)  # 自动选择 NPU
            if ret != 0:
                logger.error("初始化 RKNN 运行时失败")
                return False

            logger.info(f"RKNN 模型加载成功: {model_path}")
            return True

        except ImportError:
            logger.warning("rknnlite2 未安装，回退到 ONNX 模式")
            self.npu_enabled = False
            return self._load_onnx_model()

    def _load_onnx_model(self) -> bool:
        """加载 ONNX 模型（CPU / GPU）"""
        model_path = self.config.get("onnx_model_path", "models/yolov8n.onnx")

        # 优先使用 ultralytics YOLO
        try:
            from ultralytics import YOLO

            self.model = YOLO(model_path.replace(".onnx", ".pt") if model_path.endswith(".onnx") else model_path)
            self._backend = "ultralytics"
            logger.info(f"YOLOv8 模型加载成功 (ultralytics)")
            return True
        except ImportError:
            pass

        # 回退到 OpenCV DNN
        try:
            self.model = cv2.dnn.readNetFromONNX(model_path)
            self._backend = "opencv_dnn"
            logger.info(f"YOLOv8 模型加载成功 (OpenCV DNN)")
            return True
        except Exception as e:
            logger.error(f"加载 ONNX 模型失败: {e}")
            return False

    def detect(self, frame: np.ndarray) -> list:
        """
        检测行人

        Args:
            frame: BGR 图像

        Returns:
            检测结果列表: [{"bbox": [x1,y1,x2,y2], "confidence": float, "label": "person"}]
        """
        if self.model is None:
            return []

        start_time = time.time()

        if self.npu_enabled:
            results = self._detect_rknn(frame)
        elif self._backend == "ultralytics":
            results = self._detect_ultralytics(frame)
        else:
            results = self._detect_opencv_dnn(frame)

        elapsed = (time.time() - start_time) * 1000
        logger.debug(f"行人检测耗时: {elapsed:.1f}ms, 检测到 {len(results)} 个行人")

        return results

    def detect_vehicles(self, frame: np.ndarray) -> list:
        """
        检测车辆（car, bus, truck），并缓存结果供车牌检测使用

        Args:
            frame: BGR 图像

        Returns:
            车辆检测结果列表
        """
        if self.model is None:
            return []

        start_time = time.time()

        if self.npu_enabled:
            results = self._detect_vehicles_rknn(frame)
        elif self._backend == "ultralytics":
            results = self._detect_vehicles_ultralytics(frame)
        else:
            results = self._detect_vehicles_opencv_dnn(frame)

        # 缓存车辆检测结果
        self._last_vehicles = results

        elapsed = (time.time() - start_time) * 1000
        logger.debug(f"车辆检测耗时: {elapsed:.1f}ms, 检测到 {len(results)} 辆车")

        return results

    @property
    def last_vehicles(self) -> list:
        """获取最近一次车辆检测结果"""
        return self._last_vehicles

    def _detect_rknn(self, frame: np.ndarray) -> list:
        """使用 RKNN NPU 进行检测"""
        img, ratio, (dw, dh) = letterbox(frame, self.input_size)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = np.expand_dims(img, 0).astype(np.uint8)
        outputs = self.model.inference(inputs=[img])
        return self._postprocess_yolo(outputs[0], frame.shape, ratio, dw, dh)

    def _detect_vehicles_rknn(self, frame: np.ndarray) -> list:
        """使用 RKNN NPU 检测车辆（复用同一个模型，只过滤车辆类别）"""
        img, ratio, (dw, dh) = letterbox(frame, self.input_size)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = np.expand_dims(img, 0).astype(np.uint8)
        outputs = self.model.inference(inputs=[img])
        return self._postprocess_vehicles(outputs[0], frame.shape, ratio, dw, dh)

    def _detect_vehicles_ultralytics(self, frame: np.ndarray) -> list:
        """使用 ultralytics YOLO 检测车辆"""
        results = self.model(frame, conf=self.vehicle_confidence, classes=VEHICLE_CLASS_IDS, verbose=False)
        detections = []
        for result in results:
            for box in result.boxes:
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                cls_id = int(box.cls[0].cpu().numpy())
                label_map = {2: "car", 5: "bus", 7: "truck"}
                detections.append({
                    "bbox": [int(x1), int(y1), int(x2), int(y2)],
                    "confidence": round(float(box.conf[0].cpu().numpy()), 3),
                    "label": label_map.get(cls_id, "vehicle"),
                })
        return detections

    def _detect_vehicles_opencv_dnn(self, frame: np.ndarray) -> list:
        """使用 OpenCV DNN 检测车辆"""
        h, w = frame.shape[:2]
        img, ratio, (dw, dh) = letterbox(frame, self.input_size)
        blob = cv2.dnn.blobFromImage(img, 1.0 / 255.0, self.input_size, swapRB=True)
        self.model.setInput(blob)
        outputs = self.model.forward()
        return self._postprocess_vehicles(outputs, (h, w), ratio, dw, dh)

    def _postprocess_vehicles(self, output, orig_shape, ratio, dw, dh) -> list:
        """YOLOv8 后处理 - 车辆类别"""
        oh, ow = orig_shape[:2]
        label_map = {2: "car", 5: "bus", 7: "truck"}
        detections = []

        if len(output.shape) == 3:
            output = output[0]
        if output.shape[0] < output.shape[1]:
            output = output.T

        for det in output:
            x, y, w, h = det[:4]
            class_scores = det[4:]
            if len(class_scores) < 8:
                continue

            # 找车辆类别最高分
            best_score = 0
            best_cls = -1
            for cls_id in VEHICLE_CLASS_IDS:
                if cls_id < len(class_scores) and class_scores[cls_id] > best_score:
                    best_score = class_scores[cls_id]
                    best_cls = cls_id

            if best_score < self.vehicle_confidence:
                continue

            x1 = max(0, min(int((x - w/2 - dw) / ratio), ow))
            y1 = max(0, min(int((y - h/2 - dh) / ratio), oh))
            x2 = max(0, min(int((x + w/2 - dw) / ratio), ow))
            y2 = max(0, min(int((y + h/2 - dh) / ratio), oh))

            detections.append({
                "bbox": [x1, y1, x2, y2],
                "confidence": round(float(best_score), 3),
                "label": label_map.get(best_cls, "vehicle"),
            })

        return self._nms(detections)

    def _detect_ultralytics(self, frame: np.ndarray) -> list:
        """使用 ultralytics YOLO 进行检测"""
        results = self.model(frame, conf=self.confidence, classes=[PERSON_CLASS_ID], verbose=False)

        detections = []
        for result in results:
            boxes = result.boxes
            for box in boxes:
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                conf = float(box.conf[0].cpu().numpy())
                detections.append({
                    "bbox": [int(x1), int(y1), int(x2), int(y2)],
                    "confidence": round(conf, 3),
                    "label": "person",
                })

        return detections

    def _detect_opencv_dnn(self, frame: np.ndarray) -> list:
        """使用 OpenCV DNN 进行检测"""
        h, w = frame.shape[:2]
        img, ratio, (dw, dh) = letterbox(frame, self.input_size)
        blob = cv2.dnn.blobFromImage(img, 1.0 / 255.0, self.input_size, swapRB=True)

        self.model.setInput(blob)
        outputs = self.model.forward()

        return self._postprocess_yolo(outputs, (h, w), ratio, dw, dh)

    def _postprocess_yolo(self, output, orig_shape, ratio, dw, dh) -> list:
        """YOLOv8 后处理"""
        oh, ow = orig_shape[:2]
        detections = []

        if len(output.shape) == 3:
            output = output[0]

        # YOLOv8 输出格式: [num_classes + 4, num_detections]
        if output.shape[0] < output.shape[1]:
            output = output.T  # 转置为 [num_detections, num_classes + 4]

        for det in output:
            x, y, w, h = det[:4]
            # 类别分数 (COCO 中 person 是第 0 类)
            class_scores = det[4:]
            person_score = class_scores[PERSON_CLASS_ID] if len(class_scores) > PERSON_CLASS_ID else 0

            if person_score < self.confidence:
                continue

            # 转换为原图坐标
            x1 = int((x - w / 2 - dw) / ratio)
            y1 = int((y - h / 2 - dh) / ratio)
            x2 = int((x + w / 2 - dw) / ratio)
            y2 = int((y + h / 2 - dh) / ratio)

            # 裁剪到图像范围内
            x1 = max(0, min(x1, ow))
            y1 = max(0, min(y1, oh))
            x2 = max(0, min(x2, ow))
            y2 = max(0, min(y2, oh))

            detections.append({
                "bbox": [x1, y1, x2, y2],
                "confidence": round(float(person_score), 3),
                "label": "person",
            })

        # NMS
        detections = self._nms(detections)
        return detections

    def _nms(self, detections: list) -> list:
        """非极大值抑制"""
        if not detections:
            return detections

        boxes = np.array([d["bbox"] for d in detections])
        scores = np.array([d["confidence"] for d in detections])

        x1 = boxes[:, 0]
        y1 = boxes[:, 1]
        x2 = boxes[:, 2]
        y2 = boxes[:, 3]

        areas = (x2 - x1 + 1) * (y2 - y1 + 1)
        order = scores.argsort()[::-1]

        keep = []
        while order.size > 0:
            i = order[0]
            keep.append(i)

            xx1 = np.maximum(x1[i], x1[order[1:]])
            yy1 = np.maximum(y1[i], y1[order[1:]])
            xx2 = np.minimum(x2[i], x2[order[1:]])
            yy2 = np.minimum(y2[i], y2[order[1:]])

            inter = np.maximum(0, xx2 - xx1 + 1) * np.maximum(0, yy2 - yy1 + 1)
            iou = inter / (areas[i] + areas[order[1:]] - inter)

            inds = np.where(iou <= self.nms_threshold)[0]
            order = order[inds + 1]

        return [detections[i] for i in keep]

    def release(self):
        """释放模型资源"""
        if self.model is not None:
            if self.npu_enabled:
                self.model.release()
            self.model = None
        logger.info("行人检测器已释放")