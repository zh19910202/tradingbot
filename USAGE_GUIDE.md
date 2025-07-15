# TradingView 到 Telegram 转发机器人使用指南

## 快速开始

### 1. 设置 Telegram 机器人

1. 在 Telegram 中搜索 [@BotFather](https://t.me/BotFather) 并开始对话
2. 发送 `/newbot` 命令创建一个新机器人
3. 按照提示设置机器人名称和用户名
4. 完成后，BotFather 会提供一个 API 令牌，复制它
5. 将 API 令牌添加到 `.env` 文件的 `TELEGRAM_BOT_TOKEN` 字段

### 2. 获取 Telegram 群组 ID

#### 对于群组：

1. 将您的机器人添加到目标群组
2. 在群组中发送任意消息
3. 访问 `https://api.telegram.org/bot<您的API令牌>/getUpdates`
4. 在返回的 JSON 中找到 `chat` 对象中的 `id` 字段，这就是您的群组 ID

#### 对于个人聊天：

1. 在 Telegram 中搜索 [@userinfobot](https://t.me/userinfobot) 并开始对话
2. 它会直接返回您的用户 ID

### 3. 配置环境变量

1. 复制示例环境文件：`cp .env.example .env`
2. 编辑 `.env` 文件，填写以下信息：
   - `TELEGRAM_BOT_TOKEN`：您的 Telegram 机器人令牌
   - `TELEGRAM_CHAT_ID`：目标 Telegram 群组或用户 ID
   - `WEBHOOK_SECRET`：设置一个随机字符串作为密钥
   - `HOST` 和 `PORT`：服务器主机和端口（默认为 0.0.0.0:8000）

### 4. 测试配置

运行测试脚本确认 Telegram 配置正确：

```bash
python test_bot.py
```

如果配置正确，您将在 Telegram 中收到一条测试消息。

### 5. 启动服务器

使用启动脚本运行服务器：

```bash
./start.sh
```

服务器将在指定的主机和端口上运行。

### 6. 配置 TradingView 警报

1. 在 TradingView 中创建一个新的警报
2. 在「警报操作」部分选择「Webhook URL」
3. 输入您的 webhook URL，例如：`http://your-server-address:8000/webhook`
4. 添加一个自定义的请求头：`X-TradingView-Secret` 并设置为您在`.env`文件中配置的`WEBHOOK_SECRET`值
5. 在「消息」字段中，使用 JSON 格式设置警报内容（参见下方示例）

### 7. 测试 Webhook

使用测试脚本模拟 TradingView 发送警报：

```bash
python test_webhook.py --type basic
```

可选的警报类型：

- `basic`：基本警报（默认）
- `message`：自定义消息警报
- `detailed`：详细策略警报

## TradingView 警报示例

### 基本警报

```json
{
  "ticker": "{{ticker}}",
  "strategy": "均线交叉策略",
  "price": {{close}},
  "action": "{{strategy.order.action}}"
}
```

### 自定义消息警报

```json
{
  "message": "🚨 {{ticker}} 触发警报！当前价格: {{close}}，动作: {{strategy.order.action}}"
}
```

### 详细策略警报

```json
{
  "ticker": "{{ticker}}",
  "strategy": "{{strategy.order.comment}}",
  "price": {{close}},
  "action": "{{strategy.order.action}}",
  "volume": {{strategy.order.contracts}},
  "time": "{{time}}",
  "notes": "自定义备注"
}
```

## 故障排除

### 无法接收 Telegram 消息

- 确保您的机器人令牌正确
- 确保您的机器人已被添加到目标群组
- 运行 `python test_bot.py` 检查 Telegram 配置

### TradingView 警报未触发

- 确保 webhook URL 正确
- 确保添加了正确的 `X-TradingView-Secret` 请求头
- 运行 `python test_webhook.py` 测试 webhook 功能
- 检查服务器日志

### 服务器无法访问

- 确保服务器正在运行
- 检查防火墙设置，确保端口已开放
- 如果使用云服务器，检查安全组设置

## 高级配置

### 自定义消息格式

您可以修改 `bot.py` 文件中的 `format_telegram_message` 函数来自定义 Telegram 消息的格式。

### 添加更多功能

您可以扩展 `bot.py` 文件，添加更多功能，例如：

- 支持更多的 TradingView 警报字段
- 添加图表或图像支持
- 集成其他交易平台的 API
- 添加用户认证和权限控制

## 部署到生产环境

对于生产环境，建议：

1. 使用 HTTPS 而不是 HTTP
2. 设置更复杂的密钥
3. 使用进程管理器（如 Supervisor 或 PM2）管理服务
4. 配置日志轮转
5. 设置监控和警报
