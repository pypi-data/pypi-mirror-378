# -*- coding: utf-8 -*-
"""GrapeSettings 插件使用的引擎组件获取辅助方法。"""

import mod.client.extraClientApi as clientApi

_engine_factory = None
_level_id = None
_game = None
_config_client = None


def get_engine_factory():
    """返回缓存的引擎组件工厂。"""
    global _engine_factory
    if _engine_factory is None:
        _engine_factory = clientApi.GetEngineCompFactory()
    return _engine_factory


def get_level_id():
    """返回当前关卡的 levelId。"""
    global _level_id
    if _level_id is None:
        _level_id = clientApi.GetLevelId()
    return _level_id


def get_game():
    """返回共用的 Game 组件实例。"""
    global _game
    if _game is None:
        _game = get_engine_factory().CreateGame(get_level_id())
    return _game


def get_config_client():
    """返回用于读写注册表的 ConfigClient 组件。"""
    global _config_client
    if _config_client is None:
        _config_client = get_engine_factory().CreateConfigClient(get_level_id())
    return _config_client
