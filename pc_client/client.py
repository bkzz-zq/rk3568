"""PC 端接收客户端 - RTSP 直连视频 + WebSocket 检测叠加

架构：
  - 视频：PC 直连摄像头 RTSP（零延迟，原始画质）
  - 检测：RK3568 只发检测框 JSON（极低带宽）
  - 渲染：PC 本地叠加检测框显示
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import time
import signal
import threading
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont


class PCClient:
    """PC 端客户端：RTSP 直连视频 + WebSocket 检测叠加"""

    def __init__(
        self,
        rtsp_url: str = None,
        ws_host: str = "192.168.0.100",
        ws_port: int = 8765,
    ):
        self.rtsp_url = rtsp_url
        self.ws_url = f"ws://{ws_host}:{ws_port}"
        self.running = False
        self._ws_thread = None
        self._lock = threading.Lock()

        # 最新检测结果（JSON，极小数据量）
        self._detections = {
            "persons": [],
            "plates": [],
            "texts": [],
            "fps": 0.0,
        }
        self._ws_connected = False
        self._reconnect_interval = 3

        mode_parts = []
        if rtsp_url:
            mode_parts.append(f"RTSP直连: {rtsp_url}")
        mode_parts.append(f"WebSocket: {self.ws_url}")
        print(f"PC 客户端初始化")
        for p in mode_parts:
            print(f"  - {p}")

    def start(self):
        """启动客户端"""
        self.running = True

        # 启动 WebSocket 接收线程
        self._ws_thread = threading.Thread(target=self._ws_loop, daemon=True)
        self._ws_thread.start()

        # 主线程显示视频
        if self.rtsp_url:
            self._show_rtsp_with_overlay()
        else:
            # 回退模式：无 RTSP，显示等待状态
            print("未配置 RTSP，等待 WebSocket 检测数据...")
            self._wait_for_exit()

    def stop(self):
        """停止客户端"""
        self.running = False
        cv2.destroyAllWindows()
        print("PC 客户端已停止")

    # ── WebSocket 接收线程 ─────────────────────────────

    def _ws_loop(self):
        """WebSocket 连接循环"""
        import asyncio

        while self.running:
            try:
                asyncio.run(self._ws_connect())
            except KeyboardInterrupt:
                self.running = False
                break
            except Exception as e:
                if not self.running:
                    break
                print(f"[WS] 连接异常: {e}，{self._reconnect_interval}秒后重试...")
                self._ws_connected = False
                for _ in range(self._reconnect_interval * 10):
                    if not self.running:
                        return
                    time.sleep(0.1)

    async def _ws_connect(self):
        """连接 WebSocket 并接收检测结果"""
        import websockets

        print(f"[WS] 正在连接 {self.ws_url} ...")

        async with websockets.connect(self.ws_url, open_timeout=5) as ws:
            self._ws_connected = True
            print(f"[WS] 已连接到 RK3568 检测服务")

            async for message in ws:
                if not self.running:
                    break
                try:
                    data = json.loads(message)
                    if data.get("type") == "detection_result":
                        with self._lock:
                            self._detections = {
                                "persons": data.get("persons", []),
                                "plates": data.get("plates", []),
                                "texts": data.get("texts", []),
                                "fps": data.get("fps", 0),
                                "plate_roi": data.get("plate_roi"),
                            }
                except json.JSONDecodeError:
                    pass

    # ── RTSP 视频显示 ──────────────────────────────────

    def _show_rtsp_with_overlay(self):
        """RTSP 直连视频 + 检测框叠加"""
        print(f"[RTSP] 正在连接 {self.rtsp_url} ...")

        cap = cv2.VideoCapture(self.rtsp_url, cv2.CAP_FFMPEG)
        if not cap.isOpened():
            print(f"[RTSP] 连接失败！请检查 RTSP 地址和网络")
            print(f"[RTSP] 地址: {self.rtsp_url}")
            self.running = False
            return

        # 设置缓冲区大小为 1，减少延迟
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

        fps = cap.get(cv2.CAP_PROP_FPS) or 25
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) or 1920)
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 1080)
        print(f"[RTSP] 连接成功: {width}x{height} @ {fps:.0f}fps")
        print("按 'q' 退出")

        window_name = "RK3568 Vision Detection"
        frame_count = 0
        fps_start = time.time()
        display_fps = 0.0

        try:
            while self.running:
                ret, frame = cap.read()
                if not ret:
                    print("[RTSP] 读帧失败，尝试重连...")
                    cap.release()
                    time.sleep(1)
                    cap = cv2.VideoCapture(self.rtsp_url, cv2.CAP_FFMPEG)
                    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                    continue

                frame_count += 1

                # 叠加检测结果
                with self._lock:
                    detections = self._detections.copy()
                    ws_connected = self._ws_connected

                # 绘制检测框
                self._draw_overlay(frame, detections, ws_connected)

                # 计算 FPS
                elapsed = time.time() - fps_start
                if elapsed >= 1.0:
                    display_fps = frame_count / elapsed
                    frame_count = 0
                    fps_start = time.time()

                # 显示 FPS 和状态
                status = "CONNECTED" if ws_connected else "DISCONNECTED"
                color = (0, 255, 0) if ws_connected else (0, 0, 255)
                cv2.putText(
                    frame, f"FPS: {display_fps:.0f} | Detection: {status}",
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2
                )

                # 显示检测统计
                summary = (
                    f"Persons: {len(detections.get('persons', []))} | "
                    f"Plates: {len(detections.get('plates', []))} | "
                    f"Detect FPS: {detections.get('fps', 0):.0f}"
                )
                cv2.putText(
                    frame, summary, (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2
                )

                # 显示车牌识别结果（PIL 支持中文）
                y_offset = 90
                for plate in detections.get("plates", []):
                    plate_text = f"车牌: {plate.get('plate_number', '')} ({plate.get('plate_color', '')})"
                    self._put_chinese_text(frame, plate_text, (10, y_offset), (0, 0, 255), 22)
                    y_offset += 30

                cv2.imshow(window_name, frame)

                key = cv2.waitKey(1) & 0xFF
                if key == ord("q"):
                    self.running = False
                    break

                if cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) < 1:
                    self.running = False
                    break

        except KeyboardInterrupt:
            self.running = False
        finally:
            cap.release()
            cv2.destroyAllWindows()

    def _draw_overlay(self, frame, detections, ws_connected):
        """在帧上绘制检测框"""
        h, w = frame.shape[:2]

        # 绘制 ROI 区域虚线框（黄色）
        plate_roi = detections.get("plate_roi")
        if plate_roi and len(plate_roi) == 4:
            rx1 = int(plate_roi[0] * w)
            ry1 = int(plate_roi[1] * h)
            rx2 = int(plate_roi[2] * w)
            ry2 = int(plate_roi[3] * h)
            self._draw_dashed_rect(frame, (rx1, ry1), (rx2, ry2), (0, 255, 255), 2, 20)
            cv2.putText(frame, "Plate ROI", (rx1, ry1 - 8),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)

        if not ws_connected:
            return

        # 行人检测框（绿色）
        for person in detections.get("persons", []):
            bbox = person.get("bbox")
            if bbox and len(bbox) == 4:
                x1, y1, x2, y2 = bbox
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                conf = person.get("confidence", 0)
                label = f"{person.get('label', 'person')} {conf:.2f}"
                cv2.putText(frame, label, (x1, y1 - 5),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        # 车牌检测框（红色）+ 中文文字
        for plate in detections.get("plates", []):
            bbox = plate.get("bbox")
            if bbox and len(bbox) == 4:
                x1, y1, x2, y2 = bbox
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
                plate_number = plate.get("plate_number", "")
                plate_color = plate.get("plate_color", "")
                label = f"{plate_number} [{plate_color}]"
                # 使用 PIL 绘制中文
                self._put_chinese_text(frame, label, (x1, y1 - 30), (0, 0, 255), 24)

    @staticmethod
    def _draw_dashed_rect(img, pt1, pt2, color, thickness=1, dash_length=20):
        """绘制虚线矩形"""
        x1, y1 = pt1
        x2, y2 = pt2

        # 四条边
        edges = [
            ((x1, y1), (x2, y1)),  # 上
            ((x2, y1), (x2, y2)),  # 右
            ((x2, y2), (x1, y2)),  # 下
            ((x1, y2), (x1, y1)),  # 左
        ]

        for (ex1, ey1), (ex2, ey2) in edges:
            dx = ex2 - ex1
            dy = ey2 - ey1
            dist = max(abs(dx), abs(dy))
            dashes = int(dist / dash_length)
            if dashes == 0:
                dashes = 1

            for i in range(0, dashes, 2):
                sx = int(ex1 + dx * i / dashes)
                sy = int(ey1 + dy * i / dashes)
                ex = int(ex1 + dx * min(i + 1, dashes) / dashes)
                ey = int(ey1 + dy * min(i + 1, dashes) / dashes)
                cv2.line(img, (sx, sy), (ex, ey), color, thickness)

    def _put_chinese_text(self, img, text, position, color, font_size=20):
        """使用 PIL 在 OpenCV 图像上绘制中文文字"""
        try:
            # BGR → PIL (RGB)
            pil_img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
            draw = ImageDraw.Draw(pil_img)

            # 尝试加载中文字体
            font = None
            font_paths = [
                "C:/Windows/Fonts/msyh.ttc",       # Windows 微软雅黑
                "C:/Windows/Fonts/simhei.ttf",      # Windows 黑体
                "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",  # Linux
                "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",  # Linux
            ]
            for fp in font_paths:
                if os.path.exists(fp):
                    font = ImageFont.truetype(fp, font_size)
                    break

            if font is None:
                font = ImageFont.load_default()

            # PIL 用 RGB，OpenCV 用 BGR
            draw.text(position, text, font=font, fill=(color[2], color[1], color[0]))

            # PIL → BGR
            result = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
            np.copyto(img, result)
        except Exception as e:
            # 回退到普通 putText（可能显示乱码，但不会崩溃）
            cv2.putText(img, text, position, cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

    def _wait_for_exit(self):
        """等待退出（无 RTSP 模式）"""
        try:
            while self.running:
                time.sleep(0.5)
        except KeyboardInterrupt:
            self.running = False


def main():
    """PC 客户端入口"""
    import argparse

    parser = argparse.ArgumentParser(description="RK3568 视觉识别 - PC 接收客户端")
    parser.add_argument("--host", type=str, default="192.168.0.100", help="RK3568 IP 地址")
    parser.add_argument("--port", type=int, default=8765, help="WebSocket 端口")
    parser.add_argument("--rtsp", type=str, default=None,
                        help="RTSP 直连地址（可选，直连摄像头显示原始画质）")
    parser.add_argument("--use-main-stream", action="store_true",
                        help="使用主码流（高清）直连，需配置 camera.main_stream")
    args = parser.parse_args()

    # 自动生成 RTSP 地址
    rtsp_url = args.rtsp
    if not rtsp_url and args.use_main_stream:
        # 从配置文件读取主码流地址
        try:
            from src.utils.config import config
            config.load()
            rtsp_url = config.get("camera.main_stream")
            print(f"使用配置文件中的主码流: {rtsp_url}")
        except Exception:
            pass

    client = PCClient(rtsp_url=rtsp_url, ws_host=args.host, ws_port=args.port)

    def signal_handler(sig, frame):
        print("\n正在停止...")
        client.running = False

    signal.signal(signal.SIGINT, signal_handler)

    try:
        client.start()
    except KeyboardInterrupt:
        pass
    finally:
        client.stop()


if __name__ == "__main__":
    main()