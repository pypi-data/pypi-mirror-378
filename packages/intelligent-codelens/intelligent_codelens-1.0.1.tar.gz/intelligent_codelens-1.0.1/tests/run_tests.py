#!/usr/bin/env python3
"""
测试运行脚本
提供便捷的测试执行方式
"""

import sys
import os
import subprocess
import argparse
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def run_command(cmd, description=""):
    """运行命令并处理结果"""
    if description:
        print(f"\n{'='*60}")
        print(f"🚀 {description}")
        print(f"{'='*60}")
    
    print(f"执行命令: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=project_root)
        
        if result.stdout:
            print("标准输出:")
            print(result.stdout)
        
        if result.stderr:
            print("错误输出:")
            print(result.stderr)
        
        if result.returncode == 0:
            print(f"✅ {description or '命令'} 执行成功")
        else:
            print(f"❌ {description or '命令'} 执行失败 (退出码: {result.returncode})")
        
        return result.returncode == 0
    
    except Exception as e:
        print(f"❌ 执行命令时出错: {e}")
        return False


def run_all_tests():
    """运行所有测试"""
    cmd = [sys.executable, "-m", "pytest", "tests/", "-v"]
    return run_command(cmd, "运行所有测试")


def run_unit_tests():
    """运行单元测试"""
    cmd = [sys.executable, "-m", "pytest", "tests/", "-v", "-m", "unit"]
    return run_command(cmd, "运行单元测试")


def run_integration_tests():
    """运行集成测试"""
    cmd = [sys.executable, "-m", "pytest", "tests/", "-v", "-m", "integration"]
    return run_command(cmd, "运行集成测试")


def run_specific_module(module):
    """运行特定模块的测试"""
    test_file = f"tests/{module}/test_{module}.py"
    if not os.path.exists(test_file):
        print(f"❌ 测试文件不存在: {test_file}")
        return False
    
    cmd = [sys.executable, "-m", "pytest", test_file, "-v"]
    return run_command(cmd, f"运行{module}模块测试")


def run_with_coverage():
    """运行测试并生成覆盖率报告"""
    cmd = [
        sys.executable, "-m", "pytest", "tests/", "-v",
        "--cov=.", "--cov-report=html:tests/htmlcov", 
        "--cov-report=term-missing", "--cov-exclude=tests/*"
    ]
    success = run_command(cmd, "运行测试并生成覆盖率报告")
    
    if success:
        print(f"\n📊 覆盖率报告已生成:")
        print(f"   HTML报告: {project_root}/tests/htmlcov/index.html")
        print(f"   在浏览器中打开: file://{project_root}/tests/htmlcov/index.html")
    
    return success


def run_performance_tests():
    """运行性能测试"""
    cmd = [sys.executable, "-m", "pytest", "tests/", "-v", "-m", "slow", "--durations=0"]
    return run_command(cmd, "运行性能测试")


def run_quick_tests():
    """运行快速测试（排除慢速测试）"""
    cmd = [sys.executable, "-m", "pytest", "tests/", "-v", "-m", "not slow"]
    return run_command(cmd, "运行快速测试")


def check_test_environment():
    """检查测试环境"""
    print("🔍 检查测试环境...")
    
    # 检查Python版本
    print(f"Python版本: {sys.version}")
    
    # 检查必要的包
    required_packages = [
        'pytest', 'pytest-cov', 'pytest-asyncio', 
        'sqlite3', 'tree_sitter', 'fastapi', 'uvicorn'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            if package == 'sqlite3':
                import sqlite3
            else:
                __import__(package.replace('-', '_'))
            print(f"✅ {package} 已安装")
        except ImportError:
            print(f"❌ {package} 未安装")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️  缺少以下包: {', '.join(missing_packages)}")
        print("请运行以下命令安装:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    # 检查测试文件
    test_files = [
        "tests/core/test_semantic_search.py",
        "tests/database/test_database.py",
        "tests/indexer/test_indexer.py",
        "tests/parser/test_tree_parser.py",
        "tests/api/test_api.py",
        "tests/mcp/test_mcp_server.py"
    ]
    
    for test_file in test_files:
        if os.path.exists(test_file):
            print(f"✅ {test_file} 存在")
        else:
            print(f"❌ {test_file} 不存在")
    
    print("✅ 测试环境检查完成")
    return True


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="代码搜索系统测试运行器")
    parser.add_argument("--all", action="store_true", help="运行所有测试")
    parser.add_argument("--unit", action="store_true", help="运行单元测试")
    parser.add_argument("--integration", action="store_true", help="运行集成测试")
    parser.add_argument("--coverage", action="store_true", help="运行测试并生成覆盖率报告")
    parser.add_argument("--performance", action="store_true", help="运行性能测试")
    parser.add_argument("--quick", action="store_true", help="运行快速测试")
    parser.add_argument("--module", type=str, help="运行特定模块的测试 (core, database, indexer, parser, api, mcp)")
    parser.add_argument("--check", action="store_true", help="检查测试环境")
    
    args = parser.parse_args()
    
    # 如果没有参数，显示帮助
    if not any(vars(args).values()):
        parser.print_help()
        return
    
    success = True
    
    if args.check:
        success &= check_test_environment()
    
    if args.all:
        success &= run_all_tests()
    
    if args.unit:
        success &= run_unit_tests()
    
    if args.integration:
        success &= run_integration_tests()
    
    if args.coverage:
        success &= run_with_coverage()
    
    if args.performance:
        success &= run_performance_tests()
    
    if args.quick:
        success &= run_quick_tests()
    
    if args.module:
        success &= run_specific_module(args.module)
    
    if success:
        print("\n🎉 所有操作完成!")
        sys.exit(0)
    else:
        print("\n💥 某些操作失败!")
        sys.exit(1)


if __name__ == "__main__":
    main()