#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试Telegram机器人连接
"""

import os
import asyncio
from dotenv import load_dotenv
from telegram import Bot
from telegram.error import TelegramError

# 加载环境变量
load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

async def test_telegram():
    print("测试Telegram机器人连接...")
    print(f"Bot Token: {TELEGRAM_BOT_TOKEN[:10]}...")
    print(f"Chat ID: {TELEGRAM_CHAT_ID}")
    
    try:
        bot = Bot(token=TELEGRAM_BOT_TOKEN)
        
        # 获取机器人信息
        bot_info = await bot.get_me()
        print(f"\n✅ 机器人信息:")
        print(f"  用户名: @{bot_info.username}")
        print(f"  名称: {bot_info.first_name}")
        
        # 发送测试消息
        print(f"\n正在发送测试消息到 {TELEGRAM_CHAT_ID}...")
        message = await bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text="🔧 测试消息：机器人连接正常！"
        )
        print("✅ 消息发送成功！")
        
    except TelegramError as e:
        print(f"\n❌ 错误: {e}")
        print("\n可能的原因:")
        print("1. 机器人Token无效")
        print("2. 机器人未加入指定的群组")
        print("3. Chat ID 错误")
        print("4. 网络连接问题")
    except Exception as e:
        print(f"\n❌ 未知错误: {e}")

if __name__ == "__main__":
    asyncio.run(test_telegram())