#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
TradingView警报 -> Telegram转发机器人

这个脚本创建一个FastAPI服务器来接收TradingView的警报，
并将它们转发到指定的Telegram群组或用户。
"""

import os
import json
import logging
from typing import Dict, Any, Optional
import asyncio

import uvicorn
from fastapi import FastAPI, Request, HTTPException, Depends, Header
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv
from telegram import Bot
from telegram.error import TelegramError

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
PORT = int(os.getenv("PORT", "8000"))

# 检查必要的环境变量
if not all([TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, WEBHOOK_SECRET]):
    logger.error("缺少必要的环境变量。请检查.env文件。")
    exit(1)

# 创建FastAPI应用
app = FastAPI(title="TradingView到Telegram转发机器人")

# 创建全局的异步Telegram机器人实例
telegram_bot = None

# 添加消息去重缓存
from collections import deque
from datetime import datetime, timedelta
import hashlib

# 存储最近的消息哈希，避免重复
recent_messages = deque(maxlen=100)
message_timestamps = {}

async def get_telegram_bot():
    """获取或创建Telegram机器人实例"""
    global telegram_bot
    if telegram_bot is None:
        telegram_bot = Bot(token=TELEGRAM_BOT_TOKEN)
    return telegram_bot


class TradingViewAlert(BaseModel):
    """
    TradingView警报数据模型
    
    可以根据TradingView警报的实际格式进行调整
    """
    ticker: Optional[str] = None
    strategy: Optional[str] = None
    price: Optional[float] = None
    action: Optional[str] = None
    message: Optional[str] = None
    
    # 允许额外字段
    class Config:
        extra = "allow"


async def verify_webhook_secret(secret: Optional[str] = None):
    """
    验证TradingView请求中的密钥
    
    Args:
        secret: URL参数中的密钥
        
    Returns:
        None: 如果验证成功
        
    Raises:
        HTTPException: 如果验证失败
    """
    if secret != WEBHOOK_SECRET:
        logger.warning(f"无效的webhook密钥: {secret}")
        raise HTTPException(status_code=403, detail="无效的密钥")
    return None


async def format_telegram_message(alert_data: Dict[str, Any]) -> str:
    """
    格式化Telegram消息
    
    Args:
        alert_data: TradingView警报数据
        
    Returns:
        str: 格式化后的Telegram消息
    """
    # 处理专门的交易格式
    if all(key in alert_data for key in ["ticker", "action", "timeframe", "entry_price", "stop_loss"]):
        # 格式化开仓方向
        action = str(alert_data.get("action", "")).lower()
        if action in ["buy", "long"]:
            direction = "做多 🟢"
            direction_emoji = "📈"
        elif action in ["sell", "short"]:
            direction = "做空 🔴"
            direction_emoji = "📉"
        else:
            direction = alert_data.get("action", "未知")
            direction_emoji = "📊"
        
        # 计算风险百分比
        try:
            entry_price = float(alert_data.get("entry_price", 0))
            stop_loss = float(alert_data.get("stop_loss", 0))
            if entry_price > 0 and stop_loss > 0:
                risk_percent = abs((entry_price - stop_loss) / entry_price * 100)
                risk_display = f"{risk_percent:.2f}%"
            else:
                risk_display = "N/A"
        except:
            risk_display = "N/A"
        
        # 格式化价格显示
        try:
            entry_price_display = f"{float(alert_data.get('entry_price', 0)):,.4f}"
            stop_loss_display = f"{float(alert_data.get('stop_loss', 0)):,.4f}"
        except:
            entry_price_display = str(alert_data.get('entry_price', 'N/A'))
            stop_loss_display = str(alert_data.get('stop_loss', 'N/A'))
        
        # 构建专业的交易消息
        message_parts = [
            f"{direction_emoji} *交易信号 - {alert_data.get('ticker', 'N/A')}*",
            "",
            f"📊 *币种:* `{alert_data.get('ticker', 'N/A')}`",
            f"🎯 *开仓方向:* {direction}",
            f"⏱ *图表周期:* `{alert_data.get('timeframe', 'N/A')}`",
            f"💰 *开仓价:* `{entry_price_display}`",
            f"🛑 *止损价:* `{stop_loss_display}`",
            f"📉 *风险比例:* `{risk_display}`",
            "",
            f"⚠️ *{alert_data.get('message', '合理管理仓位')}*"
        ]
        
        # 添加时间戳（如果有）
        if alert_data.get('time') or alert_data.get('timestamp'):
            time_str = alert_data.get('time') or alert_data.get('timestamp')
            message_parts.append(f"\n⏰ `{time_str}`")
        
        return "\n".join(message_parts)
    
    # 如果有自定义消息，直接使用
    if alert_data.get("message") and len(alert_data) == 1:
        return alert_data["message"]
    
    # 否则构建一个通用格式化的消息
    message_parts = ["🔔 *TradingView警报*"]
    
    if alert_data.get("ticker"):
        message_parts.append(f"📊 *交易对:* `{alert_data['ticker']}`")
    
    if alert_data.get("strategy"):
        message_parts.append(f"📈 *策略:* `{alert_data['strategy']}`")
    
    if alert_data.get("price"):
        message_parts.append(f"💰 *价格:* `{alert_data['price']}`")
    
    if alert_data.get("action"):
        action = alert_data["action"]
        emoji = "🟢" if action.lower() in ["buy", "long"] else "🔴" if action.lower() in ["sell", "short"] else "⚪"
        message_parts.append(f"{emoji} *操作:* `{action}`")
    
    # 添加其他字段
    for key, value in alert_data.items():
        if key not in ["ticker", "strategy", "price", "action", "message"] and value is not None:
            message_parts.append(f"*{key}:* `{value}`")
    
    # 添加自定义消息（如果有）
    if alert_data.get("message"):
        message_parts.append(f"\n💬 *备注:* {alert_data['message']}")
    
    return "\n".join(message_parts)


async def send_telegram_message(message: str) -> bool:
    """
    发送Telegram消息
    
    Args:
        message: 要发送的消息
        
    Returns:
        bool: 是否发送成功
    """
    try:
        # 直接使用全局bot实例
        bot = Bot(token=TELEGRAM_BOT_TOKEN)
        
        # 使用异步方式发送消息
        await bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=message,
            parse_mode="Markdown"
        )
        logger.info("成功发送Telegram消息")
        return True
    except TelegramError as e:
        logger.error(f"发送Telegram消息时出错: {e}")
        return False
    except Exception as e:
        logger.error(f"发送消息时发生未知错误: {e}")
        return False


@app.post("/webhook")
async def tradingview_webhook(request: Request, secret: Optional[str] = None):
    """
    处理来自TradingView的webhook请求
    
    Args:
        request: FastAPI请求对象
        secret: URL参数中的密钥
        
    Returns:
        JSONResponse: API响应
    """
    # 验证密钥
    if secret != WEBHOOK_SECRET:
        logger.warning(f"无效的webhook密钥: {secret}")
        raise HTTPException(status_code=403, detail="无效的密钥")
    
    try:
        # 获取请求体
        body = await request.body()
        
        # 生成消息哈希用于去重
        message_hash = hashlib.md5(body).hexdigest()
        current_time = datetime.now()
        
        # 检查是否是重复消息（5秒内的相同消息视为重复）
        if message_hash in message_timestamps:
            last_time = message_timestamps[message_hash]
            if current_time - last_time < timedelta(seconds=5):
                logger.info(f"忽略重复消息: {message_hash}")
                return JSONResponse(content={"status": "ignored", "message": "重复消息已忽略"})
        
        # 更新消息时间戳
        message_timestamps[message_hash] = current_time
        
        # 清理过期的时间戳（超过1分钟的）
        expired_hashes = [h for h, t in message_timestamps.items() 
                         if current_time - t > timedelta(minutes=1)]
        for h in expired_hashes:
            del message_timestamps[h]
        
        # 尝试解析JSON
        try:
            alert_data = json.loads(body)
        except json.JSONDecodeError:
            # 如果不是JSON，尝试将其作为文本处理
            alert_data = {"message": body.decode("utf-8")}
        
        # 验证和处理警报数据
        alert = TradingViewAlert(**alert_data)
        
        # 格式化Telegram消息
        message = await format_telegram_message(alert_data)
        
        # 发送Telegram消息
        success = await send_telegram_message(message)
        
        if success:
            logger.info("成功发送Telegram消息")
            return JSONResponse(content={"status": "success", "message": "警报已转发到Telegram"})
        else:
            logger.error("发送Telegram消息失败")
            return JSONResponse(
                status_code=500,
                content={"status": "error", "message": "发送Telegram消息失败"}
            )
            
    except Exception as e:
        logger.exception(f"处理webhook时出错: {e}")
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": f"处理请求时出错: {str(e)}"})


@app.get("/")
async def root():
    """
    根路径处理程序
    
    Returns:
        dict: 简单的状态消息
    """
    return {"status": "running", "message": "TradingView到Telegram转发机器人正在运行"}


@app.get("/health")
async def health_check():
    """
    健康检查端点
    
    Returns:
        dict: 健康状态
    """
    return {"status": "healthy"}


if __name__ == "__main__":
    # 打印启动信息
    print("\n" + "="*50)
    print("🚀 TradingView到Telegram转发机器人")
    print("="*50)
    print(f"✅ 服务器地址: http://{HOST}:{PORT}")
    print(f"✅ Webhook URL: http://{HOST}:{PORT}/webhook?secret=YOUR_SECRET")
    print(f"✅ 健康检查: http://{HOST}:{PORT}/health")
    print("="*50)
    print("⏳ 正在启动服务器...")
    print("📝 按 Ctrl+C 停止服务器")
    print("="*50 + "\n")
    
    logger.info(f"启动服务器在 {HOST}:{PORT}")
    uvicorn.run("bot:app", host=HOST, port=PORT, reload=False)