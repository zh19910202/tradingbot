# 使用官方 Python 运行时作为基础镜像
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 复制 requirements.txt
COPY requirements.txt .

# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 暴露端口（Cloud Run 会自动设置 PORT 环境变量）
EXPOSE 8080

# 运行应用
CMD ["uvicorn", "bot:app", "--host", "0.0.0.0", "--port", "8080"]