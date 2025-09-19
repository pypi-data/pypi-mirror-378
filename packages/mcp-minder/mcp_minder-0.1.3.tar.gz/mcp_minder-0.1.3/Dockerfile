# 使用官方Python 3.12镜像作为基础镜像
FROM python:3.12-slim

# 设置工作目录
WORKDIR /app

# 安装uv
RUN pip install uv

# 复制必要的项目文件
COPY pyproject.toml README.md ./

# 使用uv创建虚拟环境并安装依赖
RUN uv sync

# 安装系统依赖和uv
RUN apt-get update && apt-get install -y procps

# 复制项目文件
COPY . /app/

# 安装项目本身
RUN uv pip install -e .

# 暴露端口
EXPOSE 8000 7860

# 设置默认命令
CMD ["sh", "-c", "uv run mcp-api-server --host 0.0.0.0 --port 8000 & uv run mcp-web --host 0.0.0.0 --port 7860 & wait"]