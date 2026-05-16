"""RTSP 视频流获取模块 - 支持硬件解码"""

import os
import time
import threading
import cv2
from src.utils.logger import setup_logger

logger = setup_logger("camera")

# 检测 GStreamer + MPP 硬解码是否可用
def _check_gstreamer_available() -> bool:
    """检查 OpenCV 是否编译了 GStreamer 后端"""
    try:
        info = cv2.getBuildInformation()
        # getBuildInformation() 输出是列对齐格式，空格数不确定
        # 例如: "    GStreamer:                   YES (1.19.90)"
        for line in info.split("\n"):
            if "GStreamer" in line and "YES" in line:
                return True
        return False
    except Exception:
        return False


def _check_mpp_available() -> bool:
    """检查 mppvideodec 插件是否可用"""
    import subprocess
    try:
        result = subprocess.run(
            ["gst-inspect-1.0", "mppvideodec"],
            capture_output=True, timeout=3
        )
        return result.returncode == 0
    except Exception:
        return False


# 全局检测结果（只检测一次）
_GST_AVAILABLE = _check_gstreamer_available()
_MPP_AVAILABLE = _check_mpp_available() if _GST_AVAILABLE else False
_HARWARE_DECODE = _GST_AVAILABLE and _MPP_AVAILABLE

if _HARWARE_DECODE:
    logger.info("✓ GStreamer + MPP 硬解码可用")
else:
    reasons = []
    if not _GST_AVAILABLE:
        reasons.append("OpenCV 无 GStreamer 后端")
    elif not _MPP_AVAILABLE:
        reasons.append("mppvideodec 插件未安装")
    logger.info(f"使用 FFmpeg 软解码 ({', '.join(reasons)})")


class CameraStream:
    """海康威视 RTSP 视频流管理（支持硬件解码）"""

    def __init__(self, config: dict):
        self.config = config
        self.use_stream = config.get("use_stream", "sub")
        self.fps_limit = config.get("fps_limit", 15)
        self.reconnect_interval = config.get("reconnect_interval", 5)
        self.hw_decode = config.get("hw_decode", True)  # 是否尝试硬解码

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
        self._decode_mode = "unknown"  # "gst_hw" / "ffmpeg_sw"
        self._output_scale = 1.0       # 坐标还原缩放比（GStreamer 缩放后需还原）
        self._original_size = None     # 原始 RTSP 分辨率 (w, h)

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

    def _probe_rtsp_resolution(self) -> tuple:
        """探测原始 RTSP 分辨率（不带 videoscale 的 pipeline）"""
        try:
            pipeline = (
                f"rtspsrc location={self.rtsp_url} latency=0 protocols=tcp ! "
                f"rtph264depay ! h264parse ! mppvideodec ! "
                f"videoconvert ! video/x-raw,format=BGR ! "
                f"fakesink"
            )
            # 用 FFmpeg 快速获取分辨率（更可靠）
            probe_cap = cv2.VideoCapture(self.rtsp_url, cv2.CAP_FFMPEG)
            if probe_cap.isOpened():
                w = int(probe_cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                h = int(probe_cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                probe_cap.release()
                if w > 0 and h > 0:
                    return (w, h)
        except Exception:
            pass
        # 回退：假设 1920x1080
        return (1920, 1080)

    def _build_gst_pipeline(self, rtsp_url: str, detect_width: int = 640, detect_height: int = 360) -> str:
        """构建 GStreamer + MPP 硬解码 pipeline（含硬件缩放）"""
        pipeline = (
            f"rtspsrc location={rtsp_url} latency=0 protocols=tcp ! "
            f"rtph264depay ! h264parse ! "
            f"mppvideodec ! "                                                # RK3568 VPU 硬解码
            f"videoconvert ! video/x-raw,format=BGR ! "
            f"videoscale ! video/x-raw,width={detect_width},height={detect_height} ! "  # 硬件缩放（必须同时指定宽高）
            f"appsink drop=true max-buffers=1 sync=false"
        )
        return pipeline

    def connect(self) -> bool:
        """连接 RTSP 视频流（优先硬解码）"""
        try:
            if self.cap is not None:
                self.cap.release()

            # 1. 尝试 GStreamer + MPP 硬解码
            if self.hw_decode and _HARWARE_DECODE:
                try:
                    pipeline = self._build_gst_pipeline(self.rtsp_url)
                    logger.info("尝试 GStreamer + MPP 硬解码...")
                    self.cap = cv2.VideoCapture(pipeline, cv2.CAP_GSTREAMER)

                    if self.cap.isOpened():
                        self._decode_mode = "gst_hw"
                        width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                        height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                        fps = self.cap.get(cv2.CAP_PROP_FPS) or 25
                        # 获取原始 RTSP 分辨率（用于坐标映射到原图）
                        self._original_size = self._probe_rtsp_resolution()
                        self._output_scale = width / self._original_size[0]
                        logger.info(f"✓ 硬解码连接成功: {width}x{height} @ {fps:.1f}fps [GStreamer+MPP] "
                                    f"(原始 {self._original_size[0]}x{self._original_size[1]}, 缩放比 {self._output_scale:.2f})")
                        return True
                    else:
                        logger.warning("GStreamer 硬解码连接失败，回退 FFmpeg 软解码")
                        self.cap.release()
                        self.cap = None
                except Exception as e:
                    logger.warning(f"GStreamer 硬解码异常: {e}，回退 FFmpeg 软解码")
                    self.cap = None

            # 2. 回退 FFmpeg 软解码
            os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;tcp|fflags;nobuffer|flags;low_delay"
            self.cap = cv2.VideoCapture(self.rtsp_url, cv2.CAP_FFMPEG)
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

            if not self.cap.isOpened():
                logger.error("无法连接 RTSP 视频流")
                return False

            self._decode_mode = "ffmpeg_sw"
            width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = self.cap.get(cv2.CAP_PROP_FPS)
            logger.info(f"软解码连接成功: {width}x{height} @ {fps:.1f}fps [FFmpeg]")
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
                if self.cap is not None:
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

    @property
    def decode_mode(self) -> str:
        """当前解码模式: 'gst_hw' / 'ffmpeg_sw'"""
        return self._decode_mode

    @property
    def output_scale(self) -> float:
        """输出帧相对原始 RTSP 的缩放比（用于坐标还原到原图）"""
        return self._output_scale

    def get_info(self) -> dict:
        """获取视频流信息"""
        info = {
            "url": self._mask_url(self.rtsp_url),
            "stream_type": self.use_stream,
            "fps_limit": self.fps_limit,
            "decode_mode": self._decode_mode,
            "is_running": self.is_running(),
        }
        if self.cap is not None and self.cap.isOpened():
            info["width"] = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            info["height"] = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        return info