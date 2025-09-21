#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
版本信息管理模块
"""

# 版本信息
__version__ = "1.0.1"
__version_info__ = (1, 0, 1)

# 项目信息
__title__ = "CodeLens"
__description__ = "智能代码搜索引擎，支持语义搜索和代码分析"
__author__ = "CodeLens Team"
__author_email__ = "support@codelens.dev"
__license__ = "MIT"
__url__ = "https://github.com/sokis/CodeLens"

# 构建信息
__build__ = "stable"
__status__ = "Production/Stable"

def get_version():
    """
    获取版本字符串
    
    Returns:
        str: 版本字符串
    """
    return __version__

def get_version_info():
    """
    获取版本信息元组
    
    Returns:
        tuple: 版本信息元组 (major, minor, patch)
    """
    return __version_info__

def get_full_version():
    """
    获取完整版本信息
    
    Returns:
        dict: 完整版本信息字典
    """
    return {
        "version": __version__,
        "version_info": __version_info__,
        "title": __title__,
        "description": __description__,
        "author": __author__,
        "author_email": __author_email__,
        "license": __license__,
        "url": __url__,
        "build": __build__,
        "status": __status__
    }