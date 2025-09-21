#!/bin/bash

# MCP 代码搜索服务器自动设置脚本
# 使用方法: ./scripts/setup_mcp.sh [项目路径]

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查依赖
check_dependencies() {
    print_info "检查系统依赖..."
    
    # 检查Python
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 未安装，请先安装 Python 3.8+"
        exit 1
    fi
    
    # 检查Python版本
    python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    if [[ $(echo "$python_version < 3.8" | bc -l) -eq 1 ]]; then
        print_error "Python 版本过低 ($python_version)，需要 3.8+"
        exit 1
    fi
    
    print_success "Python $python_version 检查通过"
}

# 安装Python依赖
install_dependencies() {
    print_info "安装Python依赖包..."
    
    if [ -f "requirements.txt" ]; then
        pip3 install -r requirements.txt
        print_success "依赖包安装完成"
    else
        print_warning "未找到 requirements.txt 文件"
    fi
}

# 配置MCP服务器
configure_mcp() {
    local project_path=${1:-"."}
    local config_file="config/mcp_config.yaml"
    
    print_info "配置MCP服务器..."
    
    # 检查配置文件是否存在
    if [ ! -f "$config_file" ]; then
        print_error "配置文件 $config_file 不存在"
        exit 1
    fi
    
    # 备份原配置文件
    cp "$config_file" "${config_file}.backup.$(date +%Y%m%d_%H%M%S)"
    print_info "已备份原配置文件"
    
    # 获取绝对路径
    if [ "$project_path" != "." ]; then
        project_path=$(realpath "$project_path")
    fi
    
    # 更新配置文件中的路径
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' "s|path: \".\"|path: \"$project_path\"|g" "$config_file"
    else
        # Linux
        sed -i "s|path: \".\"|path: \"$project_path\"|g" "$config_file"
    fi
    
    print_success "配置文件已更新，搜索路径设置为: $project_path"
}

# 创建启动脚本
create_startup_script() {
    local startup_script="start_mcp_server.sh"
    
    print_info "创建启动脚本..."
    
    cat > "$startup_script" << 'EOF'
#!/bin/bash

# MCP 服务器启动脚本

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}启动 MCP 代码搜索服务器...${NC}"

# 检查配置文件
if [ ! -f "config/mcp_config.yaml" ]; then
    echo "错误: 配置文件不存在，请先运行 setup_mcp.sh"
    exit 1
fi

# 启动服务器
echo -e "${GREEN}使用 FastMCP 服务器启动...${NC}"
python3 src/mcp/fastmcp_server.py

# 如果FastMCP失败，尝试标准MCP服务器
if [ $? -ne 0 ]; then
    echo -e "${GREEN}尝试使用标准 MCP 服务器启动...${NC}"
    python3 src/mcp/mcp_server.py
fi
EOF

    chmod +x "$startup_script"
    print_success "启动脚本已创建: $startup_script"
}

# 测试配置
test_configuration() {
    print_info "测试MCP服务器配置..."
    
    # 测试模块导入
    python3 -c "
import sys
import os

# 添加项目路径到Python搜索路径
project_root = os.getcwd()
src_path = os.path.join(project_root, 'src')
core_path = os.path.join(project_root, 'src', 'core')

sys.path.insert(0, src_path)
sys.path.insert(0, core_path)

try:
    from semantic_search import SemanticSearchEngine
    from database import CodeDatabase
    print('✓ 核心模块导入成功')
except ImportError as e:
    print(f'✗ 模块导入失败: {e}')
    sys.exit(1)
"
    
    if [ $? -eq 0 ]; then
        print_success "配置测试通过"
    else
        print_error "配置测试失败"
        exit 1
    fi
}

# 显示使用说明
show_usage() {
    echo "MCP 代码搜索服务器设置脚本"
    echo ""
    echo "使用方法:"
    echo "  $0 [选项] [项目路径]"
    echo ""
    echo "选项:"
    echo "  -h, --help     显示此帮助信息"
    echo "  -t, --test     仅测试配置，不进行设置"
    echo ""
    echo "示例:"
    echo "  $0                           # 使用当前目录"
    echo "  $0 /path/to/project         # 使用指定项目路径"
    echo "  $0 --test                   # 测试当前配置"
    echo ""
}

# 主函数
main() {
    local project_path="."
    local test_only=false
    
    # 解析命令行参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_usage
                exit 0
                ;;
            -t|--test)
                test_only=true
                shift
                ;;
            -*)
                print_error "未知选项: $1"
                show_usage
                exit 1
                ;;
            *)
                project_path="$1"
                shift
                ;;
        esac
    done
    
    print_info "开始设置 MCP 代码搜索服务器..."
    
    # 检查是否在正确的目录
    if [ ! -f "src/mcp/fastmcp_server.py" ]; then
        print_error "请在项目根目录运行此脚本"
        exit 1
    fi
    
    if [ "$test_only" = true ]; then
        test_configuration
        exit 0
    fi
    
    # 验证项目路径
    if [ "$project_path" != "." ] && [ ! -d "$project_path" ]; then
        print_error "项目路径不存在: $project_path"
        exit 1
    fi
    
    # 执行设置步骤
    check_dependencies
    install_dependencies
    configure_mcp "$project_path"
    create_startup_script
    test_configuration
    
    print_success "MCP 服务器设置完成！"
    echo ""
    print_info "接下来的步骤:"
    echo "1. 检查配置文件: config/mcp_config.yaml"
    echo "2. 根据需要调整安全设置和性能参数"
    echo "3. 运行启动脚本: ./start_mcp_server.sh"
    echo ""
    print_info "更多配置选项请参考: docs/MCP_SETUP_GUIDE.md"
}

# 运行主函数
main "$@"