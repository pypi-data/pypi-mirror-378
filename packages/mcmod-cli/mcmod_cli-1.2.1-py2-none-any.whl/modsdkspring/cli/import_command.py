# -*- coding: utf-8 -*-
import os
from modsdkspring.utils.file_utils import generate_init_py


class ImportCommand:
    """import命令实现 - 替代原来的initPy函数"""
    
    def execute(self, args):
        """执行import命令"""
        if args and args[0] in ['--help', '-h']:
            self._show_help()
            return
        
        target_path = self._parse_args(args)
        if not target_path:
            return
        
        if not os.path.exists(target_path):
            print("Error: Directory '{}' does not exist".format(target_path))
            return
        
        if not os.path.isdir(target_path):
            print("Error: '{}' is not a directory".format(target_path))
            return
        
        print("Starting to create the __init__.py file.")
        
        try:
            # 生成__init__.py内容
            init_content = generate_init_py(target_path)
            
            # 写入文件
            init_path = os.path.join(target_path, '__init__.py')
            with open(init_path, 'w') as f:
                f.write(init_content)
            
            print("Successfully created the __init__.py file!")
            
            # 显示统计信息
            import_count = len(init_content.split('\n')) - 1 if init_content.strip() else 0
            print("Generated {} import statements".format(import_count))
            
        except Exception as e:
            print("Error creating __init__.py file: {}".format(e))
            raise
    
    def _parse_args(self, args):
        """解析命令行参数"""
        if not args:
            # 没有参数，使用当前目录
            return os.getcwd()
        
        if len(args) == 2 and args[0] == '--path':
            # --path 参数
            return os.path.abspath(args[1])
        
        # 参数格式错误
        print("Usage: mcmod import [--path <directory>]")
        return None
    
    def _show_help(self):
        """显示帮助信息"""
        print("Usage: mcmod import [--path <directory>]")
        print()
        print("Automatically generate __init__.py file with imports for all Python")
        print("classes found in the specified directory and its subdirectories.")
        print()
        print("Options:")
        print("  --path <directory>   Target directory (default: current directory)")
        print()
        print("The command will:")
        print("  - Scan for all .py files in the directory tree")
        print("  - Find class definitions using regex")
        print("  - Generate appropriate import statements")
        print("  - Write everything to __init__.py file")
        print()
        print("Files and directories starting with '_' are ignored.")