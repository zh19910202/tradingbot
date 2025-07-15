#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import os
from dotenv import load_dotenv
from telegram import Bot
from telegram.constants import ParseMode

# 加载环境变量
load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

async def send_test_trading_signal():
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    
    # 构建交易信号消息
    message = """📉 *交易信号 - ETHUSDT*

📊 *币种:* `ETHUSDT`
🎯 *开仓方向:* 做空 🔴
⏱ *图表周期:* `1h`
💰 *开仓价:* `3,200.5678`
🛑 *止损价:* `3,250.1234`
📉 *风险比例:* `1.54%`

⚠️ *合理管理仓位*

⏰ `2025-01-15 01:15:00`"""
    
    try:
        print("正在发送交易信号消息...")
        await bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=message,
            parse_mode=ParseMode.MARKDOWN
        )
        print("✅ 交易信号发送成功！")
    except Exception as e:
        print(f"❌ 发送失败: {e}")

if __name__ == "__main__":
    asyncio.run(send_test_trading_signal())