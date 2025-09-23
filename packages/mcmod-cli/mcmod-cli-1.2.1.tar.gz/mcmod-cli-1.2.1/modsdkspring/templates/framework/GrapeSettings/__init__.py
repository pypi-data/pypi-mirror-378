# -*- coding: utf-8 -*-
"""重构后的 GrapeSettings 插件对外暴露的接口。"""

from .core import (
    get_engine_factory,
    get_level_id,
    get_game,
    get_config_client,
    ConfigRegistry,
)
from .handlers import EventHandler
from .managers import ConfigManager
from .ui import UIManager

__all__ = [
    'ConfigManager',
    'EventHandler',
    'UIManager',
    'ConfigRegistry',
    'get_engine_factory',
    'get_level_id',
    'get_game',
    'get_config_client',
]
