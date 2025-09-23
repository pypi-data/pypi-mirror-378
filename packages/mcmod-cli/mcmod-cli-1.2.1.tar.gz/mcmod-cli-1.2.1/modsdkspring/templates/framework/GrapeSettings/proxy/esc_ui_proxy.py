# -*- coding: utf-8 -*-
"""暂停菜单代理，负责加入 GrapeSettings 按钮。"""

import mod.client.extraClientApi as clientApi

from ....modCommon import modConfig
from ..constants import ESC_BUTTON_PANEL_PATH, LOG_MESSAGES

ViewBinder = clientApi.GetViewBinderCls()
CustomUIScreenProxy = clientApi.GetUIScreenProxyCls()
ScreenNode = clientApi.GetScreenNodeCls()


class escUIProxy(CustomUIScreenProxy):
    """在 ESC 菜单中注入一个打开模组设置界面的按钮。"""

    def __init__(self, screenName, screenNode):
        CustomUIScreenProxy.__init__(self, screenName, screenNode)
        print(LOG_MESSAGES['PROXY_INIT'])

    def OnCreate(self):
        """创建代理时插入按钮并重建退出按钮。"""
        print(LOG_MESSAGES['PROXY_CREATE'])

        screen = self.GetScreenNode()
        control = screen.GetBaseUIControl(ESC_BUTTON_PANEL_PATH)

        self._create_config_button(screen, control)
        self._recreate_quit_button(screen, control, ESC_BUTTON_PANEL_PATH)

    def _create_config_button(self, screen, parent_control):
        """创建或复用 ESC 菜单中的模组设置按钮。"""
        if not parent_control.GetChildByName("grape_esc"):
            self.grape_esc = screen.CreateChildControl(
                "grape_settings.esc_button", "grape_esc", parent_control
            ).asButton()
        else:
            self.grape_esc = parent_control.GetChildByName("grape_esc").asButton()

        self.grape_esc.AddTouchEventParams({"isSwallow": True})
        self.grape_esc.SetButtonTouchDownCallback(self.Ongrape_escButtonTouch)

    def _recreate_quit_button(self, screen, parent_control, button_panel_path):
        """重新排布退出按钮，确保布局顺序正确。"""
        if parent_control.GetChildByName("quit_button"):
            screen.RemoveComponent(button_panel_path + '/quit_button', button_panel_path)

            if not parent_control.GetChildByName("grape_padding"):
                screen.CreateChildControl("pause.vertical_padding", "grape_padding", parent_control)

            screen.CreateChildControl("pause.quit_button", "quit_button", parent_control).asButton()

    def Ongrape_escButtonTouch(self, args):
        """点击时弹出 GrapeSettings 主界面。"""
        print(LOG_MESSAGES['CONFIG_BUTTON_TOUCH'])
        MOD_NAMESPACE = modConfig.MOD_NAMESPACE
        clientApi.PushScreen(MOD_NAMESPACE, "GrapeSettings")

    def OnDestroy(self):
        print(LOG_MESSAGES['PROXY_DESTROY'])

    def OnTick(self):
        pass
