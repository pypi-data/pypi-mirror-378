# -*- coding: utf-8 -*-
"""
CrossEndCommunication - 双端通信插件

提供客户端和服务端之间的标准化通信接口，简化事件注册和消息传递。
"""

from .core.ClientCommunicator import ClientCommunicator
from .core.ServerCommunicator import ServerCommunicator

__version__ = "1.0.0"
__all__ = ['ClientCommunicator', 'ServerCommunicator']