"""图像处理工具模块"""

import cv2
import numpy as np
import base64


def resize_image(image: np.ndarray, scale: float = 0.5) -> np.ndarray:
    """按比例缩放图像"""
    if scale == 1.0:
        return image
    width = int(image.shape[1] * scale)
    height = int(image.shape[0] * scale)
    return cv2.resize(image, (width, height), interpolation=cv2.INTER_LINEAR)


def encode_image_to_base64(image: np.ndarray, quality: int = 70) -> str:
    """将图像编码为 base64 字符串"""
    encode_param = [cv2.IMWRITE_JPEG_QUALITY, quality]
    _, buffer = cv2.imencode(".jpg", image, encode_param)
    return base64.b64encode(buffer).decode("utf-8")


def decode_base64_to_image(base64_str: str) -> np.ndarray:
    """将 base64 字符串解码为图像"""
    img_data = base64.b64decode(base64_str)
    nparr = np.frombuffer(img_data, np.uint8)
    return cv2.imdecode(nparr, cv2.IMREAD_COLOR)


def draw_detections(
    image: np.ndarray,
    detections: list,
    color: tuple = (0, 255, 0),
    thickness: int = 2,
) -> np.ndarray:
    """
    在图像上绘制检测结果

    Args:
        image: 原始图像
        detections: 检测结果列表，每个元素为 dict:
            {"bbox": [x1, y1, x2, y2], "label": str, "confidence": float}
        color: 框颜色 (B, G, R)
        thickness: 线宽

    Returns:
        绘制后的图像
    """
    result = image.copy()
    for det in detections:
        x1, y1, x2, y2 = det["bbox"]
        label = det.get("label", "")
        conf = det.get("confidence", 0)

        # 绘制边界框
        cv2.rectangle(result, (int(x1), int(y1)), (int(x2), int(y2)), color, thickness)

        # 绘制标签
        text = f"{label} {conf:.2f}"
        font_scale = 0.6
        font_thickness = 1
        (text_w, text_h), _ = cv2.getTextSize(
            text, cv2.FONT_HERSHEY_SIMPLEX, font_scale, font_thickness
        )
        cv2.rectangle(
            result,
            (int(x1), int(y1) - text_h - 10),
            (int(x1) + text_w, int(y1)),
            color,
            -1,
        )
        cv2.putText(
            result,
            text,
            (int(x1), int(y1) - 5),
            cv2.FONT_HERSHEY_SIMPLEX,
            font_scale,
            (0, 0, 0),
            font_thickness,
        )

    return result


def letterbox(
    image: np.ndarray,
    new_shape: tuple = (640, 640),
    color: tuple = (114, 114, 114),
) -> tuple:
    """
    Letterbox 图像缩放，保持宽高比

    Returns:
        (缩放后的图像, 缩放比例, 填充量)
    """
    shape = image.shape[:2]  # (height, width)
    if isinstance(new_shape, int):
        new_shape = (new_shape, new_shape)

    r = min(new_shape[0] / shape[0], new_shape[1] / shape[1])
    new_unpad = (int(shape[1] * r), int(shape[0] * r))
    dw = new_shape[1] - new_unpad[0]
    dh = new_shape[0] - new_unpad[1]

    dw /= 2
    dh /= 2

    if shape[::-1] != new_unpad:
        image = cv2.resize(image, new_unpad, interpolation=cv2.INTER_LINEAR)

    top, bottom = int(round(dh - 0.1)), int(round(dh + 0.1))
    left, right = int(round(dw - 0.1)), int(round(dw + 0.1))
    image = cv2.copyMakeBorder(image, top, bottom, left, right, cv2.BORDER_CONSTANT, value=color)

    return image, r, (dw, dh)