# -*- coding: utf-8 -*-
import os
from modsdkspring.generators.project_generator import ProjectGenerator


class InitCommand:
    """init命令实现 - 替代原来的initMOD函数"""
    
    def __init__(self, package_path):
        self.package_path = package_path
        self.generator = ProjectGenerator(package_path)
    
    def execute(self, args):
        """执行init命令"""
        if args and args[0] in ['--help', '-h']:
            self._show_help()
            return
        
        print("Start initializing your Mod...")
        
        # 获取MOD名称
        mod_name = self._get_mod_name()
        if not mod_name:
            print("Error: MOD name cannot be empty")
            return
        
        # 检查目录是否已存在
        target_path = os.path.join(os.getcwd(), mod_name)
        if os.path.exists(target_path):
            try:
                # Python 2.7
                response = raw_input("Directory '{}' already exists. Overwrite? (y/N): ".format(mod_name))
            except NameError:
                # Python 3
                response = input("Directory '{}' already exists. Overwrite? (y/N): ".format(mod_name))
            
            if response.lower() != 'y':
                print("Operation cancelled.")
                return
        
        try:
            # 创建项目
            project_info = self.generator.create_project(mod_name)
            
            # 打印结果
            project_info.print_summary()
            print("\nCreated successfully!")
            
        except Exception as e:
            print("Error creating project: {}".format(e))
            raise
    
    def _get_mod_name(self):
        """获取MOD名称"""
        try:
            # Python 2.7
            mod_name = raw_input("Please enter the Mod name (will be used as namespace and folder name):\n").strip()
        except NameError:
            # Python 3
            mod_name = input("Please enter the Mod name (will be used as namespace and folder name):\n").strip()
        
        return mod_name
    
    def _show_help(self):
        """显示帮助信息"""
        print("Usage: mcmod init")
        print()
        print("Initialize a new Minecraft MOD project with the following structure:")
        print("  - Behavior pack with manifest")
        print("  - Resource pack with manifest") 
        print("  - MODSDKSpring framework files")
        print("  - Basic project configuration")
        print()
        print("The command will prompt you for the MOD name and generate all")
        print("necessary files and directories.")