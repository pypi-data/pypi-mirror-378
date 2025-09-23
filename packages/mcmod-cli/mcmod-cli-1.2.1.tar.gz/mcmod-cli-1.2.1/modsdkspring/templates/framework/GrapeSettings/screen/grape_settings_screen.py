# -*- coding: utf-8 -*-
"""展示所有已注册配置入口的界面。"""

import mod.client.extraClientApi as clientApi
from mod_log import logger

from ..constants import LOG_MESSAGES
from ..handlers.event_handler import EventHandler
from ..managers.config_manager import ConfigManager
from ..ui.ui_manager import UIManager

ScreenNode = clientApi.GetScreenNodeCls()


class GrapeSettingsScreen(ScreenNode):
    """组合配置管理、UI 管理和事件处理的主界面。"""

    def __init__(self, namespace, name, param):
        ScreenNode.__init__(self, namespace, name, param)

        self.config_manager = ConfigManager()
        self.ui_manager = UIManager(self)
        self.event_handler = EventHandler(self.config_manager, self.ui_manager)

        logger.info(LOG_MESSAGES['INIT_COMPLETE'])

    def Create(self):
        """初始化界面，创建按钮列表。"""
        logger.info(LOG_MESSAGES['CREATE_START'])

        self.SetScreenVisible(False)

        if not self.ui_manager.setup_main_controls():
            return

        self.ui_manager.setup_close_button(self.event_handler.on_close_button_touch)
        self.register_configs()

        logger.info(LOG_MESSAGES['CREATE_COMPLETE'])

    def SetGlowingButton(self, button_name):
        self.event_handler.set_glowing_button(button_name)
        self.event_handler.update_current_config(button_name)

    def SetScrollingPercent(self, value):
        self.ui_manager.set_scroll_position(value)

    def register_configs(self):
        """读取注册表并刷新按钮列表。"""
        if not self.config_manager.load_configs():
            return

        # 如果没有选中任何按钮，自动选中排行第一的配置（在创建按钮之前）
        if not self.event_handler.get_glowing_button():
            sorted_configs = self.config_manager.get_sorted_configs()
            if sorted_configs:
                first_config_name = sorted_configs[0][0]
                self.event_handler.set_glowing_button(first_config_name)
                # 立即跳转到该配置界面
                self.event_handler.navigate_to_default_config(first_config_name)

        self.ui_manager.adjust_scroll_content_size(
            self.config_manager.get_configs_count()
        )
        self._create_config_buttons()
        self.event_handler.update_current_config(
            self.event_handler.get_glowing_button()
        )

    def _create_config_buttons(self):
        """按排序结果创建配置按钮。"""
        for key, config in self.config_manager.get_sorted_configs():
            if self.config_manager.validate_config(key, config):
                self._create_single_button(config)

    def _create_single_button(self, config):
        """创建单个配置按钮并与事件处理器联动。"""
        button = self.ui_manager.create_config_button(
            config['config_name'],
            config['config_text'],
            config['config_icon'],
            self.event_handler.on_config_button_touch_down,
            self.event_handler.on_config_button_touch_up,
        )

        if button and config['config_name'] == self.event_handler.get_glowing_button():
            self.ui_manager.set_button_selected(button)
