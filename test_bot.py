#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Telegram机器人测试脚本

这个脚本用于测试Telegram机器人的配置是否正确。
它会尝试发送一条测试消息到配置的Telegram群组或用户。
"""

import os
import sys
import logging
from dotenv import load_dotenv
from telegram import Bot, ParseMode
from telegram.error import TelegramError

# 配置日志
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


async def test_telegram_bot():
    """
    测试Telegram机器人配置
    
    尝试发送一条测试消息到配置的Telegram群组或用户
    """
    # 加载环境变量
    load_dotenv()
    
    # 获取环境变量
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    if not token or not chat_id:
        logger.error("缺少必要的环境变量。请检查.env文件中是否设置了TELEGRAM_BOT_TOKEN和TELEGRAM_CHAT_ID。")
        return False
    
    try:
        # 创建机器人实例
        bot = Bot(token=token)
        
        # 获取机器人信息
        bot_info = await bot.get_me()
        logger.info(f"机器人信息: {bot_info.first_name} (@{bot_info.username})")
        
        # 发送测试消息
        message = (
            "🧪 *测试消息*\n\n"
            "如果您看到这条消息，说明您的Telegram机器人配置正确！\n\n"
            "您现在可以设置TradingView警报，将信息发送到您的机器人。"
        )
        
        await bot.send_message(
            chat_id=chat_id,
            text=message,
            parse_mode=ParseMode.MARKDOWN
        )
        
        logger.info(f"测试消息已成功发送到chat_id: {chat_id}")
        return True
        
    except TelegramError as e:
        logger.error(f"Telegram错误: {e}")
        return False
    except Exception as e:
        logger.error(f"发生错误: {e}")
        return False


if __name__ == "__main__":
    import asyncio
    
    print("正在测试Telegram机器人配置...")
    result = asyncio.run(test_telegram_bot())
    
    if result:
        print("\n✅ 测试成功！您的Telegram机器人配置正确。")
        sys.exit(0)
    else:
        print("\n❌ 测试失败。请检查日志以获取更多信息。")
        sys.exit(1)