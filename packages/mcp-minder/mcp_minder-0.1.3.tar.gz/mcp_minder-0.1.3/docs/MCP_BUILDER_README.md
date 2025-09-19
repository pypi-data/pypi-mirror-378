# MCPBuilder - 基于函数的 MCP 服务器构建器

## 概述

MCPBuilder 是一个强大的工具，用于快速构建 MCP (Model Context Protocol) 服务器。它支持链式 API 调用，并且可以直接传入函数来自动解析函数签名、参数类型和代码内容。

## 主要特性

- 🚀 **链式 API**: 流畅的链式调用语法
- 🔧 **函数自动解析**: 直接传入函数，自动解析函数签名
- 📝 **模板生成**: 基于 `tianqi.py` 模板生成 MCP 服务器文件
- 🌐 **API 集成**: 支持通过 API 服务生成和部署服务器
- 🛠️ **多工具支持**: 支持添加多个工具到同一个服务器
- ⚡ **异步支持**: 支持异步和同步函数

## 快速开始

### 基本用法

```python
from minder import MCPBuilder

# 定义函数
async def query_tianqi(input: str) -> str:
    """
    天气查询工具,
    :param input: input input
    :return: output result
    """
    output = "天气是阴天"
    return output

# 使用 MCPBuilder 构建服务器
builder = (MCPBuilder()
           .for_mcp_server("天气查询")
           .add_tool(query_tianqi)  # 直接传入函数
           .set_up(
               api_url="http://localhost:8000/api/generate-mcp",
               author="开发者"
           ))

# 生成本地模板
template_content = builder.generate_template_content()
print(template_content)
```

### 多工具示例

```python
async def get_weather(city: str) -> str:
    """获取城市天气"""
    return f"{city}的天气是晴天"

async def calculate(expression: str) -> str:
    """计算数学表达式"""
    try:
        result = eval(expression)
        return str(result)
    except:
        return "计算错误"

# 添加多个工具
builder = (MCPBuilder()
           .for_mcp_server("多功能服务")
           .add_tool(get_weather)
           .add_tool(calculate)
           .from_market("http://localhost:8000")  # 设置镜像源
           .set_up("开发者"))  # 设置作者

# 保存模板到文件
builder.save_template("my_server.py")
```

## API 参考

### MCPBuilder 类

#### 方法

##### `for_mcp_server(server_name: str) -> MCPBuilder`
设定 MCP 服务器名称。

**参数:**
- `server_name`: 服务器名称

**返回:** 返回自身以支持链式调用

##### `add_tool(tool_or_func: Union[str, Callable], ...) -> MCPBuilder`
添加工具到 MCP 服务器。

**参数:**
- `tool_or_func`: 工具名称（字符串）或函数对象
- `param_name`: 参数名称（仅在传入字符串时使用）
- `param_type`: 参数类型（仅在传入字符串时使用）
- `return_type`: 返回类型（仅在传入字符串时使用）
- `description`: 工具描述（仅在传入字符串时使用）
- `code`: 工具实现代码（仅在传入字符串时使用）

**返回:** 返回自身以支持链式调用

##### `set_up(author: str = "开发者") -> MCPBuilder`
设置作者信息。

**参数:**
- `author`: 作者名称（可选，默认为"开发者"）

**返回:** 返回自身以支持链式调用

##### `from_market(url: str, token: Optional[str] = None) -> MCPBuilder`
设置镜像源市场配置。

**参数:**
- `url`: 镜像源API地址（只需要指定域名和端口，如 `http://localhost:8000`，系统会自动添加 `/api/generate-mcp` 路径）
- `token`: API访问令牌（可选）

**返回:** 返回自身以支持链式调用

**注意:** `url` 参数只需要指定到域名或端口号即可，不需要包含具体的 API 路径。系统会自动添加正确的路径。如果提供了 `token`，会在请求头中添加 `Authorization: Bearer {token}`。

##### `build() -> Dict[str, Any]`
构建 MCP 服务器配置数据。

**返回:** 包含所有配置的字典

##### `generate_template_content() -> str`
生成本地模板内容（不发送到 API）。

**返回:** 生成的 MCP 服务器模板内容

##### `save_template(output_path: str) -> bool`
保存模板到本地文件。

**参数:**
- `output_path`: 输出文件路径

**返回:** 是否保存成功

##### `async generate_and_deploy(output_path: Optional[str] = None) -> bool`
生成 MCP 服务器文件并部署到指定目录。

**参数:**
- `output_path`: 输出路径（可选）

**返回:** 是否成功生成和部署

### FunctionParser 类

#### 静态方法

##### `parse_function(func: Callable) -> Dict[str, Any]`
解析函数，提取函数信息。

**参数:**
- `func`: 要解析的函数

**返回:** 包含函数信息的字典

### Tool 类

#### 方法

##### `from_function(func: Callable) -> Tool`
从函数创建工具实例。

**参数:**
- `func`: 函数对象

**返回:** Tool 实例

## 支持的函数类型

### 异步函数
```python
async def my_async_tool(input: str) -> str:
    """异步工具"""
    return f"处理结果: {input}"
```

### 同步函数
```python
def my_sync_tool(input: str) -> str:
    """同步工具"""
    return f"处理结果: {input}"
```

