#!/bin/bash
# MCP Test 数据库配置脚本
# 使用说明：chmod +x setup-db.sh && ./setup-db.sh

echo "🔧 配置 MCP Test 数据库连接..."

# 检测 shell 类型
if [ -n "$ZSH_VERSION" ]; then
    SHELL_RC="$HOME/.zshrc"
    SHELL_NAME="zsh"
elif [ -n "$BASH_VERSION" ]; then
    SHELL_RC="$HOME/.bashrc"
    SHELL_NAME="bash"
else
    SHELL_RC="$HOME/.profile"
    SHELL_NAME="shell"
fi

echo "📍 检测到 $SHELL_NAME shell，配置文件: $SHELL_RC"

# 检查是否已经配置
if grep -q "MONGODB_REMOTE_URI" "$SHELL_RC" 2>/dev/null; then
    echo "⚠️  环境变量已存在，是否要更新？(y/n)"
    read -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ 配置取消"
        exit 0
    fi
    
    # 移除旧配置
    sed -i.bak '/MONGODB_REMOTE_URI/d' "$SHELL_RC"
    sed -i.bak '/MONGODB_URI/d' "$SHELL_RC"
fi

# 添加环境变量到配置文件
echo "" >> "$SHELL_RC"
echo "# MCP Test 数据库配置" >> "$SHELL_RC"
echo 'export MONGODB_REMOTE_URI="mongodb://mcpuser:Zhoubotong1@47.76.139.105:27017/mcpmarket"' >> "$SHELL_RC"
echo 'export MONGODB_URI="mongodb://mcpuser:Zhoubotong1@127.0.0.1:27017/mcpmarket?authSource=admin"' >> "$SHELL_RC"

echo "✅ 数据库连接配置完成！"
echo ""
echo "📋 已添加到 $SHELL_RC:"
echo "   MONGODB_REMOTE_URI (远程数据库)"
echo "   MONGODB_URI (本地数据库)"
echo ""
# 自动重新加载配置
echo "🔄 重新加载配置..."
source "$SHELL_RC"

echo "🧪 测试配置..."
# 检查环境变量是否在配置文件中
if grep -q "MONGODB_REMOTE_URI" "$SHELL_RC" && grep -q "MONGODB_URI" "$SHELL_RC"; then
    echo "   ✅ 环境变量已添加到配置文件"
    
    # 测试 mcp-test 命令
    if command -v mcp-test &> /dev/null; then
        echo "   ✅ mcp-test 命令可用"
        echo ""
        echo "🎉 配置完成！"
        echo ""
        echo "⚠️  重要提示："
        echo "   环境变量已添加到 $SHELL_RC"
        echo "   请运行以下命令使环境变量在当前会话中生效："
        echo "   source $SHELL_RC"
        echo ""
        echo "   或者重新打开终端窗口"
        echo ""
        echo "💡 使用方法:"
        echo "   mcp-test --version"
        echo "   mcp-test --server brave"
    else
        echo "   ⚠️  mcp-test 命令未找到，请先安装："
        echo "   uv tool install mcp-servers-auto-test"
    fi
else
    echo "   ❌ 环境变量设置失败，请手动运行："
    echo "   source $SHELL_RC"
fi
echo ""
echo "💡 使用方法:"
echo "   mcp-test                    # 默认：远程数据库"
echo "   mcp-test --local            # 使用本地数据库"
echo "   mcp-test --server github    # 测试特定服务器"
echo ""
echo "🗑️  配置完成后可以删除此脚本: rm setup-db.sh"
