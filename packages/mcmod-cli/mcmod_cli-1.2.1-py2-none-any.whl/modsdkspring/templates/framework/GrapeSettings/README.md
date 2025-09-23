# GrapeSettings 插件使用说明

## 功能概述
- 在暂停菜单 ESC 界面注入“模组设置”按钮，并按优先级决定是否占据顶部入口。
- 提供可复用的列表界面，展示已注册的模组配置条目并跳转至具体配置界面。
- 通过共享注册表向其他模组开放配置注册能力，实现多模组共用一个聚合面板。
- 搭配 `CrossEndCommunication` 封装，实现客户端配置界面与服务器存档间的数据同步。

## 目录结构
- `config_system.py`：在客户端注册配置条目与 UI，负责代理 ESC 界面。
- `core/`：缓存引擎组件、读写配置注册表的底层工具。
- `handlers/event_handler.py`：处理配置按钮的触控事件与界面跳转。
- `managers/config_manager.py`：加载并校验注册在共享表中的配置数据。
- `screen/grape_settings_screen.py`：模组设置总览界面的逻辑入口。
- `ui/ui_manager.py`：封装 UI 控件查找、按钮创建、滚动区域等基础操作。
- `proxy/esc_ui_proxy.py`：将“模组设置”按钮挂接到 ESC 菜单。

## 工作流程
1. `ConfigSystem` 在 `UiInitFinished` 事件后读取 `grape_settings_config.[MOD_NAME]_config` 并写入共享注册表。
2. 当当前模组配置的 `priority` 为最小值时，系统会注册 `esc_ui_proxy` 并在暂停菜单动态补全按钮与主界面 UI。
3. 玩家点击 ESC 中的“模组设置”按钮，会打开 `GrapeSettingsScreen`，读取注册表并生成配置列表。
4. 选择具体配置项时，会根据配置提供的 `mod_name_space` 和 `ui_namespace` 切换到对应的详细界面。
5. 详页可通过 `CrossEndCommunication` 与服务器交互，实现配置的读取与持久化。

## 集成步骤

### 1. 启用配置系统
- 在 `modCommon/modConfig.py` 中确认 `REG_CONFIG = True`，使 `modMain.py` 在客户端注册 `GrapeSettingsConfigSystem`。
- Manifest 中需确保已经注册 `modConfig.CONFIG_SYSTEM_CLS_PATH` 指向的脚本。

### 2. 声明配置条目
- 在 `modCommon/GrapeSettings/grape_settings_config.py` 中新增或修改配置字典，最少需要以下字段：
  - `config_name`：唯一键，用于注册表与网络通信。
  - `config_text`：在总览界面显示的文本。
  - `config_icon`：按钮图标的纹理路径。
  - `mod_name_space` / `ui_namespace`：用于 `clientApi.PushScreen` 的命名空间。
  - `priority`：决定排序；数值越小优先级越高。
  - `python_path`：可选，提供自定义 UI 时需要。
- 示例：

```python
new_mod_config = {
    'mod_name_space': 'your_mod',
    'config_name': 'your_mod',
    'ui_namespace': 'your_mod_config',
    'priority': 10000,
    'config_text': '你的模组',
    'config_icon': 'textures/your_icon',
    'python_path': 'yourModScripts.modCommon.GrapeSettings.your_mod_config.ConfigScreen',
}
```

### 3. 准备 UI 与资源
- `resource_pack/ui/grape_settings.json` 定义了聚合界面的布局，可根据需要复制并扩展。
- 如需自定义按钮图标或详情 UI，请保证纹理与 UI JSON 已在资源包中导出，并与配置中的路径对应。

### 4. 继承 `GrapeSettingsScreen` 实现详情界面
- 创建自定义类继承 `screen/grape_settings_screen.py` 中的 `GrapeSettingsScreen`，在 `Create` 中捕获控件、绑定事件。
- 使用 `@ViewBinder.binding` 装饰器可快速绑定切换、按钮等交互。参考 `modCommon/GrapeSettings/[MOD_NAME]_config.py`。
- 如需记忆最后一次打开的配置按钮，可调用 `EventHandler.set_glowing_button` 来同步初始高亮项。

### 5. 同步服务器配置（可选）
- 通过 `plugins/CrossEndCommunication` 提供的 `ClientCommunicator`、`ServerCommunicator` 与服务器系统互通。
- 服务器端可参考 `ServerSystem/ConfigServerSystem.py`，利用 `ExtraData` 持久化配置，并实现 `get_config` / `set_config` 处理逻辑。

## 优先级与代理策略
- `ConfigSystem.is_highest_priority` 会读取注册表并按 `priority` 从小到大排序。
- 当当前模组条目位于首位时，`esc_ui_proxy` 会被注册，确保 ESC 菜单中只有一个来源的“模组设置”入口。
- 如果希望共存多个模组，可调整 `priority`，避免覆盖其他插件的按钮。

## 相关资源
- UI：`resource_pack_2WQkaYY2/ui/grape_settings.json`
- 配置示例：`behavior_pack_rWQthfal/[MOD_NAME]Scripts/modCommon/GrapeSettings/[MOD_NAME]_config.py`
- 服务器实现：`behavior_pack_rWQthfal/[MOD_NAME]Scripts/ServerSystem/ConfigServerSystem.py`
