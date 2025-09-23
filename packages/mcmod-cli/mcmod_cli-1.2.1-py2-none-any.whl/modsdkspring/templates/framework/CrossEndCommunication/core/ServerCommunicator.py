# -*- coding: utf-8 -*-

import mod.server.extraServerApi as serverApi

class ServerCommunicator(object):
    """
    服务端通信器

    封装服务端与客户端通信的标准接口，简化事件监听和消息发送。
    提供统一的数据存储和玩家通信管理。
    """

    def __init__(self, namespace, system_name, target_system_name, server_system_instance=None):
        """
        初始化服务端通信器

        参数:
            namespace (str): 命名空间，用于标识模组
            system_name (str): 当前系统名称
            target_system_name (str): 目标客户端系统名称
            server_system_instance (ServerSystem): 服务端系统实例，用于发送消息
        """
        self._namespace = namespace
        self._system_name = system_name
        self._target_system_name = target_system_name
        self._server_system_instance = server_system_instance
        self._event_handlers = {}  # 事件名 -> 处理函数映射
        self._registered_events = set()  # 已注册的事件集合

        # 初始化Minecraft API组件
        self._comp_factory = serverApi.GetEngineCompFactory()
        self._level_id = serverApi.GetLevelId()
        self._game = self._comp_factory.CreateGame(self._level_id)
        self._comp_extra_data = self._comp_factory.CreateExtraData(self._level_id)

    def register_handler(self, event_name, handler, instance=None):
        """
        注册事件处理器

        参数:
            event_name (str): 事件名称
            handler (callable): 处理函数，接收一个参数(event_data)
            instance (object, optional): 处理函数绑定的实例对象
        """
        if self._server_system_instance is None:
            raise RuntimeError("ServerCommunicator needs server_system_instance to register event handlers.")

        if event_name in self._event_handlers:
            # 记录重复注册（开发调试用）
            print("Warning: Event '{}' handler already registered, replacing".format(event_name))

        # 记录处理器信息
        self._event_handlers[event_name] = {
            'handler': handler,
            'instance': instance
        }

        # 只在第一次注册时监听事件，后续复用同一个监听器
        if event_name not in self._registered_events:
            self._server_system_instance.ListenForEvent(
                self._namespace,
                self._target_system_name,
                event_name,
                self,
                self._dispatch_single_event
            )
            self._registered_events.add(event_name)

    def _dispatch_single_event(self, args):
        """
        通用事件分发器 - Minecraft会根据ListenForEvent的具体事件调用这个函数

        参数:
            args (dict): 事件参数
        """
        # 由于Minecraft的ListenForEvent机制，我们需要通过某种方式识别事件类型
        # 但实际上，每个ListenForEvent调用都会为特定事件名创建监听
        # 所以我们需要一个更直接的分发机制

        # 遍历所有注册的处理器，找到匹配的
        for event_name, handler_info in self._event_handlers.items():
            handler = handler_info['handler']
            instance = handler_info['instance']

            try:
                handler(args)
            except Exception as e:
                print("Error in event handler for '{}': {}".format(event_name, str(e)))
                break  # 只处理第一个匹配的处理器

    def unregister_handler(self, event_name):
        """
        取消注册事件处理器

        参数:
            event_name (str): 事件名称
        """
        if event_name in self._event_handlers:
            # 取消Minecraft事件监听
            if self._server_system_instance:
                self._server_system_instance.UnListenForEvent(
                    self._namespace,
                    self._target_system_name,
                    event_name,
                    self,
                    self._dispatch_event
                )
            del self._event_handlers[event_name]

    def send_to_client(self, player_id, event_name, data=None):
        """
        向指定客户端发送消息

        参数:
            player_id (str): 目标玩家ID
            event_name (str): 事件名称
            data (dict, optional): 要发送的数据
        """
        if data is None:
            data = {}

        if self._server_system_instance is None:
            raise RuntimeError("ServerCommunicator needs server_system_instance to send messages. Pass it in constructor.")

        # 直接调用系统实例的NotifyToClient发送消息
        self._server_system_instance.NotifyToClient(player_id, event_name, data)

    def send_to_all_clients(self, event_name, data=None):
        """
        向所有客户端广播消息

        参数:
            event_name (str): 事件名称
            data (dict, optional): 要发送的数据
        """
        if data is None:
            data = {}

        # 获取所有在线玩家
        player_ids = self._game.GetPlayerIds()

        for player_id in player_ids:
            self.send_to_client(player_id, event_name, data)

    def store_data(self, key, value, persistent=True):
        """
        存储数据到服务端

        参数:
            key (str): 数据键名
            value: 要存储的数据
            persistent (bool): 是否持久化存储
        """
        self._comp_extra_data.SetExtraData(key, value, persistent)

    def get_data(self, key, default_value=None):
        """
        从服务端获取数据

        参数:
            key (str): 数据键名
            default_value: 默认值

        返回:
            存储的数据或默认值
        """
        data = self._comp_extra_data.GetExtraData(key)
        return data if data is not None else default_value

    def get_online_players(self):
        """
        获取所有在线玩家ID列表

        返回:
            list: 玩家ID列表
        """
        return self._game.GetPlayerIds()

    def is_player_online(self, player_id):
        """
        检查玩家是否在线

        参数:
            player_id (str): 玩家ID

        返回:
            bool: 是否在线
        """
        return player_id in self.get_online_players()

    def cleanup(self):
        """
        清理所有注册的事件处理器
        """
        self._event_handlers.clear()

    def get_handler(self, event_name):
        """
        获取指定事件的处理器信息

        参数:
            event_name (str): 事件名称

        返回:
            dict: 处理器信息，包含handler和instance
        """
        return self._event_handlers.get(event_name)

    def is_handler_registered(self, event_name):
        """
        检查事件处理器是否已注册

        参数:
            event_name (str): 事件名称

        返回:
            bool: 是否已注册
        """
        return event_name in self._event_handlers