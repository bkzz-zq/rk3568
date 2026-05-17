"""RK3568 智能视觉识别系统 - 多线程流水线架构

流水线:
  线程1 (CameraStream): GStreamer 硬解码 → 最新帧缓存
  线程2 (检测线程):     取帧 → 缩放 → NPU行人+CPU车牌并行 → 结果缓存
  主线程 (推送线程):     读缓存结果 → WebSocket推送 → FPS统计
"""

import os
import sys
import time
import signal
import argparse
import threading
import cv2
from concurrent.futures import ThreadPoolExecutor, as_completed

# 将项目根目录添加到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.config import config
from src.utils.logger import setup_logger
from src.camera import CameraStream
from src.detector.person import PersonDetector
from src.detector.plate import PlateDetector
from src.pusher.ws_pusher import WebSocketPusher


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="RK3568 智能视觉识别系统")
    parser.add_argument("--config", type=str, default=None, help="配置文件路径")
    parser.add_argument("--no-npu", action="store_true", help="禁用 NPU，使用 CPU")
    parser.add_argument("--no-person", action="store_true", help="禁用行人检测")
    parser.add_argument("--no-plate", action="store_true", help="禁用车牌识别")
    args = parser.parse_args()

    # 加载配置
    config.load(args.config)
    logger = setup_logger(config=config.get("logging"))

    logger.info("=" * 60)
    logger.info("RK3568 智能视觉识别系统启动（多线程流水线）")
    logger.info("=" * 60)

    # NPU 配置
    npu_enabled = config.get("npu.enabled", False) and not args.no_npu
    logger.info(f"NPU 加速: {'开启' if npu_enabled else '关闭'}")

    # 初始化摄像头
    camera_config = config.get("camera")
    camera = CameraStream(camera_config)
    if not camera.connect():
        logger.error("摄像头连接失败，退出")
        sys.exit(1)

    # 初始化检测器
    person_detector = None
    plate_detector = None
    # 行人检测
    if config.get("person_detection.enabled", True) and not args.no_person:
        person_config = config.get("person_detection")
        person_detector = PersonDetector(person_config, npu_enabled=npu_enabled)
        if person_detector.load_model():
            logger.info("✓ 行人检测模块就绪")
        else:
            logger.warning("✗ 行人检测模块加载失败")
            person_detector = None

    # 车牌识别（HyperLPR3 CPU模式）
    if config.get("plate_recognition.enabled", True) and not args.no_plate:
        plate_config = config.get("plate_recognition")
        plate_detector = PlateDetector(plate_config, npu_enabled=False)
        if plate_detector.load_model():
            logger.info("✓ 车牌识别模块就绪")
        else:
            logger.warning("✗ 车牌识别模块加载失败")
            plate_detector = None

    # 初始化 WebSocket 推送
    ws_config = config.get("websocket")
    pusher = WebSocketPusher(ws_config)
    pusher.start()

    # ── 主运行标志（供 signal_handler / sensor_collect_loop 使用）──
    running = True

    # ── 智能家居 IoT 服务 ──────────────────────────────
    mqtt_client = None
    iot_server_thread = None
    sensor_collect_timer = None

    if config.get("iot.enabled", False):
        try:
            from src.iot.mqtt_client import MQTTClient
            from src.iot.server import run_server, set_mqtt_client, set_camera, collect_sensor_data

            # 启动 MQTT 客户端
            mqtt_config = config.get("iot.mqtt", {})
            mqtt_client = MQTTClient(mqtt_config)
            mqtt_client.start()

            # 注入到 FastAPI
            set_mqtt_client(mqtt_client)

            # 注入摄像头引用（供 MJPEG 视频流使用）
            # detect_scale: 将 1920x1080 坐标缩放到当前帧分辨率（0.33）
            detect_scale = getattr(camera, 'output_scale', 1.0)
            set_camera(camera, detect_scale)

            # 启动 FastAPI 服务（独立线程）
            server_config = config.get("iot.server", {})
            iot_server_thread = threading.Thread(
                target=run_server,
                kwargs={
                    "host": server_config.get("host", "0.0.0.0"),
                    "port": server_config.get("port", 8000),
                },
                daemon=True,
            )
            iot_server_thread.start()
            logger.info("✓ 智能家居 IoT 服务已启动")

            # 传感器数据采集定时器
            collect_interval = config.get("iot.sensor_collect_interval", 180)

            def sensor_collect_loop():
                while running:
                    time.sleep(collect_interval)
                    collect_sensor_data()

            sensor_collect_timer = threading.Thread(target=sensor_collect_loop, daemon=True)
            sensor_collect_timer.start()

        except ImportError as e:
            logger.warning(f"智能家居模块导入失败（缺少依赖）: {e}")
            logger.warning("安装: pip install fastapi uvicorn paho-mqtt PyJWT")
        except Exception as e:
            logger.warning(f"智能家居服务启动失败: {e}")

    # 启动视频流（线程1: 解码）
    camera.start()

    # 信号处理
    def signal_handler(sig, frame):
        nonlocal running
        logger.info("收到退出信号，正在停止...")
        running = False

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # ── 共享检测结果（线程安全）──────────────────────────
    results_lock = threading.Lock()
    cached_results = {
        "persons": None,
        "plates": None,
    }

    # ── 线程2: 检测线程 ─────────────────────────────────
    detect_running = True

    def detection_loop():
        """检测线程：持续取帧 → 缩放 → 检测 → 更新缓存"""
        DETECT_WIDTH = 640
        PERSON_INTERVAL = 3       # 行人检测：每3帧检测一次
        PLATE_INTERVAL = 3        # 车牌检测：每3帧检测一次
        PLATE_UPSAMPLE = 2.0      # 车牌检测前上采样倍数（640x360→1280x720）
        detect_scale = None
        frame_count = 0

        # 检测内部并行线程池
        executor = ThreadPoolExecutor(max_workers=3)

        logger.info("检测线程已启动")

        while detect_running:
            frame = camera.get_frame()
            if frame is None:
                time.sleep(0.005)
                continue

            frame_count += 1
            h, w = frame.shape[:2]

            # 计算缩放比例（仅第一次）
            if detect_scale is None:
                if camera.decode_mode == "gst_hw":
                    # GStreamer 已缩放，用 output_scale 还原坐标到原始分辨率
                    detect_scale = camera.output_scale
                    logger.info(f"检测缩放: GStreamer 已缩放，output_scale={detect_scale:.2f}")
                else:
                    detect_scale = DETECT_WIDTH / w
                    logger.info(f"检测缩放: {w}x{h} → {int(w * detect_scale)}x{int(h * detect_scale)} "
                                f"(scale={detect_scale:.2f})")

            # 判断本轮需要哪些检测
            need_person = (frame_count % PERSON_INTERVAL == 0)
            need_plate = (frame_count % PLATE_INTERVAL == 0)

            if not need_person and not need_plate:
                continue

            # 缩小分辨率用于检测（GStreamer 硬解码已缩放，无需再 resize）
            if camera.decode_mode == "gst_hw":
                small_frame = frame
            else:
                small_frame = cv2.resize(
                    frame, None, fx=detect_scale, fy=detect_scale,
                    interpolation=cv2.INTER_LINEAR
                )

            # 提交并行检测任务
            futures = {}

            if person_detector is not None and need_person:
                futures[executor.submit(person_detector.detect, small_frame)] = "person"

            if plate_detector is not None and need_plate:
                # 上采样提升车牌识别率（640x360 → 1280x720）
                plate_frame = cv2.resize(
                    frame, None, fx=PLATE_UPSAMPLE, fy=PLATE_UPSAMPLE,
                    interpolation=cv2.INTER_LINEAR
                )
                futures[executor.submit(plate_detector.detect, plate_frame)] = "plate"

            # 收集并行检测结果
            new_persons = None
            new_plates = None

            for future in as_completed(futures):
                name = futures[future]
                try:
                    result = future.result()

                    if name == "person":
                        # 坐标从小图还原到原图
                        for r in result:
                            r["bbox"] = [int(v / detect_scale) for v in r["bbox"]]
                        new_persons = result

                    elif name == "plate":
                        # 坐标从上采样帧还原到原图（先除以上采样倍数，再除以detect_scale）
                        plate_scale = detect_scale * PLATE_UPSAMPLE
                        for r in result:
                            r["bbox"] = [int(v / plate_scale) for v in r["bbox"]]
                        new_plates = result

                except Exception as e:
                    logger.error(f"{name} 检测异常: {e}")

            # 更新缓存结果（快速加锁）
            with results_lock:
                if new_persons is not None:
                    cached_results["persons"] = new_persons
                if new_plates is not None:
                    cached_results["plates"] = new_plates
        executor.shutdown(wait=False)
        logger.info("检测线程已退出")

    # 启动检测线程
    detect_thread = threading.Thread(target=detection_loop, daemon=True)
    detect_thread.start()

    # ── 主线程: 推送循环 ────────────────────────────────
    logger.info("主推送循环已启动")
    logger.info(f"WebSocket 客户端连接数: {pusher.client_count}")

    fps_frame_count = 0
    fps_start_time = time.time()
    fps = 0.0

    try:
        while running:
            # 读取缓存结果（不等待检测完成）
            with results_lock:
                persons = cached_results["persons"]
                plates = cached_results["plates"]
            # 同步 AI 结果到 IoT 服务器
            if mqtt_client is not None:
                try:
                    from src.iot.server import set_ai_results
                    set_ai_results(persons, plates)
                except Exception:
                    pass

            # 推送检测结果
            pusher.push_results(
                persons=persons,
                plates=plates,
                fps=fps,
                plate_roi=plate_detector.roi if plate_detector else None,
            )

            # FPS 统计
            fps_frame_count += 1
            elapsed = time.time() - fps_start_time
            if elapsed >= 1.0:
                fps = fps_frame_count / elapsed
                fps_frame_count = 0
                fps_start_time = time.time()

                summary_parts = []
                if persons is not None:
                    summary_parts.append(f"行人:{len(persons)}")
                if plates is not None:
                    summary_parts.append(f"车牌:{len(plates)}")
                logger.info(
                    f"FPS: {fps:.1f} | {', '.join(summary_parts)} | "
                    f"客户端: {pusher.client_count} | "
                    f"解码: {camera.decode_mode}"
                )

            # 推送频率控制（避免空转占 CPU）
            time.sleep(0.02)  # ~50fps 上限

    except KeyboardInterrupt:
        logger.info("用户中断")
    finally:
        # 停止检测线程
        detect_running = False
        detect_thread.join(timeout=3)

        # 清理资源
        logger.info("正在释放资源...")
        camera.stop()

        if person_detector is not None:
            person_detector.release()
        if plate_detector is not None:
            plate_detector.release()
        pusher.stop()

        # 停止 IoT 服务
        if mqtt_client is not None:
            mqtt_client.stop()

        logger.info("系统已停止")


if __name__ == "__main__":
    main()