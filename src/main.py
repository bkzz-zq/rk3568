"""RK3568 智能视觉识别系统 - 主入口"""

import os
import sys
import time
import signal
import argparse
import cv2
from concurrent.futures import ThreadPoolExecutor, as_completed

# 将项目根目录添加到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.config import config
from src.utils.logger import setup_logger
from src.camera import CameraStream
from src.detector.person import PersonDetector
from src.detector.plate import PlateDetector
from src.detector.ocr import OCRDetector
from src.pusher.ws_pusher import WebSocketPusher


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="RK3568 智能视觉识别系统")
    parser.add_argument("--config", type=str, default=None, help="配置文件路径")
    parser.add_argument("--no-npu", action="store_true", help="禁用 NPU，使用 CPU")
    parser.add_argument("--no-person", action="store_true", help="禁用行人检测")
    parser.add_argument("--no-plate", action="store_true", help="禁用车牌识别")
    parser.add_argument("--no-ocr", action="store_true", help="禁用文字识别")
    args = parser.parse_args()

    # 加载配置
    config.load(args.config)
    logger = setup_logger(config=config.get("logging"))

    logger.info("=" * 60)
    logger.info("RK3568 智能视觉识别系统启动")
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
    ocr_detector = None

    # 行人检测
    if config.get("person_detection.enabled", True) and not args.no_person:
        person_config = config.get("person_detection")
        person_detector = PersonDetector(person_config, npu_enabled=npu_enabled)
        if person_detector.load_model():
            logger.info("✓ 行人检测模块就绪")
        else:
            logger.warning("✗ 行人检测模块加载失败")
            person_detector = None

    # 车牌识别
    if config.get("plate_recognition.enabled", True) and not args.no_plate:
        plate_config = config.get("plate_recognition")
        plate_detector = PlateDetector(plate_config, npu_enabled=npu_enabled)
        if plate_detector.load_model():
            logger.info("✓ 车牌识别模块就绪")
        else:
            logger.warning("✗ 车牌识别模块加载失败")
            plate_detector = None

    # 文字识别
    if config.get("ocr.enabled", True) and not args.no_ocr:
        ocr_config = config.get("ocr")
        ocr_detector = OCRDetector(ocr_config)
        if ocr_detector.load_model():
            logger.info("✓ 文字识别模块就绪")
        else:
            logger.warning("✗ 文字识别模块加载失败")
            ocr_detector = None

    # 初始化 WebSocket 推送
    ws_config = config.get("websocket")
    pusher = WebSocketPusher(ws_config)
    pusher.start()

    # 启动视频流
    camera.start()

    # 信号处理
    running = True

    def signal_handler(sig, frame):
        nonlocal running
        logger.info("收到退出信号，正在停止...")
        running = False

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # 检测优化参数
    DETECT_WIDTH = 640           # 检测时缩放到的宽度
    DETECT_INTERVAL = 3          # 行人检测：每隔几帧做一次检测
    PLATE_DETECT_INTERVAL = 9    # 车牌检测：每隔几帧做一次（CPU密集，降低频率）
    DETECT_SCALE = None          # 缓存缩放比例

    # 并行检测线程池
    detector_executor = ThreadPoolExecutor(max_workers=3)

    # 主循环
    logger.info("开始实时检测...")
    logger.info(f"检测优化: 缩放到 {DETECT_WIDTH}px, 每 {DETECT_INTERVAL} 帧检测一次, 并行检测")
    logger.info(f"WebSocket 客户端连接数: {pusher.client_count}")

    frame_count = 0
    fps_start_time = time.time()
    fps = 0.0

    # 缓存上一次检测结果（用于非检测帧的推送）
    last_persons = None
    last_plates = None
    last_texts = None

    # 辅助函数：检测并还原坐标
    def _detect_and_rescale(detector, frame, scale):
        results = detector.detect(frame)
        for r in results:
            r["bbox"] = [int(v / scale) for v in r["bbox"]]
        return results

    try:
        while running:
            # 获取帧
            frame = camera.get_frame()
            if frame is None:
                time.sleep(0.01)
                continue

            frame_count += 1
            h, w = frame.shape[:2]

            # 计算检测缩放比例（仅第一次）
            if DETECT_SCALE is None:
                DETECT_SCALE = DETECT_WIDTH / w
                logger.info(f"检测缩放比例: {DETECT_SCALE:.2f} ({w}x{h} -> {int(w*DETECT_SCALE)}x{int(h*DETECT_SCALE)})")

            # 降频检测：行人每 DETECT_INTERVAL 帧，车牌每 PLATE_DETECT_INTERVAL 帧
            need_person_detect = (frame_count % DETECT_INTERVAL == 0)
            need_plate_detect = (frame_count % PLATE_DETECT_INTERVAL == 0)
            need_ocr_detect = need_plate_detect  # OCR 跟随车牌频率
            need_detect = need_person_detect or need_plate_detect or (ocr_detector is not None and need_ocr_detect)

            if need_detect:
                # 缩小分辨率用于检测
                if DETECT_SCALE != 1.0:
                    small_frame = cv2.resize(frame, None, fx=DETECT_SCALE, fy=DETECT_SCALE, interpolation=cv2.INTER_LINEAR)
                else:
                    small_frame = frame

                # 按需提交检测任务
                futures = {}
                # 行人检测用缩小帧（NPU 处理，速度快）
                if person_detector is not None and need_person_detect:
                    futures[detector_executor.submit(
                        _detect_and_rescale, person_detector, small_frame, DETECT_SCALE
                    )] = "person"
                # 车牌检测用原始帧（1080p，车牌更清晰，识别更准）
                if plate_detector is not None and need_plate_detect:
                    futures[detector_executor.submit(
                        plate_detector.detect, frame
                    )] = "plate"
                if ocr_detector is not None and need_ocr_detect:
                    futures[detector_executor.submit(
                        _detect_and_rescale, ocr_detector, small_frame, DETECT_SCALE
                    )] = "ocr"

                # 收集并行检测结果
                for future in as_completed(futures):
                    name = futures[future]
                    try:
                        result = future.result()
                        if name == "person":
                            last_persons = result
                        elif name == "plate":
                            last_plates = result
                        elif name == "ocr":
                            last_texts = result
                    except Exception as e:
                        logger.error(f"{name} 检测异常: {e}")

            # 使用缓存的检测结果
            persons = last_persons
            plates = last_plates
            texts = last_texts

            # 推送检测结果（仅 JSON，无图像编码开销）
            pusher.push_results(
                persons=persons,
                plates=plates,
                texts=texts,
                fps=fps,
                plate_roi=plate_detector.roi if plate_detector else None,
            )

            # 计算 FPS
            elapsed = time.time() - fps_start_time
            if elapsed >= 1.0:
                fps = frame_count / elapsed
                frame_count = 0
                fps_start_time = time.time()

                summary_parts = []
                if persons is not None:
                    summary_parts.append(f"行人:{len(persons)}")
                if plates is not None:
                    summary_parts.append(f"车牌:{len(plates)}")
                if texts is not None:
                    summary_parts.append(f"文字:{len(texts)}")

                logger.info(
                    f"FPS: {fps:.1f} | {', '.join(summary_parts)} | 客户端: {pusher.client_count}"
                )

    except KeyboardInterrupt:
        logger.info("用户中断")
    finally:
        # 清理资源
        logger.info("正在释放资源...")
        detector_executor.shutdown(wait=False)
        camera.stop()

        if person_detector is not None:
            person_detector.release()
        if plate_detector is not None:
            plate_detector.release()
        if ocr_detector is not None:
            ocr_detector.release()

        pusher.stop()
        logger.info("系统已停止")


if __name__ == "__main__":
    main()