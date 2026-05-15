"""RTSP 视频流获取模块"""

import time
import threading
import cv2
from src.utils.logger import setup_logger

logger = setup_logger("camera")


class CameraStream:
    """海康威视 RTSP 视频流管理"""

    def __init__(self, config: dict):
        """
        初始化摄像头

        Args:
            config: 摄像头配置字典
        """
        self.config = config
        self.use_stream = config.get("use_stream", "sub")
        self.fps_limit = config.get("fps_limit", 15)
        self.reconnect_interval = config.get("reconnect_interval", 5)

        # 选择码流
        if self.use_stream == "main":
            self.rtsp_url = config.get("main_stream", "")
        else:
            self.rtsp_url = config.get("sub_stream", "")

        self.cap = None
        self._frame = None
        self._running = False
        self._lock = threading.Lock()
        self._thread = None
        self._last_frame_time = 0

        logger.info(f"摄像头初始化，使用{'主' if self.use_stream == 'main' else '子'}码流")
        logger.info(f"RTSP 地址: {self._mask_url(self.rtsp_url)}")

    @staticmethod
    def _mask_url(url: str) -> str:
        """隐藏 RTSP URL 中的密码"""
        try:
            parts = url.split("@")
            if len(parts) > 1:
                credentials = parts[0].split("://")[-1]
                user = credentials.split(":")[0]
                return parts[0].split("://")[0] + "://" + user + ":***@" + parts[1]
        except Exception:
            pass
        return url

    def connect(self) -> bool:
        """连接 RTSP 视频流"""
        try:
            if self.cap is not None:
                self.cap.release()

            # OpenCV RTSP 连接参数优化
            os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;tcp|fflags;nobuffer|flags;low_delay"
            self.cap = cv2.VideoCapture(self.rtsp_url, cv2.CAP_FFMPEG)

            # 设置缓冲区大小为 1，降低延迟
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

            if not self.cap.isOpened():
                logger.error("无法连接 RTSP 视频流")
                return False

            # 获取视频信息
            width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = self.cap.get(cv2.CAP_PROP_FPS)
            logger.info(f"视频流连接成功: {width}x{height} @ {fps:.1f}fps")

            return True

        except Exception as e:
            logger.error(f"连接 RTSP 视频流失败: {e}")
            return False

    def start(self):
        """启动视频流读取线程"""
        if self._running:
            logger.warning("视频流已在运行")
            return

        self._running = True
        self._thread = threading.Thread(target=self._read_loop, daemon=True)
        self._thread.start()
        logger.info("视频流读取线程已启动")

    def stop(self):
        """停止视频流"""
        self._running = False
        if self._thread is not None:
            self._thread.join(timeout=5)
            self._thread = None
        if self.cap is not None:
            self.cap.release()
            self.cap = None
        logger.info("视频流已停止")

    def _read_loop(self):
        """视频流读取循环（独立线程）"""
        frame_interval = 1.0 / self.fps_limit if self.fps_limit > 0 else 0

        while self._running:
            if self.cap is None or not self.cap.isOpened():
                logger.warning("视频流断开，尝试重新连接...")
                if not self.connect():
                    time.sleep(self.reconnect_interval)
                    continue

            ret, frame = self.cap.read()
            if not ret or frame is None:
                logger.warning("读取帧失败，尝试重新连接...")
                self.cap.release()
                self.cap = None
                time.sleep(self.reconnect_interval)
                continue

            current_time = time.time()
            if frame_interval > 0 and (current_time - self._last_frame_time) < frame_interval:
                continue

            with self._lock:
                self._frame = frame
            self._last_frame_time = current_time

    def get_frame(self):
        """
        获取最新一帧

        Returns:
            numpy.ndarray 或 None
        """
        with self._lock:
            return self._frame.copy() if self._frame is not None else None

    def is_running(self) -> bool:
        """检查视频流是否正在运行"""
        return self._running and self.cap is not None and self.cap.isOpened()

    def get_info(self) -> dict:
        """获取视频流信息"""
        info = {
            "url": self._mask_url(self.rtsp_url),
            "stream_type": self.use_stream,
            "fps_limit": self.fps_limit,
            "is_running": self.is_running(),
        }
        if self.cap is not None and self.cap.isOpened():
            info["width"] = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            info["height"] = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        return info


import os