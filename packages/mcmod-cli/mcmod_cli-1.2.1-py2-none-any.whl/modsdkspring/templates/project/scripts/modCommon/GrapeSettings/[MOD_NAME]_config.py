# -*- coding: utf-8 -*-
"""模组的配置界面实现模板。"""

import mod.client.extraClientApi as clientApi

from ...plugins.GrapeSettings.screen.grape_settings_screen import GrapeSettingsScreen
from ...plugins.CrossEndCommunication import ClientCommunicator
from .. import modConfig
from . import grape_settings_config

ViewBinder = clientApi.GetViewBinderCls()


class ConfigScreen(GrapeSettingsScreen):
    """继承 GrapeSettings 主界面，补充模组的详细配置。"""

    def __init__(self, namespace, name, param):
        super(ConfigScreen, self).__init__(namespace, name, param)

        # 默认配置，可以按需扩展
        self.mod_config = {
            "mod_enable": True
        }

        # 初始化通信器
        self.communicator = ClientCommunicator(
            namespace=modConfig.MOD_NAMESPACE,
            system_name=modConfig.CONFIG_SYSTEM_NAME,
            target_system_name=modConfig.CONFIG_SERVER_SYSTEM_NAME,
        )

    def Create(self):
        """初始化界面并向服务器请求当前配置。"""
        super(ConfigScreen, self).Create()

        self._capture_detail_controls()
        self.communicator.register_handler("return_config", self.on_return_config, self)
        self._request_config_from_server()

    def Destroy(self):
        """销毁界面时释放通信资源。"""
        self.communicator.cleanup()
        super(ConfigScreen, self).Destroy()

    # ------------------------------------------------------------------
    # 服务器通信回调
    # ------------------------------------------------------------------
    def on_return_config(self, config):
        """接收服务器返回的配置并刷新控件状态。"""
        self.mod_config = config
        self.set_controller_state()

    def set_controller_state(self):
        """同步 UI 控件与当前配置。"""
        if self.toggle_mod_enable.GetToggleState() != self.mod_config['mod_enable']:
            self.toggle_mod_enable.SetToggleState(self.mod_config['mod_enable'])

    @ViewBinder.binding(ViewBinder.BF_ToggleChanged, "toggle_mod_enable")
    def on_toggle_mod_enable_changed(self, args):
        """在开关变化时向服务器提交配置。"""
        if self.mod_config['mod_enable'] != args['state']:
            self.mod_config['mod_enable'] = args['state']
            self.communicator.send_to_server("set_config", {
                'playerId': self.communicator.get_local_player_id(),
                'config_name': modConfig.MOD_NAMESPACE,
                'config': self.mod_config,
            })

    # ------------------------------------------------------------------
    # 私有工具方法
    # ------------------------------------------------------------------
    def _capture_detail_controls(self):
        """缓存详情面板中的常用控件引用。"""
        self.config_detail_panel = self.GetBaseUIControl("config_detail_panel")
        self.detail_scroll_view = self.config_detail_panel.GetChildByName('config_scroll_view').asScrollView()
        self.detail_scrolling_content = self.detail_scroll_view.GetScrollViewContentControl()

        # 示例：获取开关控件
        toggle_panel = self.detail_scrolling_content.GetChildByName('toggle_mod_enable_panel')
        self.toggle_mod_enable = toggle_panel.GetChildByName('toggle_mod_enable').asSwitchToggle()

    def _request_config_from_server(self):
        """向服务器请求当前玩家的配置数据。"""
        self.communicator.send_to_server("get_config", {
            'playerId': self.communicator.get_local_player_id(),
            'config_name': modConfig.MOD_NAMESPACE,
        })