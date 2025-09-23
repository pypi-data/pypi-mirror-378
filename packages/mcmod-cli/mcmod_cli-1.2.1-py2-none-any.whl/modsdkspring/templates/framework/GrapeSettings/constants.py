# -*- coding: utf-8 -*-
"""GrapeSettings 插件使用到的常量定义。"""

# UI 布局默认值
CONFIG_BUTTON_HEIGHT = 30
TOUCH_DELAY = 0.1
DEFAULT_TITLE = u"模组设置·概览"
SELECTED_BUTTON_SPRITE = "textures/netease/common/button/choose"

# 暂停菜单中 ESC 按钮面板的控件路径
ESC_BUTTON_PANEL_PATH = (
    "variables_button_mappings_and_controls/safezone_screen_matrix/"
    "inner_matrix/safezone_screen_panel/root_screen_panel/"
    "pause_screen_main_panels/menu/the_rest_panel/pause_menu/"
    "menu_button_control/menu_background/button_panel"
)

# 配置注册表相关
CONFIG_REGISTRY_KEY = "grape_settings_reg"
REQUIRED_CONFIG_FIELDS = ['config_name', 'config_text', 'config_icon']
REQUIRED_NAVIGATION_FIELDS = ['mod_name_space', 'ui_namespace']

# 日志消息（保留中文方便游戏内显示）
LOG_MESSAGES = {
    'INIT_COMPLETE': u"模组设置界面初始化完成",
    'CREATE_START': u"开始构建模组设置界面",
    'CREATE_COMPLETE': u"模组设置界面构建完成",
    'CLOSE_BUTTON': u"用户点击关闭按钮，退出模组设置界面",
    'NO_CONFIGS': u"未发现任何已注册的模组设置",
    'INVALID_CLICK': u"无效点击：触控位置不匹配",
    'PROXY_INIT': "escUIProxy __init__",
    'PROXY_CREATE': "escUIProxy Create",
    'PROXY_DESTROY': "escUIProxy Destroy",
    'CONFIG_BUTTON_TOUCH': "Ongrape_escButtonTouch",
}

ERROR_MESSAGES = {
    'NO_MAIN_PANEL': u"无法获取界面主面板",
    'BUTTON_CREATE_FAILED': u"无法创建配置按钮: {}",
    'CONFIG_SORT_FAILED': u"配置排序失败: {}",
    'MISSING_FIELD': u"配置 {} 缺少必填字段: {}",
    'CONFIG_NOT_EXIST': u"配置不存在: {}",
    'NO_BUTTON_NAME': u"无法解析按钮名称",
    'INVALID_BUTTON_PATH': u"无效的按钮路径: {}",
    'GET_SCROLL_FAILED': u"获取滚动位置失败: {}",
    'NAVIGATE_FAILED': u"跳转到配置界面失败: {}",
    'SETUP_CONTENT_FAILED': u"设置按钮内容失败: {}",
    'SET_SELECTED_FAILED': u"设置按钮选中状态失败: {}",
    'HANDLE_CLICK_FAILED': u"处理配置按钮点击失败: {}",
    'CREATE_BUTTON_FAILED': u"创建配置按钮失败 {}: {}",
    'NO_NEW_SCREEN': u"无法打开新的配置界面",
}

WARNING_MESSAGES = {
    'INVALID_SCROLL': u"滚动百分比无效: {}",
    'NO_LABEL': u"按钮文本标签不存在",
    'NO_ICON': u"按钮图标控件不存在",
    'NO_DEFAULT_BG': u"按钮默认背景控件不存在",
}
