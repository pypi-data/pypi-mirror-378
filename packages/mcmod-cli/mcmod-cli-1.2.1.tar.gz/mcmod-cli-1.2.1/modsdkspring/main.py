# -*- coding: utf-8 -*-
import os
import sys

# 添加父目录到Python路径，确保能找到modsdkspring包
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modsdkspring.cli.commands import CommandDispatcher


def main():
    """
    控制台命令入口 - 清晰简洁的实现
    """
    package_path = os.path.dirname(__file__)
    dispatcher = CommandDispatcher(package_path)
    return dispatcher.dispatch()

# Legacy function kept for backward compatibility
# Use ProjectGenerator class instead
def initMOD():
    """
    Legacy initMOD function - deprecated
    Use cli.init_command.InitCommand instead
    """
    from modsdkspring.cli.init_command import InitCommand
    import os
    
    package_path = os.path.dirname(__file__)
    command = InitCommand(package_path)
    command.execute([])

# Legacy function kept for backward compatibility
# Use ImportCommand class instead
def initPy(args):
    """
    Legacy initPy function - deprecated
    Use cli.import_command.ImportCommand instead
    """
    from modsdkspring.cli.import_command import ImportCommand
    
    command = ImportCommand()
    # Convert old args format to new format
    if len(args) >= 4 and args[2] == '--path':
        new_args = ['--path', args[3]]
    else:
        new_args = []
    
    command.execute(new_args)


if __name__ == '__main__':
    main()

