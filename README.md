# TradingView 到 Telegram 转发机器人

这是一个简单的服务，用于接收 TradingView 的警报信息，并将其转发到指定的 Telegram 群组或用户。

## 功能特点

- 接收 TradingView 通过 webhook 发送的警报
- 支持 JSON 和纯文本格式的警报
- 将警报格式化并转发到 Telegram
- 使用密钥验证确保安全性
- 简单的健康检查 API

## 安装步骤

### 前提条件

- Python 3.7+
- 一个 Telegram 机器人令牌（从 BotFather 获取）
- 一个 Telegram 群组或用户 ID

### 安装

1. 克隆此仓库或下载代码

2. 安装依赖项

```bash
pip install -r requirements.txt
```

3. 复制环境变量示例文件并填写您的配置

```bash
cp .env.example .env
```

然后编辑`.env`文件，填写以下信息：

- `TELEGRAM_BOT_TOKEN`：您的 Telegram 机器人令牌
- `TELEGRAM_CHAT_ID`：目标 Telegram 群组或用户 ID
- `WEBHOOK_SECRET`：用于验证 TradingView 请求的密钥
- `HOST`和`PORT`：服务器主机和端口（默认为 0.0.0.0:8000）

## 使用方法

### 启动服务器

```bash
python bot.py
```

服务器将在指定的主机和端口上运行。

### 配置 TradingView 警报

1. 在 TradingView 中创建一个新的警报
2. 在「警报操作」部分选择「Webhook URL」
3. 输入您的 webhook URL，格式为：`http://your-server-address:8000/webhook?secret=YOUR_WEBHOOK_SECRET`
   - 将 `YOUR_WEBHOOK_SECRET` 替换为您在 `.env` 文件中配置的 `WEBHOOK_SECRET` 值
4. 在「消息」字段中，您可以使用以下格式之一：

#### JSON 格式（推荐）

```json
{
  "ticker": "{{ticker}}",
  "strategy": "均线交叉策略",
  "price": {{close}},
  "action": "{{strategy.order.action}}"
}
```

#### 自定义消息格式

```json
{
  "message": "🚨 {{ticker}} 触发警报！当前价格: {{close}}，动作: {{strategy.order.action}}"
}
```

#### 纯文本格式

如果您发送的不是有效的 JSON，系统将把整个消息作为文本处理并直接转发。

## 安全性考虑

- 使用URL参数中的`secret`验证请求，防止未经授权的访问
- 请勿在公开场合分享您的webhook URL和密钥
- 考虑在生产环境中使用 HTTPS
- 不要将`.env`文件提交到版本控制系统

## 故障排除

### 常见问题

1. **无法接收 Telegram 消息**

   - 确保您的机器人令牌正确
   - 确保您的机器人已被添加到目标群组
   - 检查日志中的错误信息

2. **TradingView 警报未触发**
   - 确保 webhook URL 正确，包含正确的密钥参数
   - URL 格式应为：`http://your-server:8000/webhook?secret=YOUR_SECRET`
   - 检查服务器日志

## 贡献

欢迎提交问题和拉取请求！

## 许可证

[MIT](LICENSE)
