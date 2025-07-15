#!/bin/bash

# TradingView到Telegram转发机器人启动脚本

echo "正在启动TradingView到Telegram转发机器人..."

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到Python3，请安装Python3后再试"
    exit 1
fi

# 检查是否已安装依赖
if [ ! -d "venv" ]; then
    echo "首次运行，正在设置虚拟环境..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

# 检查.env文件是否存在
if [ ! -f ".env" ]; then
    echo "未找到.env文件，正在从示例创建..."
    cp .env.example .env
    echo "请编辑.env文件，填写您的Telegram机器人令牌和其他配置"
    echo "完成后重新运行此脚本"
    exit 1
fi

# 启动机器人
echo "正在启动服务器..."
python3 bot.py