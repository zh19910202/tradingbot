#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
简化版本的TradingView警报转发机器人
"""

import os
import json
import logging
import asyncio
from typing import Dict, Any, Optional

import uvicorn
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import telegram

# 配置日志
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# 加载环境变量
load_dotenv()

# 获取环境变量
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8001"))  # 使用不同端口避免冲突

# 创建FastAPI应用
app = FastAPI(title="TradingView Bot (Simple)")

# 创建bot实例
bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)

def format_message(data: Dict[str, Any]) -> str:
    """格式化消息"""
    # 专门的交易格式
    if all(key in data for key in ["ticker", "action", "timeframe", "entry_price", "stop_loss"]):
        action = str(data.get("action", "")).lower()
        if action in ["buy", "long"]:
            direction = "做多 🟢"
            emoji = "📈"
        elif action in ["sell", "short"]:
            direction = "做空 🔴"
            emoji = "📉"
        else:
            direction = data.get("action", "未知")
            emoji = "📊"
        
        return f"""{emoji} **交易信号 - {data.get('ticker')}**

📊 **币种:** {data.get('ticker')}
🎯 **开仓方向:** {direction}
⏱ **图表周期:** {data.get('timeframe')}
💰 **开仓价:** {data.get('entry_price')}
🛑 **止损价:** {data.get('stop_loss')}

⚠️ **{data.get('message', '合理管理仓位')}**"""
    
    # 简单消息
    return json.dumps(data, ensure_ascii=False, indent=2)

@app.post("/webhook")
async def webhook(request: Request, secret: Optional[str] = None):
    """处理webhook请求"""
    # 验证密钥
    if secret != WEBHOOK_SECRET:
        logger.warning(f"无效的密钥: {secret}")
        raise HTTPException(status_code=403, detail="无效的密钥")
    
    try:
        # 获取请求数据
        body = await request.body()
        data = json.loads(body)
        logger.info(f"收到数据: {data}")
        
        # 格式化消息
        message = format_message(data)
        
        # 发送消息
        logger.info("正在发送消息到Telegram...")
        await bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=message,
            parse_mode=telegram.constants.ParseMode.MARKDOWN
        )
        
        logger.info("消息发送成功！")
        return JSONResponse(content={"status": "success"})
        
    except Exception as e:
        logger.error(f"错误: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e)}
        )

@app.get("/health")
async def health():
    """健康检查"""
    return {"status": "healthy"}

if __name__ == "__main__":
    print(f"\n{'='*50}")
    print(f"🚀 简化版TradingView Bot")
    print(f"✅ 运行在: http://{HOST}:{PORT}")
    print(f"✅ Webhook: http://{HOST}:{PORT}/webhook?secret=YOUR_SECRET")
    print(f"{'='*50}\n")
    
    uvicorn.run(app, host=HOST, port=PORT)