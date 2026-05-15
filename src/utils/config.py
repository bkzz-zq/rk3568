"""配置文件加载模块"""

import os
import yaml


class Config:
    """全局配置管理"""

    _instance = None
    _config = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def load(self, config_path: str = None):
        """加载配置文件"""
        if config_path is None:
            # 默认配置路径
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            config_path = os.path.join(base_dir, "config", "config.yaml")

        if not os.path.exists(config_path):
            raise FileNotFoundError(f"配置文件不存在: {config_path}")

        with open(config_path, "r", encoding="utf-8") as f:
            self._config = yaml.safe_load(f)

        return self._config

    @property
    def data(self):
        """获取配置数据"""
        if self._config is None:
            self.load()
        return self._config

    def get(self, key: str, default=None):
        """获取配置项，支持点号分隔的嵌套键"""
        keys = key.split(".")
        value = self.data
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
            if value is None:
                return default
        return value


# 全局配置实例
config = Config()