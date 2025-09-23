# -*- coding: utf-8 -*-
"""模组设置总览界面的 UI 控件封装。"""

from mod_log import logger

from ..constants import (
    CONFIG_BUTTON_HEIGHT,
    TOUCH_DELAY,
    DEFAULT_TITLE,
    SELECTED_BUTTON_SPRITE,
    ERROR_MESSAGES,
    WARNING_MESSAGES,
)
from ..core.client_context import get_game


game = get_game()


class UIManager(object):
    """负责创建按钮列表、调整布局并处理基础 UI 行为。"""

    def __init__(self, screen_node):
        self.screen = screen_node
        self.main_panel = None
        self.scroll_view = None
        self.scrolling_content = None

    def setup_main_controls(self):
        """获取常用控件引用，初始化主界面。"""
        self.main_panel = self.screen.GetBaseUIControl("main_panel")
        if not self.main_panel:
            logger.error(ERROR_MESSAGES['NO_MAIN_PANEL'])
            return False

        self.scroll_view = self.main_panel.GetChildByName('scroll_view').asScrollView()
        self.scrolling_content = self.scroll_view.GetScrollViewContentControl()
        return True

    def setup_close_button(self, callback):
        """绑定关闭按钮的回调函数。"""
        if not self.main_panel:
            return False

        top_panel = self.main_panel.GetChildByName("top_panel").GetChildByName("top_bg")
        close_btn = top_panel.GetChildByName("close_btn").asButton()
        close_btn.AddTouchEventParams({"isSwallow": True})
        close_btn.SetButtonTouchDownCallback(callback)
        return True

    def adjust_scroll_content_size(self, config_count):
        """根据配置数量调整滚动容器高度。"""
        if not self.scrolling_content:
            return

        size_x, _ = self.scrolling_content.GetSize()
        new_size_y = config_count * CONFIG_BUTTON_HEIGHT
        self.scrolling_content.SetSize((size_x, new_size_y))

    def create_config_button(self, btn_name, btn_text, btn_icon, touch_down_callback, touch_up_callback):
        """创建单个配置按钮并绑定事件。"""
        try:
            button_control = self.screen.CreateChildControl(
                "grape_settings.single_config_btn", btn_name, self.scrolling_content)
            if not button_control:
                logger.error(ERROR_MESSAGES['BUTTON_CREATE_FAILED'].format(btn_name))
                return None

            button = button_control.asButton()
            game.AddTimer(TOUCH_DELAY, self._enable_button_touch, button)

            button.SetButtonTouchDownCallback(touch_down_callback)
            button.SetButtonTouchUpCallback(touch_up_callback)

            self._setup_button_content(button, btn_text, btn_icon)
            return button

        except Exception as exc:
            logger.error(ERROR_MESSAGES['CREATE_BUTTON_FAILED'].format(btn_name, exc))
            return None

    def _enable_button_touch(self, button):
        """延迟开启触控参数以避免穿透。"""
        if button:
            button.AddTouchEventParams({"isSwallow": True})

    def _setup_button_content(self, button, btn_text, btn_icon):
        """设置按钮的文本与图标资源。"""
        try:
            label = button.GetChildByName("label")
            if label:
                label.asLabel().SetText(btn_text)
            else:
                logger.warning(WARNING_MESSAGES['NO_LABEL'])

            icon = button.GetChildByName("icon")
            if icon:
                icon.asImage().SetSprite(btn_icon)
            else:
                logger.warning(WARNING_MESSAGES['NO_ICON'])

        except Exception as exc:
            logger.error(ERROR_MESSAGES['SETUP_CONTENT_FAILED'].format(exc))

    def set_button_selected(self, button):
        """为按钮设置选中态的背景。"""
        try:
            default_bg = button.GetChildByName("default")
            if default_bg:
                default_bg.asImage().SetSprite(SELECTED_BUTTON_SPRITE)
            else:
                logger.warning(WARNING_MESSAGES['NO_DEFAULT_BG'])
        except Exception as exc:
            logger.error(ERROR_MESSAGES['SET_SELECTED_FAILED'].format(exc))

    def update_title(self, title_text=None):
        """更新界面顶部标题。"""
        if not self.main_panel:
            return

        title_label = self.main_panel.GetChildByName("top_panel").GetChildByName("top_bg").GetChildByName("label").asLabel()
        title_label.SetText(title_text or DEFAULT_TITLE)

    def get_scroll_position(self):
        """获取当前滚动百分比。"""
        try:
            if self.scroll_view:
                return self.scroll_view.GetScrollViewPercentValue()
        except Exception as exc:
            logger.error(ERROR_MESSAGES['GET_SCROLL_FAILED'].format(exc))
        return 0.0

    def set_scroll_position(self, value):
        """设置滚动百分比并校验取值范围。"""
        if 0.0 <= value <= 1.0 and self.scroll_view:
            self.scroll_view.SetScrollViewPercentValue(value)
        else:
            logger.warning(WARNING_MESSAGES['INVALID_SCROLL'].format(value))
