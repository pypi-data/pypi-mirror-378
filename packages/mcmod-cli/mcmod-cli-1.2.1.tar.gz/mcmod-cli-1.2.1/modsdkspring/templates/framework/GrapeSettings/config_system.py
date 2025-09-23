# -*- coding: utf-8 -*-
"""负责把 GrapeSettings 接入暂停菜单的客户端系统。"""

import mod.client.extraClientApi as clientApi
from mod_log import logger

from ...modCommon.GrapeSettings import grape_settings_config
from ...modCommon.modConfig import SCRIPT_PATH
from .core.client_context import get_game, get_config_client
from .core.registry import ConfigRegistry

NativeScreenManager = clientApi.GetNativeScreenManagerCls()
ClientSystem = clientApi.GetClientSystemCls()

PROXY_SCREEN_PATH = "pause.pause_screen"
UI_INIT_DELAY = 1  # 秒


class ConfigSystem(ClientSystem):
    """负责注册配置项、代理 ESC 界面以及动态注册 UI。"""

    def __init__(self, namespace, systemName):
        ClientSystem.__init__(self, namespace, systemName)
        logger.info("ConfigSystem: 初始化配置系统")

        self.registry = ConfigRegistry(get_config_client())
        self.game = get_game()

        self._init_config_registry()
        self._register_ui_init_listener()

    def _init_config_registry(self):
        """保证注册表存在并被清空。"""
        try:
            self.registry.clear()
            logger.info("ConfigSystem: 配置注册表已初始化")
        except Exception as exc:
            logger.error("ConfigSystem: 初始化配置注册表失败 - %s" % str(exc))

    def _register_ui_init_listener(self):
        """监听 UI 初始化事件，以便延迟注册按钮和界面。"""
        try:
            self.ListenForEvent(
                clientApi.GetEngineNamespace(),
                clientApi.GetEngineSystemName(),
                "UiInitFinished",
                self,
                self.OnUIInitFinished,
            )
            logger.info("ConfigSystem: UI 初始化事件监听已注册")
        except Exception as exc:
            logger.error("ConfigSystem: 注册 UI 初始化监听失败 - %s" % str(exc))

    def OnUIInitFinished(self, args):
        """UI 初始化完毕后注册模组配置并尝试挂载代理按钮。"""
        logger.info('ConfigSystem: UI 初始化完成，开始注册配置')

        try:
            # 自动扫描并注册所有配置项
            configs = self._discover_all_configs()
            logger.info('ConfigSystem: 发现 %d 个配置项' % len(configs))

            for config in configs:
                self.register_config(config)

            # 注册完所有配置后，找到最高优先级的配置来判断代理
            if configs:
                self.game.AddTimer(UI_INIT_DELAY, self._try_register_proxy_for_highest_priority)
            else:
                logger.warning("ConfigSystem: 未发现任何配置项")

        except Exception as exc:
            logger.error("ConfigSystem: 处理 UI 初始化逻辑失败 - %s" % str(exc))

    def _discover_all_configs(self):
        """自动发现模块中所有以 _config 结尾的配置项。"""
        configs = []
        try:
            # 获取模块中所有属性
            for attr_name in dir(grape_settings_config):
                if attr_name.endswith('_config') and not attr_name.startswith('_'):
                    attr_value = getattr(grape_settings_config, attr_name)
                    if isinstance(attr_value, dict) and 'config_name' in attr_value:
                        configs.append(attr_value)
                        logger.info('ConfigSystem: 发现配置项 - %s' % attr_name)

        except Exception as exc:
            logger.error("ConfigSystem: 扫描配置项失败 - %s" % str(exc))

        return configs

    def _try_register_proxy_for_highest_priority(self):
        """找到最高优先级配置并尝试注册代理。"""
        try:
            registry = self.registry.read_all()
            if not registry:
                logger.warning("ConfigSystem: 配置注册表为空，无法注册代理")
                return

            sorted_configs = ConfigRegistry.sort_entries(registry)
            if not sorted_configs:
                logger.warning("ConfigSystem: 排序后配置列表为空")
                return

            highest_priority_name = sorted_configs[0][0]
            logger.info('ConfigSystem: 最高优先级配置 - %s' % highest_priority_name)

            self._register_screen_proxy()
            self._register_config_ui()

        except Exception as exc:
            logger.error("ConfigSystem: 注册最高优先级代理失败 - %s" % str(exc))

    def try_proxy_config_screen(self, config_name):
        """判断是否需要成为暂停菜单中的最高优先级设置并注册代理。"""
        logger.info("ConfigSystem: 评估配置优先级 - %s" % config_name)

        try:
            if self.is_highest_priority(config_name):
                logger.info('ConfigSystem: 检测到最高优先级配置 - %s' % config_name)
                self._register_screen_proxy()
                self._register_config_ui()
            else:
                logger.info('ConfigSystem: 当前配置非最高优先级 - %s' % config_name)

        except Exception as exc:
            logger.error("ConfigSystem: 代理配置界面失败 - %s" % str(exc))

    def _register_screen_proxy(self):
        """在暂停菜单注册 ESC 按钮代理。"""
        try:
            NativeScreenManager.instance().RegisterScreenProxy(
                PROXY_SCREEN_PATH,
                SCRIPT_PATH + ".plugins.GrapeSettings.proxy.esc_ui_proxy.escUIProxy",
            )
            logger.info("ConfigSystem: 暂停界面代理注册成功")
        except Exception as exc:
            logger.error("ConfigSystem: 暂停界面代理注册失败 - %s" % str(exc))

    def _register_config_ui(self):
        """注册 GrapeSettings 主界面的 UI 脚本。"""
        try:
            clientApi.RegisterUI(
                grape_settings_config.MOD_NAMESPACE,
                "GrapeSettings",
                SCRIPT_PATH + ".plugins.GrapeSettings.screen.grape_settings_screen.GrapeSettingsScreen",
                "grape_settings.main",
            )
            logger.info("ConfigSystem: 配置 UI 注册成功")
        except Exception as exc:
            logger.error("ConfigSystem: 配置 UI 注册失败 - %s" % str(exc))

    def register_config(self, config_data):
        """将单个配置写入注册表，并根据需要注册其 UI。"""
        if not isinstance(config_data, dict):
            logger.error("ConfigSystem: 跳过 - 配置需要字典类型")
            return

        config_name = config_data.get("config_name")
        if not config_name:
            logger.error("ConfigSystem: 跳过 - 缺少 config_name 字段")
            return

        logger.info('ConfigSystem: 注册配置 - %s' % config_name)

        try:
            registry = self.registry.read_all()
            registry[config_name] = config_data
            self.registry.write_all(registry)

            logger.info('ConfigSystem: 配置注册成功 - %s' % config_name)
            self._register_ui_if_needed(config_data)

        except Exception as exc:
            logger.error("ConfigSystem: 注册配置失败 - %s" % str(exc))

    def _register_ui_if_needed(self, config_data):
        """当配置提供 UI 信息时，动态注册对应界面。"""
        required_fields = ['mod_name_space', 'ui_namespace', 'python_path']

        if all(field in config_data for field in required_fields):
            try:
                clientApi.RegisterUI(
                    config_data['mod_name_space'],
                    config_data['ui_namespace'],
                    config_data['python_path'],
                    config_data['ui_namespace'] + '.main',
                )
                logger.info("ConfigSystem: 动态配置 UI 注册成功 - %s" % config_data['ui_namespace'])
            except Exception as exc:
                logger.error("ConfigSystem: 动态配置 UI 注册失败 - %s" % str(exc))

    def is_highest_priority(self, config_name):
        """检查给定配置是否拥有最高优先级。"""
        try:
            registry = self.registry.read_all()

            if not registry:
                logger.warning("ConfigSystem: 配置注册表为空")
                return False

            if config_name not in registry:
                logger.warning("ConfigSystem: 未找到配置: %s" % config_name)
                return False

            sorted_configs = ConfigRegistry.sort_entries(registry)
            if not sorted_configs:
                return False

            highest_priority_name = sorted_configs[0][0]
            return highest_priority_name == config_name

        except Exception as exc:
            logger.error("ConfigSystem: 计算优先级失败 - %s" % str(exc))
            return False
