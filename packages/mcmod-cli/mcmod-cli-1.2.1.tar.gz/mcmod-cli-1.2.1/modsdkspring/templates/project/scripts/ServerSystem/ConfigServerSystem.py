# -*- coding: utf-8 -*-

import mod.server.extraServerApi as serverApi
from [SCRIPTS_FOLDER].plugins.MODSDKSpring.core.ListenEvent import ListenEvent
from ..plugins.CrossEndCommunication import ServerCommunicator
from ..modCommon import modConfig

# 初始化 Minecraft API 组件
ServerSystem = serverApi.GetServerSystemCls()
compFactory = serverApi.GetEngineCompFactory()
levelId = serverApi.GetLevelId()
game = compFactory.CreateGame(levelId)
compExtraData = compFactory.CreateExtraData(levelId)


@ListenEvent.InitServer
class ConfigServerSystem(ServerSystem):
    """
    配置管理系统。
    负责模组配置的初始化、获取和更新。
    """

    # 默认配置模板
    DEFAULT_CONFIG = {
        "mod_enable": True
    }

    # 配置键名模板
    CONFIG_NAME = "[MOD_NAME]"
    CONFIG_KEY_TEMPLATE = "{}_config"
    INIT_KEY_TEMPLATE = "{}_config_inited"

    def __init__(self, namespace, systemName):
        """
        初始化配置系统。

        参数:
            namespace (str): 系统命名空间
            systemName (str): 系统名称
        """
        super(ConfigServerSystem, self).__init__(namespace, systemName)

        self.communicator = ServerCommunicator(
            namespace=namespace,
            system_name=systemName,
            target_system_name=modConfig.CONFIG_SYSTEM_NAME,
            server_system_instance=self
        )

        # 使用插件注册事件处理器
        self.communicator.register_handler("get_config", self.on_get_config, self)
        self.communicator.register_handler("set_config", self.on_set_config, self)

        self._initialize_mod_config()

    def _initialize_mod_config(self):
        """
        初始化模组配置（如果尚未初始化）。
        使用一个标记来避免重复初始化。
        """
        init_key = self.INIT_KEY_TEMPLATE.format(modConfig.MOD_NAMESPACE)
        is_initialized = compExtraData.GetExtraData(init_key)

        if is_initialized is None:
            self._create_default_config()

    def _create_default_config(self):
        """
        创建并保存默认配置。
        并标记配置已初始化。
        """
        config_key = self.CONFIG_KEY_TEMPLATE.format(self.CONFIG_NAME)
        init_key = self.INIT_KEY_TEMPLATE.format(modConfig.MOD_NAMESPACE)

        compExtraData.SetExtraData(config_key, self.DEFAULT_CONFIG.copy(), True)
        compExtraData.SetExtraData(init_key, True, True)

    def _get_config_by_name(self, config_name):
        """
        根据名称获取配置，如果不存在则创建默认配置。

        参数:
            config_name (str): 要获取的配置名

        返回:
            dict: 配置字典
        """
        config_key = self.CONFIG_KEY_TEMPLATE.format(config_name)
        config = compExtraData.GetExtraData(config_key)

        if config is None and config_name == self.CONFIG_NAME:
            config = self.DEFAULT_CONFIG.copy()
            compExtraData.SetExtraData(config_key, config, True)

        return config

    def on_get_config(self, args):
        """
        处理客户端获取配置的请求。

        参数:
            args (dict): 事件参数，包含 playerId 和 config_name
        """
        player_id = args.get('playerId')
        config_name = args.get('config_name')
        print('on_get_config')
        if not player_id or not config_name:
            return

        config = self._get_config_by_name(config_name)
        if config is not None:
            self.communicator.send_to_client(player_id, "return_config", config)

    def on_set_config(self, args):
        """
        处理客户端更新配置的请求。

        参数:
            args (dict): 事件参数，包含 playerId、config_name 和 config
        """
        print('on_set_config')
        config_name = args.get('config_name')
        config_data = args.get('config')

        if not config_name or config_data is None:
            return

        config_key = self.CONFIG_KEY_TEMPLATE.format(config_name)
        compExtraData.SetExtraData(config_key, config_data, True)
