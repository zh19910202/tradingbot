#!/bin/bash

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "======================================"
echo "TradingView Bot 状态检查"
echo "======================================"

# 1. 检查进程是否运行
echo -n "检查进程状态... "
if pgrep -f "python.*bot.py" > /dev/null; then
    echo -e "${GREEN}✓ 运行中${NC}"
    PID=$(pgrep -f "python.*bot.py")
    echo "  PID: $PID"
else
    echo -e "${RED}✗ 未运行${NC}"
    echo "  请运行: ./start.sh 或 python bot.py"
    exit 1
fi

# 2. 检查端口
echo -n "检查端口 8000... "
if lsof -i :8000 | grep LISTEN > /dev/null 2>&1; then
    echo -e "${GREEN}✓ 正在监听${NC}"
else
    echo -e "${RED}✗ 端口未监听${NC}"
    exit 1
fi

# 3. 检查健康端点
echo -n "检查健康状态... "
HEALTH_RESPONSE=$(curl -s http://localhost:8000/health 2>/dev/null)
if [[ "$HEALTH_RESPONSE" == *"healthy"* ]]; then
    echo -e "${GREEN}✓ 健康${NC}"
else
    echo -e "${RED}✗ 不健康${NC}"
    echo "  响应: $HEALTH_RESPONSE"
    exit 1
fi

# 4. 检查API响应
echo -n "检查API状态... "
API_RESPONSE=$(curl -s http://localhost:8000/ 2>/dev/null)
if [[ "$API_RESPONSE" == *"running"* ]]; then
    echo -e "${GREEN}✓ API运行正常${NC}"
else
    echo -e "${YELLOW}⚠ API响应异常${NC}"
    echo "  响应: $API_RESPONSE"
fi

# 5. 检查环境变量
echo -n "检查配置文件... "
if [ -f ".env" ]; then
    echo -e "${GREEN}✓ .env 文件存在${NC}"
    # 检查必要的环境变量
    if grep -q "TELEGRAM_BOT_TOKEN=" .env && grep -q "TELEGRAM_CHAT_ID=" .env && grep -q "WEBHOOK_SECRET=" .env; then
        echo -e "  ${GREEN}✓ 必要配置已设置${NC}"
    else
        echo -e "  ${YELLOW}⚠ 请检查配置是否完整${NC}"
    fi
else
    echo -e "${RED}✗ .env 文件不存在${NC}"
fi

echo ""
echo "======================================"
echo -e "${GREEN}✓ 机器人运行正常！${NC}"
echo ""
echo "Webhook URL 格式:"
echo "http://your-server:8000/webhook?secret=YOUR_WEBHOOK_SECRET"
echo ""
echo "停止服务: pkill -f 'python.*bot.py'"
echo "查看日志: 在运行bot.py的终端查看"
echo "======================================"