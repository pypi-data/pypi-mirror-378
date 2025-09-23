# -*- coding: utf-8 -*-
import sys
from modsdkspring.cli.init_command import InitCommand
from modsdkspring.cli.import_command import ImportCommand


class CommandDispatcher:
    """命令分发器 - 替代main.py中的if/else分支"""
    
    def __init__(self, package_path):
        self.package_path = package_path
        self.commands = {
            'init': InitCommand(package_path),
            'import': ImportCommand()
        }
    
    def dispatch(self, args=None):
        """分发命令执行"""
        if args is None:
            args = sys.argv
        
        if len(args) <= 1:
            self._show_help()
            return
        
        command_name = args[1]
        command_args = args[2:] if len(args) > 2 else []
        
        if command_name not in self.commands:
            print("Unknown command: {}".format(command_name))
            self._show_help()
            return
        
        try:
            self.commands[command_name].execute(command_args)
        except Exception as e:
            print("Error executing command '{}': {}".format(command_name, e))
            return 1
        
        return 0
    
    def _show_help(self):
        """显示帮助信息"""
        print("Usage: mcmod <command> [options]")
        print()
        print("Available commands:")
        print("  init     - Initialize a new MOD project")
        print("  import   - Generate __init__.py files with class imports")
        print()
        print("For help on a specific command, use: mcmod <command> --help")