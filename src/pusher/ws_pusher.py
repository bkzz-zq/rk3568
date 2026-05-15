"""WebSocket 推送模块 - 将识别结果推送给 PC 客户端"""

import json
import time
import asyncio
import threading
import numpy as np
from src.utils.logger import setup_logger
from src.utils.image import encode_image_to_base64, resize_image, draw_detections

logger = setup_logger("ws_pusher")


class WebSocketPusher:
    """WebSocket 服务器，推送识别结果给 PC 客户端"""

    def __init__(self, config: dict):
        """
        初始化 WebSocket 推送服务

        Args:
            config: WebSocket 配置
        """
        self.host = config.get("host", "0.0.0.0")
        self.port = config.get("port", 8765)
        self.push_interval = config.get("push_interval", 100) / 1000.0  # 转为秒
        self.send_image = config.get("send_image", True)
        self.image_scale = config.get("image_scale", 0.5)
        self.image_quality = config.get("image_quality", 70)

        self.clients = set()
        self._server = None
        self._loop = None
        self._thread = None
        self._running = False
        self._last_push_time = 0

        logger.info(f"WebSocket 推送服务初始化: ws://{self.host}:{self.port}")

    def start(self):
        """启动 WebSocket 服务器（后台线程）"""
        self._running = True
        self._thread = threading.Thread(target=self._run_server, daemon=True)
        self._thread.start()
        logger.info("WebSocket 推送服务已启动")

    def stop(self):
        """停止 WebSocket 服务器"""
        self._running = False
        if self._loop is not None:
            self._loop.call_soon_threadsafe(self._loop.stop)
        if self._thread is not None:
            self._thread.join(timeout=5)
            self._thread = None
        logger.info("WebSocket 推送服务已停止")

    def _run_server(self):
        """运行 WebSocket 服务器（在独立线程的事件循环中）"""
        try:
            import websockets

            self._loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._loop)

            async def handle_client(websocket):
                """处理客户端连接"""
                self.clients.add(websocket)
                client_addr = websocket.remote_address
                logger.info(f"PC 客户端已连接: {client_addr}, 当前连接数: {len(self.clients)}")

                try:
                    # 保持连接，等待客户端断开
                    async for message in websocket:
                        # 可以处理客户端发来的控制命令
                        try:
                            data = json.loads(message)
                            logger.debug(f"收到客户端消息: {data}")
                        except json.JSONDecodeError:
                            pass
                except websockets.exceptions.ConnectionClosed:
                    pass
                finally:
                    self.clients.discard(websocket)
                    logger.info(f"PC 客户端已断开: {client_addr}")

            async def run():
                async with websockets.serve(handle_client, self.host, self.port):
                    logger.info(f"WebSocket 服务器运行中: ws://{self.host}:{self.port}")
                    while self._running:
                        await asyncio.sleep(0.1)

            self._loop.run_until_complete(run())

        except ImportError:
            logger.error("websockets 库未安装，请执行: pip install websockets")
        except Exception as e:
            logger.error(f"WebSocket 服务器异常: {e}")

    def push_results(
        self,
        frame: np.ndarray = None,
        persons: list = None,
        plates: list = None,
        texts: list = None,
        fps: float = 0.0,
        plate_roi: list = None,
    ):
        """
        推送检测结果给所有连接的 PC 客户端（仅 JSON，无图像）

        PC 客户端直连 RTSP 获取视频，这里只发检测框坐标。
        数据量从 ~50KB/帧（图片）降到 ~1KB/帧（JSON）。

        Args:
            frame: 原始图像（新架构下不再使用）
            persons: 行人检测结果
            plates: 车牌识别结果
            texts: 文字识别结果
            fps: 当前检测帧率
            plate_roi: 车牌检测 ROI 区域 [x1, y1, x2, y2] 归一化坐标
        """
        if not self.clients:
            return

        # 频率限制
        current_time = time.time()
        if self.push_interval > 0 and (current_time - self._last_push_time) < self.push_interval:
            return
        self._last_push_time = current_time

        # 只发 JSON 检测结果（极小数据量 ~1KB）
        message = {
            "type": "detection_result",
            "timestamp": time.time(),
            "fps": round(fps, 1),
            "summary": {
                "person_count": len(persons) if persons else 0,
                "plate_count": len(plates) if plates else 0,
                "text_count": len(texts) if texts else 0,
            },
            "persons": persons or [],
            "plates": plates or [],
            "texts": texts or [],
            "plate_roi": plate_roi,
        }

        # 异步发送
        self._send_async(message)

    def push_event(self, event_type: str, data: dict):
        """
        推送事件消息

        Args:
            event_type: 事件类型
            data: 事件数据
        """
        if not self.clients:
            return

        message = {
            "type": "event",
            "event_type": event_type,
            "timestamp": time.time(),
            "data": data,
        }
        self._send_async(message)

    def _send_async(self, message: dict):
        """异步发送消息给所有客户端"""
        if not self._loop or not self.clients:
            return

        try:
            data = json.dumps(message, ensure_ascii=False)

            async def broadcast():
                disconnected = set()
                for client in self.clients:
                    try:
                        await client.send(data)
                    except Exception:
                        disconnected.add(client)

                # 移除断开的客户端
                self.clients -= disconnected

            asyncio.run_coroutine_threadsafe(broadcast(), self._loop)

        except Exception as e:
            logger.error(f"推送消息失败: {e}")

    @property
    def client_count(self) -> int:
        """当前连接的客户端数量"""
        return len(self.clients)