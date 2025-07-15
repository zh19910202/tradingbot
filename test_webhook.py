#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
TradingView Webhook测试脚本

这个脚本用于模拟TradingView发送警报到webhook，
帮助测试webhook服务器是否正常工作。
"""

import os
import sys
import json
import argparse
import requests
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 获取环境变量
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")
HOST = os.getenv("HOST", "0.0.0.0")
PORT = os.getenv("PORT", "8000")


def send_test_alert(alert_type="basic", custom_url=None):
    """
    发送测试警报到webhook
    
    Args:
        alert_type: 警报类型，可选值：basic, message, detailed
        custom_url: 自定义webhook URL
        
    Returns:
        bool: 是否发送成功
    """
    # 检查webhook密钥
    if not WEBHOOK_SECRET:
        print("错误: 未设置WEBHOOK_SECRET环境变量。请检查.env文件。")
        return False
    
    # 构建webhook URL
    if custom_url:
        webhook_url = custom_url
    else:
        webhook_url = f"http://{HOST}:{PORT}/webhook"
    
    # 准备请求头
    headers = {
        "Content-Type": "application/json",
        "X-TradingView-Secret": WEBHOOK_SECRET
    }
    
    # 根据类型选择警报数据
    if alert_type == "message":
        payload = {
            "message": "🚨 测试警报！这是一个自定义消息警报。当前价格: 45000.50，动作: BUY"
        }
    elif alert_type == "detailed":
        payload = {
            "ticker": "ETHUSDT",
            "strategy": "RSI超买超卖",
            "price": 3200.75,
            "action": "SELL",
            "rsi": 78.5,
            "timeframe": "1h",
            "notes": "RSI超过70，可能超买"
        }
    else:  # basic
        payload = {
            "ticker": "BTCUSDT",
            "strategy": "均线交叉策略",
            "price": 45000.50,
            "action": "BUY"
        }
    
    # 发送请求
    try:
        print(f"正在发送{alert_type}类型的测试警报到 {webhook_url}...")
        print(f"警报内容: {json.dumps(payload, ensure_ascii=False, indent=2)}")
        
        response = requests.post(webhook_url, headers=headers, json=payload)
        
        # 检查响应
        if response.status_code == 200:
            print(f"\n✅ 成功! 服务器返回: {response.status_code}")
            print(f"响应内容: {response.text}")
            return True
        else:
            print(f"\n❌ 失败! 服务器返回: {response.status_code}")
            print(f"响应内容: {response.text}")
            return False
            
    except requests.RequestException as e:
        print(f"\n❌ 请求错误: {e}")
        return False


if __name__ == "__main__":
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="TradingView Webhook测试工具")
    parser.add_argument(
        "--type", 
        choices=["basic", "message", "detailed"], 
        default="basic",
        help="警报类型: basic(基本), message(自定义消息), detailed(详细)"
    )
    parser.add_argument(
        "--url", 
        help="自定义webhook URL，例如: http://example.com/webhook"
    )
    
    args = parser.parse_args()
    
    # 发送测试警报
    result = send_test_alert(args.type, args.url)
    
    if result:
        sys.exit(0)
    else:
        sys.exit(1)