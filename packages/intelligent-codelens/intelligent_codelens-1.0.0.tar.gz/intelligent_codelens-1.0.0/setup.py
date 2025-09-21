#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CodeLens - 智能代码搜索引擎安装配置文件
"""

import os
import sys
from pathlib import Path
from setuptools import setup, find_packages

# 确保Python版本要求
if sys.version_info < (3, 8):
    sys.exit("Python 3.8+ is required")

# 项目根目录
ROOT_DIR = Path(__file__).parent.absolute()

# 读取版本信息
def get_version():
    """获取版本信息"""
    version_file = ROOT_DIR / "src" / "_version.py"
    version_dict = {}
    with open(version_file, encoding="utf-8") as f:
        exec(f.read(), version_dict)
    return version_dict["__version__"]

# 读取README
def get_long_description():
    """获取长描述"""
    readme_file = ROOT_DIR / "README.md"
    if readme_file.exists():
        with open(readme_file, encoding="utf-8") as f:
            return f.read()
    return ""

# 读取依赖
def get_requirements():
    """获取依赖列表"""
    requirements_file = ROOT_DIR / "requirements.txt"
    requirements = []
    if requirements_file.exists():
        with open(requirements_file, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    requirements.append(line)
    return requirements

# 开发依赖
dev_requirements = [
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
    "pytest-asyncio>=0.21.0",
    "black>=22.0.0",
    "flake8>=5.0.0",
    "mypy>=1.0.0",
    "isort>=5.10.0",
    "pre-commit>=2.20.0",
]

# 文档依赖
docs_requirements = [
    "sphinx>=5.0.0",
    "sphinx-rtd-theme>=1.0.0",
    "myst-parser>=0.18.0",
]

# 完整安装依赖
all_requirements = dev_requirements + docs_requirements

setup(
    # 基本信息
    name="intelligent-codelens",
    version=get_version(),
    description="智能代码搜索引擎，支持语义搜索和代码分析",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    
    # 作者信息
    author="CodeLens Team",
    author_email="support@codelens.dev",
    maintainer="CodeLens Team",
    maintainer_email="support@codelens.dev",
    
    # 项目链接
    url="https://github.com/your-org/CodeLens",
    project_urls={
        "Bug Reports": "https://github.com/your-org/CodeLens/issues",
        "Source": "https://github.com/your-org/CodeLens",
        "Documentation": "https://codelens.readthedocs.io/",
    },
    
    # 许可证和分类
    license="MIT",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Code Generators",
        "Topic :: Text Processing :: Linguistic",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    
    # 关键词
    keywords="codelens code search semantic ai development tools analysis",
    
    # 包配置
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
    
    # 依赖
    install_requires=get_requirements(),
    extras_require={
        "dev": dev_requirements,
        "docs": docs_requirements,
        "all": all_requirements,
    },
    
    # 包数据
    include_package_data=True,
    package_data={
        "": ["*.yaml", "*.yml", "*.json", "*.md", "*.txt"],
    },
    
    # 入口点
    entry_points={
        "console_scripts": [
            "codelens-mcp=mcp.mcp_server:main",
            "codelens-api=api.web:main",
            "codelens-setup=scripts.setup_mcp:main",
        ],
    },
    
    # 其他配置
    zip_safe=False,
    platforms=["any"],
    
    # 项目状态
    project_status="stable",
)