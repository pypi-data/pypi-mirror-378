# -*- coding: utf-8 -*-
"""GrapeSettings 配置条目。"""

from ..modConfig import MOD_NAMESPACE

[MOD_NAME]_config = {
    'mod_name_space': MOD_NAMESPACE,
    'config_name': '[MOD_NAME]_config',
    'ui_namespace': MOD_NAMESPACE + "_config",
    'priority': 12000,
    'config_text': "[MOD_NAME]",
    'config_icon': "textures/ui/replace_me",
    'python_path': "[MOD_NAME]Scripts.modCommon.GrapeSettings.[MOD_NAME]_config.ConfigScreen",
}
