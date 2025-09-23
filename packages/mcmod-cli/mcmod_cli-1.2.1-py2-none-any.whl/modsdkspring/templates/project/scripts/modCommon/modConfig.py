# -*- coding: utf-8 -*-

# ==================================================
# 手动配置区域 - 用户可以修改的配置
# ==================================================
MOD_NAMESPACE = "[MOD_NAME]"
MOD_VERSION = "0.0.1"

 # mod settings in Grape Setting
REG_CONFIG = True 

# ==================================================
# 自动生成配置区域 - 请勿手动修改
# ==================================================
def _make_system_name(suffix):
    return "{}{}".format(MOD_NAMESPACE, suffix)

def _make_class_path(module_path, class_name):
    return "{}Scripts.{}.{}".format(MOD_NAMESPACE, module_path, class_name)

# 基础路径
SCRIPT_PATH = "{}Scripts".format(MOD_NAMESPACE)

# Mod Client System
CLIENT_SYSTEM_NAME = _make_system_name("ClientSystem")
CLIENT_SYSTEM_CLS_PATH = _make_class_path("ClientSystem.MainClientSystem", _make_system_name("ClientSystem"))

# Mod Server System
SERVER_SYSTEM_NAME = _make_system_name("ServerSystem")
SERVER_SYSTEM_CLS_PATH = _make_class_path("ServerSystem.MainServerSystem", _make_system_name("ServerSystem"))

CONFIG_SERVER_SYSTEM_NAME = "ConfigServerSystem"
CONFIG_SERVER_SYSTEM_CLS_PATH = _make_class_path("ServerSystem.ConfigServerSystem", "ConfigServerSystem")

# ======== Grape Settings ========
CONFIG_SYSTEM_NAME = "GrapeSettingsConfigSystem"
CONFIG_SYSTEM_CLS_PATH = _make_class_path("plugins.GrapeSettings.config_system", "ConfigSystem")
