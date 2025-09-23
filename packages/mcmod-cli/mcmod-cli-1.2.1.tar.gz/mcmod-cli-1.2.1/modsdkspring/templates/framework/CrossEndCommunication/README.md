# CrossEndCommunication - 双端通信插件

## 概述

CrossEndCommunication 是一个为 Minecraft 基岩版模组开发的标准化双端通信插件。它封装了客户端和服务端之间的事件通信机制，提供简洁易用的API，让开发者专注于业务逻辑而非底层通信细节。

## 特性

- **统一接口**: 为客户端和服务端提供一致的通信API
- **事件管理**: 自动处理事件注册和注销，避免内存泄漏
- **数据存储**: 服务端提供持久化数据存储功能
- **类型安全**: 清晰的参数定义和错误处理

## 项目结构

```
CrossEndCommunication/
├── __init__.py                 # 插件入口
├── core/                       # 核心模块
│   ├── __init__.py
│   ├── ClientCommunicator.py   # 客户端通信器
│   └── ServerCommunicator.py   # 服务端通信器
└── README.md                   # 说明文档
```

## 快速开始

### 1. 导入插件

```python
from your_add_on.plugins.CrossEndCommunication import ClientCommunicator, ServerCommunicator
```

### 2. 客户端使用

```python
# -*- coding: utf-8 -*-
import mod.client.extraClientApi as clientApi
from your_add_on.plugins.CrossEndCommunication import ClientCommunicator

class MyClientSystem(object):
    def __init__(self, namespace, name, param):
        # 创建通信器
        self.communicator = ClientCommunicator(
            namespace=namespace,
            system_name=name,
            target_system_name="MyServerSystem"
        )

    def Create(self):
        # 注册事件处理器
        self.communicator.register_handler(
            "server_response",
            self.on_server_response,
            self
        )

        # 发送消息到服务端
        self.communicator.send_to_server("client_request", {
            "player_id": self.communicator.get_local_player_id(),
            "data": "hello server"
        })

    def on_server_response(self, args):
        print("收到服务端响应: {}".format(args))

    def Destroy(self):
        # 清理资源
        self.communicator.cleanup()
```

### 3. 服务端使用

```python
# -*- coding: utf-8 -*-
import mod.server.extraServerApi as serverApi
from your_add_on.plugins.CrossEndCommunication import ServerCommunicator

ServerSystem = serverApi.GetServerSystemCls()

class MyServerSystem(ServerSystem):
    def __init__(self, namespace, systemName):
        super(MyServerSystem, self).__init__(namespace, systemName)

        # 创建通信器
        self.communicator = ServerCommunicator(
            namespace=namespace,
            system_name=systemName,
            target_system_name="MyClientSystem",
            server_system_instance=self
        )

        # 注册事件处理器
        self.communicator.register_handler(
            "client_request",
            self.on_client_request,
            self
        )

    def on_client_request(self, args):
        player_id = args.get("player_id")
        data = args.get("data")

        print("收到客户端请求: {} - {}".format(player_id, data))

        # 响应客户端
        self.communicator.send_to_client(player_id, "server_response", {
            "message": "服务端已收到: {}".format(data),
            "timestamp": "2024-01-01 12:00:00"
        })
```

## API 文档

### ClientCommunicator

客户端通信器，负责与服务端的通信。

#### 构造函数
```python
ClientCommunicator(namespace, system_name, target_system_name)
```

**参数:**
- `namespace` (str): 命名空间，用于标识模组
- `system_name` (str): 当前客户端系统名称
- `target_system_name` (str): 目标服务端系统名称

#### 主要方法

##### register_handler(event_name, handler, instance=None)
注册事件处理器

**参数:**
- `event_name` (str): 事件名称
- `handler` (callable): 处理函数，接收一个参数(event_data)
- `instance` (object, optional): 处理函数绑定的实例对象

##### send_to_server(event_name, data=None)
向服务端发送消息

**参数:**
- `event_name` (str): 事件名称
- `data` (dict, optional): 要发送的数据

##### unregister_handler(event_name)
取消注册事件处理器

##### cleanup()
清理所有注册的事件处理器

##### get_local_player_id()
获取本地玩家ID

**返回:** str - 本地玩家ID

### ServerCommunicator

服务端通信器，负责与客户端的通信和数据管理。

#### 构造函数
```python
ServerCommunicator(namespace, system_name, target_system_name, server_system_instance=None)
```

**参数:**
- `namespace` (str): 命名空间，用于标识模组
- `system_name` (str): 当前服务端系统名称
- `target_system_name` (str): 目标客户端系统名称
- `server_system_instance` (ServerSystem): 服务端系统实例，用于发送消息到客户端

#### 主要方法

##### register_handler(event_name, handler, instance=None)
注册事件处理器

##### send_to_client(player_id, event_name, data=None)
向指定客户端发送消息

##### send_to_all_clients(event_name, data=None)
向所有客户端广播消息

##### store_data(key, value, persistent=True)
存储数据到服务端

**参数:**
- `key` (str): 数据键名
- `value`: 要存储的数据
- `persistent` (bool): 是否持久化存储

##### get_data(key, default_value=None)
从服务端获取数据

##### get_online_players()
获取所有在线玩家ID列表

##### cleanup()
清理所有注册的事件处理器

## 版本历史

### v1.0.0
- 初始版本
- 实现基础的双端通信功能
- 提供客户端和服务端通信器
- 包含完整的使用示例和文档