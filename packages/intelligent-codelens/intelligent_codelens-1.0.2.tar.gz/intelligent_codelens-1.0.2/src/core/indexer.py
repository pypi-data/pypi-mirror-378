#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
代码索引模块
用于批量解析代码文件并建立索引
"""

import os
import time
from pathlib import Path
from typing import List, Dict, Any, Generator
import yaml

try:
    from .tree_parser import TreeSitterParser
    from .database import CodeDatabase
except ImportError:
    from tree_parser import TreeSitterParser
    from database import CodeDatabase


class CodeIndexer:
    """代码索引器"""
    
    def __init__(self, config_path: str = "config.yaml"):
        """
        初始化索引器
        
        Args:
            config_path: 配置文件路径
        """
        self.config = self._load_config(config_path)
        self.parser = TreeSitterParser(config_path)
        self.db = CodeDatabase(self.config['db_file'])
        
        # 统计信息
        self.stats = {
            'total_files': 0,
            'processed_files': 0,
            'failed_files': 0,
            'total_functions': 0,
            'total_classes': 0,
            'start_time': None,
            'end_time': None
        }
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """
        加载配置文件
        
        Args:
            config_path: 配置文件路径
            
        Returns:
            配置字典
        """
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def index_repository(self, repo_path: str = None) -> Dict[str, Any]:
        """
        索引整个代码仓库
        
        Args:
            repo_path: 仓库路径，如果为 None 则使用配置文件中的路径
            
        Returns:
            索引统计信息
        """
        if repo_path is None:
            repo_path = self.config['repo_path']
        
        print(f"🚀 开始索引代码仓库: {repo_path}")
        self.stats['start_time'] = time.time()
        
        # 清空现有索引
        self.db.clear_index()
        
        # 获取所有需要处理的文件
        files = list(self._get_source_files(repo_path))
        self.stats['total_files'] = len(files)
        
        print(f"📁 找到 {len(files)} 个源代码文件")
        
        # 批量处理文件
        batch_size = self.config.get('batch_size', 100)
        for i in range(0, len(files), batch_size):
            batch = files[i:i + batch_size]
            self._process_batch(batch)
            
            # 显示进度
            progress = (i + len(batch)) / len(files) * 100
            print(f"📊 进度: {progress:.1f}% ({i + len(batch)}/{len(files)})")
        
        self.stats['end_time'] = time.time()
        
        # 输出统计信息
        self._print_stats()
        
        # 获取数据库统计信息并合并到返回结果中
        db_stats = self.db.get_stats()
        self.stats.update(db_stats)
        
        return self.stats
    
    def _get_source_files(self, repo_path: str) -> Generator[str, None, None]:
        """
        获取仓库中的所有源代码文件
        
        Args:
            repo_path: 仓库路径
            
        Yields:
            源代码文件路径
        """
        repo_path = Path(repo_path)
        exclude_dirs = set(self.config.get('exclude_dirs', []))
        file_extensions = []
        
        # 收集所有支持的文件扩展名
        for lang, exts in self.config['file_extensions'].items():
            file_extensions.extend(exts)
        
        for root, dirs, files in os.walk(repo_path):
            # 过滤排除的目录
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            
            for file in files:
                file_path = Path(root) / file
                
                # 检查文件扩展名
                if file_path.suffix.lower() in file_extensions:
                    # 检查文件大小
                    try:
                        if file_path.stat().st_size <= self.config.get('max_file_size', 1048576):
                            yield str(file_path)
                    except OSError:
                        continue
    
    def _process_batch(self, files: List[str]):
        """
        批量处理文件
        
        Args:
            files: 文件路径列表
        """
        for file_path in files:
            try:
                # 解析文件
                result = self.parser.parse_file(file_path)
                if result:
                    # 存储到数据库
                    self.db.store_file_data(result)
                    
                    # 更新统计信息
                    self.stats['processed_files'] += 1
                    self.stats['total_functions'] += len(result['functions'])
                    self.stats['total_classes'] += len(result['classes'])
                else:
                    self.stats['failed_files'] += 1
                    
            except Exception as e:
                print(f"❌ 处理文件 {file_path} 失败: {e}")
                self.stats['failed_files'] += 1
    
    def _print_stats(self):
        """打印索引统计信息"""
        duration = self.stats['end_time'] - self.stats['start_time']
        
        print("\n" + "="*50)
        print("📈 索引完成统计")
        print("="*50)
        print(f"⏱️  总耗时: {duration:.2f} 秒")
        print(f"📁 总文件数: {self.stats['total_files']}")
        print(f"✅ 成功处理: {self.stats['processed_files']}")
        print(f"❌ 处理失败: {self.stats['failed_files']}")
        print(f"🔧 总函数数: {self.stats['total_functions']}")
        print(f"🏗️  总类数: {self.stats['total_classes']}")
        
        if self.stats['processed_files'] > 0:
            avg_time = duration / self.stats['processed_files']
            print(f"⚡ 平均处理速度: {avg_time:.3f} 秒/文件")
        
        # 数据库统计
        db_stats = self.db.get_stats()
        print(f"💾 数据库大小: {db_stats['db_size_mb']:.2f} MB")
        print(f"📊 索引记录数: {db_stats['files'] + db_stats['functions'] + db_stats['classes']}")
        print("="*50)
    
    def update_file(self, file_path: str) -> bool:
        """
        更新单个文件的索引
        
        Args:
            file_path: 文件路径
            
        Returns:
            是否更新成功
        """
        try:
            # 解析文件
            result = self.parser.parse_file(file_path)
            if result:
                # 删除旧索引
                self.db.delete_file_data(file_path)
                
                # 存储新索引
                self.db.store_file_data(result)
                
                print(f"✅ 已更新文件索引: {file_path}")
                return True
            else:
                print(f"❌ 解析文件失败: {file_path}")
                return False
                
        except Exception as e:
            print(f"❌ 更新文件索引失败 {file_path}: {e}")
            return False
    
    def remove_file(self, file_path: str) -> bool:
        """
        从索引中移除文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            是否移除成功
        """
        try:
            self.db.delete_file_data(file_path)
            print(f"✅ 已从索引中移除文件: {file_path}")
            return True
        except Exception as e:
            print(f"❌ 移除文件索引失败 {file_path}: {e}")
            return False


def main():
    """主函数，用于命令行调用"""
    import argparse
    
    parser = argparse.ArgumentParser(description="代码索引工具")
    parser.add_argument("--config", default="config.yaml", help="配置文件路径")
    parser.add_argument("--repo", help="要索引的仓库路径")
    parser.add_argument("--update", help="更新单个文件的索引")
    parser.add_argument("--remove", help="从索引中移除文件")
    
    args = parser.parse_args()
    
    indexer = CodeIndexer(args.config)
    
    if args.update:
        indexer.update_file(args.update)
    elif args.remove:
        indexer.remove_file(args.remove)
    else:
        indexer.index_repository(args.repo)


if __name__ == "__main__":
    main()