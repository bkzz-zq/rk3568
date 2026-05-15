"""日志模块"""

import os
import logging
from logging.handlers import RotatingFileHandler


def setup_logger(name: str = "rk3568_vision", config: dict = None) -> logging.Logger:
    """
    设置日志记录器

    Args:
        name: 日志记录器名称
        config: 日志配置字典

    Returns:
        配置好的 Logger 实例
    """
    logger = logging.getLogger(name)

    # 默认配置
    log_level = "INFO"
    log_file = "logs/app.log"
    max_size = 10  # MB
    backup_count = 5

    if config:
        log_level = config.get("level", "INFO")
        log_file = config.get("file", "logs/app.log")
        max_size = config.get("max_size", 10)
        backup_count = config.get("backup_count", 5)

    logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))

    # 日志格式
    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # 控制台输出
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # 文件输出
    log_dir = os.path.dirname(log_file)
    if log_dir:
        os.makedirs(log_dir, exist_ok=True)

    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=max_size * 1024 * 1024,
        backupCount=backup_count,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger