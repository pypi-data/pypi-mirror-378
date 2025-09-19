# Docker 部署指南

本文档介绍如何使用 Docker 和 Docker Compose 部署 MCP Minder。

## 快速开始

### 开发环境

```bash
# 启动开发环境
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

### 生产环境

```bash
# 启动生产环境
docker-compose -f docker-compose.prod.yml up -d

# 查看日志
docker-compose -f docker-compose.prod.yml logs -f

# 停止服务
docker-compose -f docker-compose.prod.yml down
```

## 服务说明

### 开发环境服务

- **mcp-minder**: 统一服务 (同时包含API和Web)
  - API服务器 (端口 8000)
  - Web界面 (端口 7860)

## 环境变量

### 通用环境变量

- `PYTHONPATH`: Python路径
- `PYTHONUNBUFFERED`: 禁用Python输出缓冲

### 服务特定环境变量

可以通过环境变量文件或docker-compose.yml中的environment部分设置：

```yaml
environment:
  - MCP_MINDER_LOG_LEVEL=INFO
  - MCP_MINDER_MAX_WORKERS=4
```

## 数据持久化

### 卷挂载

- `./service_logs:/app/service_logs`: 服务日志
- `./mcpserver:/app/mcpserver`: MCP服务器文件
- `./services.json:/app/services.json`: 服务配置

### 生产环境卷

- `service_logs`: 服务日志卷
- `mcpserver_data`: MCP服务器数据卷

## 健康检查

所有服务都配置了健康检查：

- **API服务器**: `GET /health`
- **Web界面**: `GET /`
- **检查间隔**: 30秒
- **超时时间**: 10秒
- **重试次数**: 3次

## 网络配置

### 开发环境

服务直接暴露端口到主机。

### 生产环境

服务直接暴露端口到主机，可以通过不同端口访问不同服务。

## 构建自定义镜像

### 构建镜像

```bash
docker build -t mcp-minder:latest .
```

## 常用命令

### 查看服务状态

```bash
docker-compose ps
```

### 查看服务日志

```bash
# 查看所有服务日志
docker-compose logs

# 查看特定服务日志
docker-compose logs mcp-minder-api

# 实时查看日志
docker-compose logs -f mcp-minder-api
```

### 进入容器

```bash
# 进入API容器
docker-compose exec mcp-minder-api bash

# 进入Web容器
docker-compose exec mcp-minder-web bash
```

### 重启服务

```bash
# 重启所有服务
docker-compose restart

# 重启特定服务
docker-compose restart mcp-minder-api
```

### 更新服务

```bash
# 重新构建并启动
docker-compose up -d --build

# 强制重新创建容器
docker-compose up -d --force-recreate
```

## 故障排除

### 端口冲突

如果遇到端口冲突，可以修改docker-compose.yml中的端口映射：

```yaml
ports:
  - "8001:8000"  # 将主机端口改为8001
```

### 权限问题

确保挂载的目录有正确的权限：

```bash
sudo chown -R $USER:$USER ./service_logs ./mcpserver
```

### 内存不足

如果遇到内存不足，可以限制容器内存使用：

```yaml
deploy:
  resources:
    limits:
      memory: 512M
```

## 监控和日志

### 日志管理

日志文件存储在 `./service_logs` 目录中，可以通过以下方式查看：

```bash
# 查看容器日志
docker-compose logs mcp-minder-api

# 查看应用日志文件
tail -f ./service_logs/*.log
```

### 性能监控

可以使用Docker stats监控资源使用：

```bash
docker stats
```

## 安全考虑

### 生产环境

1. 使用非root用户运行容器
2. 限制容器资源使用
3. 使用HTTPS (配置SSL证书)
4. 定期更新基础镜像
5. 使用secrets管理敏感信息

### 网络安全

1. 配置防火墙规则
2. 使用HTTPS (配置SSL证书)
3. 启用访问日志和监控
4. 限制容器资源使用
