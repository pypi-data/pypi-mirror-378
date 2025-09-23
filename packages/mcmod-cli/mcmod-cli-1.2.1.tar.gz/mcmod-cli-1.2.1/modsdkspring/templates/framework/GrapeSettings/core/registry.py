# -*- coding: utf-8 -*-
"""基于 ConfigClient 的配置注册表读写工具。"""

from ..constants import CONFIG_REGISTRY_KEY
from .client_context import get_config_client


class ConfigRegistry(object):
    """对共享配置注册表的简单包装。"""

    def __init__(self, config_client=None):
        self._config_client = config_client or get_config_client()

    def read_all(self):
        """读取完整的注册表数据字典。"""
        registry = self._config_client.GetConfigData(CONFIG_REGISTRY_KEY, False)
        return registry if isinstance(registry, dict) else {}

    def write_all(self, registry):
        """写回注册表字典。"""
        self._config_client.SetConfigData(CONFIG_REGISTRY_KEY, registry or {}, False)

    def clear(self):
        """将注册表清空为一个空字典。"""
        self.write_all({})

    @staticmethod
    def sort_entries(registry):
        """按 priority 字段对配置项排序并返回列表。"""
        if not registry:
            return []
        return sorted(
            registry.items(),
            key=lambda item: item[1].get('priority', float('inf'))
        )
