"""MQTT 客户端 - 桥接 FastAPI ↔ STM32F407

功能：
1. 订阅 STM32 发布的设备属性（温湿度/位置/限位）
2. 缓存最新设备状态，供 FastAPI 查询
3. 提供 API 发送控制命令到 STM32
"""

import json
import time
import threading
import paho.mqtt.client as mqtt
try:
    from paho.mqtt.enums import CallbackAPIVersion
except ImportError:
    CallbackAPIVersion = None
from src.utils.logger import setup_logger

logger = setup_logger("mqtt_client")


class MQTTClient:
    """MQTT 客户端（本地 mosquitto broker）"""

    def __init__(self, config: dict):
        self.host = config.get("host", "127.0.0.1")
        self.port = config.get("port", 1883)
        self.keepalive = config.get("keepalive", 60)

        # 设备缓存状态
        self._device_state = {
            "tremp": None,       # 温度
            "hum": None,         # 湿度
            "position": None,    # 门位置百分比
            "limit_sw": None,    # 限位开关编码
            "last_update": None, # 最后更新时间
            "online": False,     # 设备是否在线
        }
        self._lock = threading.Lock()

        # MQTT 客户端（兼容 paho-mqtt 1.x 和 2.x）
        try:
            self._client = mqtt.Client(
                callback_api_version=CallbackAPIVersion.VERSION1,
                client_id="rk3568_server",
                clean_session=True,
            )
        except TypeError:
            # paho-mqtt 1.x 没有 callback_api_version 参数
            self._client = mqtt.Client(client_id="rk3568_server", clean_session=True)
        self._client.on_connect = self._on_connect
        self._client.on_message = self._on_message
        self._client.on_disconnect = self._on_disconnect

        # 订阅的 topic
        self._sub_topic = "device/+/property/post"
        # 发布控制命令的 topic 前缀
        self._cmd_topic_prefix = "device"

        self._running = False

    # ── MQTT 回调 ─────────────────────────────────────

    def _on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            logger.info("MQTT 连接成功")
            client.subscribe(self._sub_topic)
            logger.info(f"已订阅: {self._sub_topic}")
        else:
            logger.error(f"MQTT 连接失败, rc={rc}")

    def _on_message(self, client, userdata, msg):
        """收到 STM32 发布的属性数据"""
        try:
            payload = msg.payload.decode("utf-8")
            data = json.loads(payload)

            # 解析 OneNET 兼容格式:
            # {"id":"123","params":{"hum":{"value":60},"tremp":{"value":25},...}}
            params = data.get("params", {})

            with self._lock:
                for key, val_obj in params.items():
                    if isinstance(val_obj, dict) and "value" in val_obj:
                        self._device_state[key] = val_obj["value"]
                    else:
                        self._device_state[key] = val_obj

                self._device_state["last_update"] = time.time()
                self._device_state["online"] = True

            logger.debug(f"设备数据更新: {params}")

        except Exception as e:
            logger.error(f"解析 MQTT 消息失败: {e}, topic={msg.topic}")

    def _on_disconnect(self, client, userdata, rc):
        if rc != 0:
            logger.warning(f"MQTT 意外断开, rc={rc}, 尝试重连...")
        with self._lock:
            self._device_state["online"] = False

    # ── 公共 API ──────────────────────────────────────

    def start(self):
        """启动 MQTT 客户端"""
        try:
            self._client.connect(self.host, self.port, self.keepalive)
            self._client.loop_start()
            self._running = True
            logger.info(f"MQTT 客户端已启动 ({self.host}:{self.port})")
        except Exception as e:
            logger.error(f"MQTT 连接失败: {e}")

    def stop(self):
        """停止 MQTT 客户端"""
        self._running = False
        self._client.loop_stop()
        self._client.disconnect()
        logger.info("MQTT 客户端已停止")

    def get_device_status(self) -> dict:
        """获取设备最新状态（供 FastAPI 查询）"""
        with self._lock:
            state = dict(self._device_state)

        # 兼容 OneNET API 格式（App 端已有解析逻辑）
        data_list = []
        mapping = {
            "tremp": "tremp",
            "hum": "hum",
            "position": "position",
            "limit_sw": "limit_sw",
        }
        for state_key, identifier in mapping.items():
            if state.get(state_key) is not None:
                data_list.append({
                    "identifier": identifier,
                    "value": str(state[state_key])
                })

        return {
            "data": data_list,
            "online": state.get("online", False),
            "last_update": state.get("last_update"),
        }

    def send_control(self, device_name: str, params: dict) -> bool:
        """
        发送控制命令到 STM32（替代 OneNET set-device-property）

        Args:
            device_name: 设备名（如 "esp8266"）
            params: 控制参数（如 {"led": true}）

        Returns:
            bool: 是否发送成功
        """
        topic = f"{self._cmd_topic_prefix}/{device_name}/property/set"
        payload = json.dumps({"params": params})

        try:
            result = self._client.publish(topic, payload, qos=1)
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                logger.info(f"控制命令已发送: topic={topic}, params={params}")
                return True
            else:
                logger.error(f"控制命令发送失败: rc={result.rc}")
                return False
        except Exception as e:
            logger.error(f"控制命令发送异常: {e}")
            return False

    @property
    def is_connected(self) -> bool:
        return self._client.is_connected()