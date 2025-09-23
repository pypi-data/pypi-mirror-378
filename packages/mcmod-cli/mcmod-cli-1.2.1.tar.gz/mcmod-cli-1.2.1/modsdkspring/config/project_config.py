# -*- coding: utf-8 -*-

class ProjectConfig:
    """项目配置类 - 替代硬编码的字符串常量"""
    
    def __init__(self, mod_name):
        if not mod_name or not mod_name.strip():
            raise ValueError("Mod name cannot be empty")
        
        self.mod_name = mod_name.strip()
        self.mod_dir_name = self.mod_name
        self.client_system_name = "{}ClientSystem".format(self.mod_name)
        self.server_system_name = "{}ServerSystem".format(self.mod_name)
        self.scripts_folder = "{}Scripts".format(self.mod_name)
        
    def get_template_vars(self):
        """获取模板变量字典"""
        return {
            'MOD_NAME': self.mod_name,
            'MOD_DIR_NAME': self.mod_dir_name,
            'CLIENT_SYSTEM_NAME': self.client_system_name,
            'SERVER_SYSTEM_NAME': self.server_system_name,
            'SCRIPTS_FOLDER': self.scripts_folder,
        }


class ManifestConfig:
    """Manifest配置类"""
    
    def __init__(self, header_uuid, module_uuid, name, version=(0, 0, 1)):
        self.header_uuid = header_uuid
        self.module_uuid = module_uuid
        self.name = name
        self.version = version
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            "format_version": 2,
            "header": {
                "description": "{} pack".format(self.name),
                "name": self.name,
                "uuid": self.header_uuid,
                "version": list(self.version),
                "min_engine_version": [1, 16, 0]
            },
            "modules": [
                {
                    "description": "{} module".format(self.name),
                    "type": "data",
                    "uuid": self.module_uuid,
                    "version": list(self.version)
                }
            ]
        }