### 带默认参数的函数
```python
def tool_with_default(name: str = "默认名称") -> str:
    """带默认参数的工具"""
    return f"你好, {name}!"
```

### 无参数函数
```python
def no_params_tool() -> str:
    """无参数工具"""
    return "执行成功"
```

## 生成的模板格式

生成的 MCP 服务器文件基于 `tianqi.py` 模板，包含以下结构：

```python
"""
MCP服务器模板 - 基于HTTP Stream的MCP服务器
作者: 开发者
服务名称: 天气查询
"""

import logging
import random
import sys
from fastmcp import FastMCP

mcp = FastMCP("天气查询")

logger = logging.getLogger(__name__)

# 确保 mcp 工具装饰器能正确处理异步函数
@mcp.tool()
async def query_tianqi(input: str) -> str:
    """
    天气查询工具,
    :param input: input input
    :return: output result
    """
    # 实现天气查询逻辑
    output = "天气是阴天"

    return output

if __name__ == "__main__":
    # 检查命令行参数中的端口
    port = None
    for i, arg in enumerate(sys.argv):
        if arg == "--port" and i + 1 < len(sys.argv):
            try:
                port = int(sys.argv[i + 1])
                break
            except ValueError:
                pass
    
    # 如果没有指定端口，使用随机端口
    if port is None:
        port = random.randint(10001, 18000)
    
    mcp.run(transport="streamable-http", host="0.0.0.0", port=port, path="/mcp", stateless_http=True)
```

## 示例文件

- `examples/function_based_usage.py`: 基于函数的详细使用示例
- `demo_function_based.py`: 快速演示脚本
- `tests/test_function_based_mcp_builder.py`: 测试文件

## API 接口

### 新增的 API 接口

#### 1. 生成 MCP 服务器文件（支持自动启动）
```
POST /api/generate-mcp
```

**请求体:**
```json
{
  "config": {
    "server_name": "天气查询服务",
    "tools": [
      {
        "name": "query_tianqi",
        "param_name": "input",
        "param_type": "str",
        "return_type": "str",
        "description": "天气查询工具",
        "code": "# 实现天气查询逻辑\n    output = \"天气是阴天\""
      }
    ],
    "author": "开发者",
    "port": 8080
  },
  "output_path": "server.py",  // 将保存在 mcpserver/天气查询服务/server.py
  "auto_start": true,
  "host": "0.0.0.0"
}
```

**响应:**
```json
{
  "success": true,
  "output_path": "/path/to/mcpserver/天气查询服务/server.py",
  "message": "MCP服务器文件生成成功: /path/to/mcpserver/天气查询服务/server.py，服务已启动在端口 8080，进程ID: 12345",
  "service_id": "uuid-string",
  "service_name": "天气查询服务",
  "port": 8080,
  "pid": 12345,
  "started": true
}
```

**自动启动功能说明:**
- `auto_start`: 是否自动启动服务（默认: true）
- `host`: 服务主机地址（默认: "0.0.0.0"）
- 如果 `auto_start` 为 true，系统会：
  1. 生成 MCP 服务器文件
  2. 注册服务到现有的服务管理器（复用现有逻辑）
  3. 自动启动服务（使用现有的启动逻辑）
  4. 返回服务ID、端口、进程ID等信息
- **集成优势**: 生成的服务会自动集成到现有的服务管理系统中，可以通过服务管理 API 进行统一管理

**文件路径结构:**
- 所有生成的 MCP 服务器文件都会保存在 `mcpserver/` 目录下
- 每个服务都有独立的子目录：`mcpserver/服务名/`
- 默认文件名为 `server.py`，完整路径为：`mcpserver/服务名/server.py`
- 如果指定了绝对路径，则按指定路径保存
- 如果只指定文件名，则保存在对应的服务目录下

#### 2. 预览 MCP 服务器代码
```
POST /api/preview-mcp
```

**请求体:** 与生成接口相同

**响应:**
```json
{
  "success": true,
  "content": "生成的完整代码内容...",
  "message": "MCP服务器代码预览生成成功"
}
```

### 传统 API 接口（仍然可用）

#### 生成单个工具的 MCP 服务器
```
POST /api/generate
```

**请求体:**
```json
{
  "output_path": "server.py",
  "service_name": "服务名",
  "tool_name": "工具名",
  "tool_param_name": "input",
  "tool_param_type": "str",
  "tool_return_type": "str",
  "tool_description": "工具描述",
  "tool_code": "代码",
  "author": "作者"
}
```

## 运行演示

```bash
# 运行演示脚本
python demo_function_based.py

# 运行详细示例
python examples/function_based_usage.py

# 运行 API 使用示例
python examples/api_usage_example.py

# 运行测试
python -m pytest tests/test_function_based_mcp_builder.py -v
```

## 注意事项

1. 函数必须包含类型注解才能正确解析参数类型
2. 函数文档字符串会被用作工具描述
3. 函数源代码会被提取并嵌入到生成的模板中
4. 支持异步和同步函数
5. 可以混合使用函数和手动定义的工具

## 错误处理

- 如果函数没有类型注解，会使用默认类型 `str`
- 如果无法获取函数源代码，会使用默认代码 `pass`
- 如果缺少必要配置（服务器名称、工具、API地址），会抛出 `ValueError`

## 许可证

MIT License
