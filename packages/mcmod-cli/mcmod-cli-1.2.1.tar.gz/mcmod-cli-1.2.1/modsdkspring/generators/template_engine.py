# -*- coding: utf-8 -*-
import os
import re
from ..utils.file_utils import makedirs_compat


class TemplateEngine:
    """简单的模板引擎 - 替代原始的字符串替换"""
    
    @staticmethod
    def render_file(template_path, output_path, variables):
        """渲染单个文件模板"""
        if not os.path.exists(template_path):
            raise FileNotFoundError("Template file not found: {}".format(template_path))
            
        with open(template_path, 'r') as f:
            content = f.read()
        
        rendered_content = TemplateEngine.render_string(content, variables)
        
        makedirs_compat(os.path.dirname(output_path))
        with open(output_path, 'w') as f:
            f.write(rendered_content)
    
    @staticmethod
    def render_string(template_string, variables):
        """渲染字符串模板"""
        if not template_string:
            return ""
            
        result = template_string
        for key, value in variables.items():
            # 使用 [KEY] 格式的占位符替换
            placeholder = "[{}]".format(key)
            result = result.replace(placeholder, str(value))
        
        return result
    
    @staticmethod
    def render_directory(template_dir, output_dir, variables, exclude_patterns=None):
        """递归渲染整个目录"""
        if not os.path.exists(template_dir):
            raise FileNotFoundError("Template directory not found: {}".format(template_dir))

        exclude_patterns = exclude_patterns or []

        for root, dirs, files in os.walk(template_dir):
            # 计算相对路径
            rel_path = os.path.relpath(root, template_dir)
            if rel_path == ".":
                target_dir = output_dir
            else:
                target_dir = os.path.join(output_dir, rel_path)

            # 创建目标目录
            makedirs_compat(target_dir)

            # 处理文件
            for file in files:
                if TemplateEngine._should_exclude(file, exclude_patterns):
                    continue

                template_file = os.path.join(root, file)
                # 对文件名也进行模板替换
                rendered_filename = TemplateEngine.render_string(file, variables)
                target_file = os.path.join(target_dir, rendered_filename)

                # 判断是否为二进制文件
                if TemplateEngine._is_binary_file(template_file):
                    # 二进制文件直接复制
                    TemplateEngine._copy_binary_file(template_file, target_file)
                else:
                    # 文本文件进行模板渲染
                    TemplateEngine.render_file(template_file, target_file, variables)
    
    @staticmethod
    def _should_exclude(filename, patterns):
        """检查文件是否应该被排除"""
        for pattern in patterns:
            if re.match(pattern, filename):
                return True
        return False

    @staticmethod
    def _is_binary_file(file_path):
        """判断文件是否为二进制文件"""
        # 定义二进制文件扩展名
        binary_extensions = {
            '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.ico', '.tiff',
            '.mp3', '.wav', '.ogg', '.mp4', '.avi', '.mov',
            '.zip', '.rar', '.7z', '.tar', '.gz',
            '.exe', '.dll', '.so', '.dylib',
            '.pdf', '.doc', '.docx', '.xls', '.xlsx'
        }

        file_ext = os.path.splitext(file_path)[1].lower()
        return file_ext in binary_extensions

    @staticmethod
    def _copy_binary_file(src_path, dst_path):
        """复制二进制文件"""
        import shutil
        makedirs_compat(os.path.dirname(dst_path))
        shutil.copy2(src_path, dst_path)