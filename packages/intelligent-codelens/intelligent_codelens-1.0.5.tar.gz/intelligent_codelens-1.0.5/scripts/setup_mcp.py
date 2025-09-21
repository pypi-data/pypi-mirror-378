#!/usr/bin/env python3
"""
MCP 代码搜索服务器自动设置脚本
使用方法: codelens-setup [项目路径]
"""

import argparse
import os
import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional


def print_info(message: str) -> None:
    """打印信息消息"""
    print(f"\033[0;34m[INFO]\033[0m {message}")


def print_success(message: str) -> None:
    """打印成功消息"""
    print(f"\033[0;32m[SUCCESS]\033[0m {message}")


def print_warning(message: str) -> None:
    """打印警告消息"""
    print(f"\033[1;33m[WARNING]\033[0m {message}")


def print_error(message: str) -> None:
    """打印错误消息"""
    print(f"\033[0;31m[ERROR]\033[0m {message}")


def check_dependencies() -> bool:
    """检查系统依赖"""
    print_info("检查系统依赖...")
    
    # 检查Python版本
    if sys.version_info < (3, 8):
        print_error(f"Python 版本过低 ({sys.version_info.major}.{sys.version_info.minor})，需要 3.8+")
        return False
    
    print_success(f"Python {sys.version_info.major}.{sys.version_info.minor} 检查通过")
    return True


def get_claude_config_path() -> Optional[Path]:
    """获取Claude Desktop配置文件路径"""
    if sys.platform == "darwin":  # macOS
        config_path = Path.home() / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json"
    elif sys.platform == "win32":  # Windows
        config_path = Path.home() / "AppData" / "Roaming" / "Claude" / "claude_desktop_config.json"
    else:  # Linux
        config_path = Path.home() / ".config" / "claude" / "claude_desktop_config.json"
    
    return config_path if config_path.exists() else None


def setup_claude_desktop(project_path: str) -> bool:
    """设置Claude Desktop配置"""
    print_info("设置Claude Desktop配置...")
    
    config_path = get_claude_config_path()
    if not config_path:
        print_warning("未找到Claude Desktop配置文件，请手动配置")
        return False
    
    try:
        # 读取现有配置
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
        else:
            config = {}
        
        # 确保mcpServers存在
        if "mcpServers" not in config:
            config["mcpServers"] = {}
        
        # 添加CodeLens配置
        config["mcpServers"]["codelens"] = {
            "command": "codelens-mcp",
            "args": ["mcp-server"],
            "env": {
                "CODE_PATH": project_path,
                "PYTHONPATH": str(Path(project_path).absolute())
            }
        }
        
        # 写入配置
        config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        print_success(f"Claude Desktop配置已更新: {config_path}")
        return True
        
    except Exception as e:
        print_error(f"设置Claude Desktop配置失败: {e}")
        return False


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="MCP 代码搜索服务器自动设置脚本")
    parser.add_argument("project_path", nargs="?", default=".", help="项目路径 (默认: 当前目录)")
    parser.add_argument("--claude", action="store_true", help="设置Claude Desktop配置")
    parser.add_argument("--version", action="version", version="CodeLens Setup 1.0.0")
    
    args = parser.parse_args()
    
    # 检查依赖
    if not check_dependencies():
        sys.exit(1)
    
    # 获取项目路径
    project_path = Path(args.project_path).absolute()
    if not project_path.exists():
        print_error(f"项目路径不存在: {project_path}")
        sys.exit(1)
    
    print_info(f"项目路径: {project_path}")
    
    # 设置Claude Desktop配置
    if args.claude or True:  # 默认设置Claude Desktop
        if setup_claude_desktop(str(project_path)):
            print_success("设置完成！请重启Claude Desktop以应用配置。")
        else:
            print_warning("Claude Desktop配置设置失败，请手动配置。")
    
    print_success("设置脚本执行完成！")


if __name__ == "__main__":
    main()