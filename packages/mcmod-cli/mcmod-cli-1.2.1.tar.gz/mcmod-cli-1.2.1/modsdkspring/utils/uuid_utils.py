# -*- coding: utf-8 -*-
import uuid
import random
import string


def generate_uuid():
    """生成UUID字符串"""
    return str(uuid.uuid4())


def generate_random_string(length=8):
    """生成随机字符串"""
    if length <= 0:
        return ""
    
    chars = string.ascii_lowercase + string.digits
    return ''.join(random.choice(chars) for _ in range(length))