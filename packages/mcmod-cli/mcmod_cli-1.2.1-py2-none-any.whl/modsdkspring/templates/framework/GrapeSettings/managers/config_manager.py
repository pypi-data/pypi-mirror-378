# -*- coding: utf-8 -*-
"""负责加载与校验 GrapeSettings 配置项的管理器。"""

from mod_log import logger

from ..constants import (
    LOG_MESSAGES,
    ERROR_MESSAGES,
    REQUIRED_CONFIG_FIELDS,
    REQUIRED_NAVIGATION_FIELDS,
)
from ..core.registry import ConfigRegistry


class ConfigManager(object):
    """从共享注册表中加载、缓存并校验配置项。"""

    def __init__(self, registry=None):
        self._registry = registry or ConfigRegistry()
        self.configs = {}
        self.sorted_configs = []

    def load_configs(self):
        """刷新本地缓存，读取全部配置项。"""
        self.configs = self._registry.read_all()

        if not self.configs:
            logger.warning(LOG_MESSAGES['NO_CONFIGS'])
            self.sorted_configs = []
            return False

        self.sorted_configs = ConfigRegistry.sort_entries(self.configs)
        return True

    def validate_config(self, key, config):
        """校验展示所需的基础字段是否齐全。"""
        return self._validate_fields(key, config, REQUIRED_CONFIG_FIELDS)

    def validate_navigation_config(self, key, config):
        """校验跳转详细界面所需字段是否齐全。"""
        return self._validate_fields(key, config, REQUIRED_NAVIGATION_FIELDS)

    def get_config(self, config_name):
        """返回指定名称的原始配置数据。"""
        return self.configs.get(config_name)

    def get_sorted_configs(self):
        """返回排序后的 (名称, 配置) 列表副本。"""
        return list(self.sorted_configs)

    def get_configs_count(self):
        """返回缓存中的配置数量。"""
        return len(self.configs)

    def config_exists(self, config_name):
        """判断某个配置名称是否存在。"""
        return config_name in self.configs

    def _validate_fields(self, key, config, required_fields):
        """通用字段校验逻辑。"""
        if not isinstance(config, dict):
            logger.error(ERROR_MESSAGES['CONFIG_NOT_EXIST'].format(key))
            return False

        for field in required_fields:
            if field not in config:
                logger.error(ERROR_MESSAGES['MISSING_FIELD'].format(key, field))
                return False
        return True
