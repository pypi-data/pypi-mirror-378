# -*- coding: utf-8 -*-
import os
import re


def makedirs_compat(path):
    """兼容Python 2.7的makedirs函数，相当于exist_ok=True"""
    try:
        os.makedirs(path)
    except OSError:
        if not os.path.isdir(path):
            raise


def copytree_compat(src, dst):
    """兼容Python 2.7的copytree函数，相当于dirs_exist_ok=True"""
    import shutil
    
    # 如果目标目录存在，先删除
    if os.path.exists(dst):
        shutil.rmtree(dst)
    
    shutil.copytree(src, dst)


def find_python_classes(directory_path):
    """在目录中查找Python类定义"""
    if not os.path.exists(directory_path):
        return []
    
    class_pattern = r'class\s+([a-zA-Z][a-zA-Z0-9_]*)(\(.*\))?\s*:'
    classes = []
    
    for root, dirs, files in os.walk(directory_path):
        # 跳过以_开头的文件和目录
        dirs[:] = [d for d in dirs if not d.startswith('_')]
        
        for file in files:
            if not file.endswith('.py') or file.startswith('_'):
                continue
                
            file_path = os.path.join(root, file)
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                
                matches = re.findall(class_pattern, content)
                for class_name, _ in matches:
                    # 计算模块路径
                    rel_path = os.path.relpath(file_path, directory_path)
                    module_path = rel_path[:-3].replace(os.sep, '.')  # 去掉.py，替换路径分隔符
                    
                    classes.append({
                        'class_name': class_name,
                        'module_path': module_path,
                        'file_path': file_path
                    })
                    
            except Exception as e:
                print("Warning: Could not read file {}: {}".format(file_path, e))
                continue
    
    return classes


def generate_init_py(directory_path):
    """生成__init__.py文件内容"""
    classes = find_python_classes(directory_path)
    
    imports = []
    for cls_info in classes:
        import_line = "from {} import {}".format(cls_info['module_path'], cls_info['class_name'])
        imports.append(import_line)
    
    return '\n'.join(imports) + '\n' if imports else ''