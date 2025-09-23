# -*- coding: utf-8 -*-

import mod.client.extraClientApi as clientApi

class ClientCommunicator(object):
    """
    客户端通信器

    封装客户端与服务端通信的标准接口，简化事件监听和消息发送。
    基于观察者模式，提供类型安全的通信机制。
    """

    def __init__(self, namespace, system_name, target_system_name):
        """
        初始化客户端通信器

        参数:
            namespace (str): 命名空间，用于标识模组
            system_name (str): 当前系统名称
            target_system_name (str): 目标服务端系统名称
        """
        self._namespace = namespace
        self._system_name = system_name
        self._target_system_name = target_system_name
        self._system = clientApi.GetSystem(namespace, system_name)
        self._event_handlers = {}  # 事件名 -> 处理函数映射

    def register_handler(self, event_name, handler, instance=None):
        """
        注册事件处理器

        参数:
            event_name (str): 事件名称
            handler (callable): 处理函数，接收一个参数(event_data)
            instance (object, optional): 处理函数绑定的实例对象
        """
        if event_name in self._event_handlers:
            # 取消之前的监听
            old_handler_info = self._event_handlers[event_name]
            self._system.UnListenForEvent(
                self._namespace,
                self._target_system_name,
                event_name,
                old_handler_info['instance'],
                old_handler_info['handler']
            )

        # 注册新的监听
        self._system.ListenForEvent(
            self._namespace,
            self._target_system_name,
            event_name,
            instance,
            handler
        )

        # 记录处理器信息
        self._event_handlers[event_name] = {
            'handler': handler,
            'instance': instance
        }

    def unregister_handler(self, event_name):
        """
        取消注册事件处理器

        参数:
            event_name (str): 事件名称
        """
        if event_name in self._event_handlers:
            handler_info = self._event_handlers[event_name]
            self._system.UnListenForEvent(
                self._namespace,
                self._target_system_name,
                event_name,
                handler_info['instance'],
                handler_info['handler']
            )
            del self._event_handlers[event_name]

    def send_to_server(self, event_name, data=None):
        """
        向服务端发送消息

        参数:
            event_name (str): 事件名称
            data (dict, optional): 要发送的数据
        """
        if data is None:
            data = {}

        self._system.NotifyToServer(event_name, data)

    def cleanup(self):
        """
        清理所有注册的事件处理器
        """
        for event_name in list(self._event_handlers.keys()):
            self.unregister_handler(event_name)

    def get_local_player_id(self):
        """
        获取本地玩家ID

        返回:
            str: 本地玩家ID
        """
        return clientApi.GetLocalPlayerId()

    def is_handler_registered(self, event_name):
        """
        检查事件处理器是否已注册

        参数:
            event_name (str): 事件名称

        返回:
            bool: 是否已注册
        """
        return event_name in self._event_handlers