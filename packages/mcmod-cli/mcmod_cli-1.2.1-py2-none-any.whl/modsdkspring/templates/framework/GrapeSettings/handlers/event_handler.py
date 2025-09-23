# -*- coding: utf-8 -*-
"""模组设置总览界面的事件响应逻辑。"""

import mod.client.extraClientApi as clientApi
from mod_log import logger

from ..constants import TOUCH_DELAY, ERROR_MESSAGES, LOG_MESSAGES
from ..core.client_context import get_game


game = get_game()


class EventHandler(object):
    """负责处理按钮交互并跳转到对应的配置界面。"""

    def __init__(self, config_manager, ui_manager):
        self.config_manager = config_manager
        self.ui_manager = ui_manager
        self.touch_pos = [0, 0]
        self.current_config = {}
        self.glowing_button = ""

    def on_close_button_touch(self, args):
        """处理关闭按钮点击。"""
        logger.info(LOG_MESSAGES['CLOSE_BUTTON'])
        clientApi.PopScreen()

    def on_config_button_touch_down(self, args):
        """记录按钮按下时的触控坐标，用于校验非法滑动。"""
        self.touch_pos = [
            args.get('TouchPosX', 0),
            args.get('TouchPosY', 0)
        ]

    def on_config_button_touch_up(self, args):
        """在按钮抬起时跳转到对应的配置界面。"""
        try:
            current_pos = [args.get('TouchPosX', -1), args.get('TouchPosY', -1)]

            if current_pos != self.touch_pos:
                logger.info(LOG_MESSAGES['INVALID_CLICK'])
                return

            button_name = self._extract_button_name(args.get('ButtonPath', ''))
            if not button_name:
                logger.error(ERROR_MESSAGES['NO_BUTTON_NAME'])
                return

            if not self.config_manager.config_exists(button_name):
                logger.error(ERROR_MESSAGES['CONFIG_NOT_EXIST'].format(button_name))
                return

            scroll_position = self.ui_manager.get_scroll_position()
            self._navigate_to_config_screen(button_name, scroll_position)

        except Exception as exc:
            logger.error(ERROR_MESSAGES['HANDLE_CLICK_FAILED'].format(exc))

    def _extract_button_name(self, button_path):
        """从按钮路径中解析名称。"""
        if not button_path:
            return ""

        try:
            return button_path.split("/")[-1]
        except (IndexError, AttributeError):
            logger.error(ERROR_MESSAGES['INVALID_BUTTON_PATH'].format(button_path))
            return ""

    def _navigate_to_config_screen(self, button_name, scroll_position):
        """跳转到目标配置界面并同步滚动位置。"""
        try:
            config = self.config_manager.get_config(button_name)
            if not self.config_manager.validate_navigation_config(button_name, config):
                return

            clientApi.PopTopUI()

            logger.info(u"跳转到配置界面 {} -> {}.{}".format(
                button_name, config['mod_name_space'], config['ui_namespace']))

            new_screen = clientApi.PushScreen(
                config['mod_name_space'],
                config['ui_namespace']
            )

            if new_screen:
                new_screen.SetGlowingButton(button_name)
                game.AddTimer(TOUCH_DELAY, new_screen.SetScrollingPercent, scroll_position)
            else:
                logger.error(ERROR_MESSAGES['NO_NEW_SCREEN'])

        except Exception as exc:
            logger.error(ERROR_MESSAGES['NAVIGATE_FAILED'].format(exc))

    def set_glowing_button(self, button_name):
        """记录当前高亮的按钮名称。"""
        self.glowing_button = button_name or ""

    def navigate_to_default_config(self, button_name):
        """导航到默认配置界面（用于首次加载）。"""
        if not button_name:
            return

        try:
            self._navigate_to_config_screen(button_name, 0)
        except Exception as exc:
            logger.error("导航到默认配置失败: %s" % str(exc))

    def update_current_config(self, button_name):
        """根据按钮名称更新标题文字。"""
        if button_name and self.config_manager.config_exists(button_name):
            self.current_config = self.config_manager.get_config(button_name)
            title_text = u"模组设置·" + self.current_config.get('config_text', '')
            self.ui_manager.update_title(title_text)
        else:
            self.current_config = {}
            self.ui_manager.update_title()

    def get_glowing_button(self):
        """返回当前高亮的按钮名称。"""
        return self.glowing_button
