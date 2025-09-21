#!/bin/bash

# Tree-sitter 语法模块安装脚本
# 支持 Python, JavaScript, Java 等语言

set -e

echo "开始安装 Tree-sitter 语法模块..."

# 创建 grammars 目录
mkdir -p grammars
cd grammars

# 安装 Python 语法
if [ ! -d "tree-sitter-python" ]; then
    echo "安装 Python 语法模块..."
    git clone https://github.com/tree-sitter/tree-sitter-python.git
fi

# 安装 JavaScript 语法
if [ ! -d "tree-sitter-javascript" ]; then
    echo "安装 JavaScript 语法模块..."
    git clone https://github.com/tree-sitter/tree-sitter-javascript.git
fi

# 安装 Java 语法
if [ ! -d "tree-sitter-java" ]; then
    echo "安装 Java 语法模块..."
    git clone https://github.com/tree-sitter/tree-sitter-java.git
fi

# 编译语法模块
echo "编译语法模块..."
for dir in tree-sitter-*; do
    if [ -d "$dir" ]; then
        echo "编译 $dir..."
        cd "$dir"
        tree-sitter build
        cd ..
    fi
done

echo "语法模块安装完成！"