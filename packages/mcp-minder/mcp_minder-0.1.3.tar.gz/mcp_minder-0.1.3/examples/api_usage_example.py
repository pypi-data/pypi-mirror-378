"""
API 使用示例

展示如何通过 HTTP API 调用 MCPBuilder 接口
"""

import asyncio
import httpx
import json


async def test_generate_mcp_api():
    """测试生成 MCP 服务器 API"""
    print("=== 测试生成 MCP 服务器 API ===")
    
    # API 请求数据
    request_data = {
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
                },
                {
                    "name": "get_weather",
                    "param_name": "city",
                    "param_type": "str",
                    "return_type": "str",
                    "description": "获取城市天气",
                    "code": "# 获取天气信息\n    output = f\"{city}的天气是晴天\""
                }
            ],
            "author": "API测试者",
            "port": 8080
        },
        "output_path": "server.py",  # 将保存在 mcpserver/天气查询服务/server.py
        "auto_start": True,  # 启用自动启动
        "host": "0.0.0.0"
    }
    
    try:
        async with httpx.AsyncClient() as client:
            # 发送生成请求
            response = await client.post(
                "http://localhost:8000/api/generate-mcp",
                json=request_data,
                headers={"Content-Type": "application/json"},
                timeout=30.0
            )
            
            if response.status_code == 200:
                result = response.json()
                print("✅ 生成成功!")
                print(f"   输出路径: {result.get('output_path')}")
                print(f"   服务名称: {result.get('service_name')}")
                print(f"   服务ID: {result.get('service_id')}")
                print(f"   端口: {result.get('port')}")
                print(f"   进程ID: {result.get('pid')}")
                print(f"   已启动: {result.get('started')}")
                print(f"   消息: {result.get('message')}")
            else:
                print(f"❌ 生成失败: {response.status_code}")
                print(f"   错误: {response.text}")
                
    except Exception as e:
        print(f"❌ 请求失败: {e}")


async def test_preview_mcp_api():
    """测试预览 MCP 服务器 API"""
    print("\n=== 测试预览 MCP 服务器 API ===")
    
    # API 请求数据
    request_data = {
        "config": {
            "server_name": "多功能服务",
            "tools": [
                {
                    "name": "calculate",
                    "param_name": "expression",
                    "param_type": "str",
                    "return_type": "str",
                    "description": "计算数学表达式",
                    "code": "# 计算表达式\n    try:\n        result = eval(expression)\n        output = str(result)\n    except:\n        output = \"计算错误\""
                }
            ],
            "author": "预览测试者"
        },
        "output_path": "preview_server.py"
    }
    
    try:
        async with httpx.AsyncClient() as client:
            # 发送预览请求
            response = await client.post(
                "http://localhost:8000/api/preview-mcp",
                json=request_data,
                headers={"Content-Type": "application/json"},
                timeout=30.0
            )
            
            if response.status_code == 200:
                result = response.json()
                print("✅ 预览成功!")
                print(f"   消息: {result.get('message')}")
                
                # 显示生成的代码预览
                content = result.get('content', '')
                if content:
                    print("\n📝 生成的代码预览:")
                    print("```python")
                    lines = content.split('\n')
                    for line in lines[:15]:  # 只显示前15行
                        print(line)
                    if len(lines) > 15:
                        print("...")
                    print("```")
            else:
                print(f"❌ 预览失败: {response.status_code}")
                print(f"   错误: {response.text}")
                
    except Exception as e:
        print(f"❌ 请求失败: {e}")


async def test_legacy_generate_api():
    """测试传统的生成 API（对比）"""
    print("\n=== 测试传统生成 API ===")
    
    # 传统 API 请求数据
    request_data = {
        "output_path": "legacy_generated_server.py",
        "service_name": "传统服务",
        "tool_name": "legacy_tool",
        "tool_param_name": "input",
        "tool_param_type": "str",
        "tool_return_type": "str",
        "tool_description": "传统工具",
        "tool_code": "# 传统工具实现\n    output = \"传统处理完成\"",
        "author": "传统开发者"
    }
    
    try:
        async with httpx.AsyncClient() as client:
            # 发送传统生成请求
            response = await client.post(
                "http://localhost:8000/api/generate",
                json=request_data,
                headers={"Content-Type": "application/json"},
                timeout=30.0
            )
            
            if response.status_code == 200:
                result = response.json()
                print("✅ 传统生成成功!")
                print(f"   输出路径: {result.get('output_path')}")
                print(f"   消息: {result.get('message')}")
            else:
                print(f"❌ 传统生成失败: {response.status_code}")
                print(f"   错误: {response.text}")
                
    except Exception as e:
        print(f"❌ 请求失败: {e}")


def show_api_comparison():
    """显示 API 对比"""
    print("\n=== API 接口对比 ===")
    print("\n📊 传统 API vs MCPBuilder API")
    print("\n传统 API:")
    print("  POST /api/generate")
    print("  - 单个工具")
    print("  - 简单参数")
    print("  - 基础功能")
    
    print("\nMCPBuilder API:")
    print("  POST /api/generate-mcp")
    print("  POST /api/preview-mcp")
    print("  - 多个工具")
    print("  - 结构化配置")
    print("  - 高级功能")
    print("  - 支持预览")
    
    print("\n📝 请求格式对比:")
    print("\n传统 API 请求:")
    print("""
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
    """)
    
    print("MCPBuilder API 请求:")
    print("""
{
  "config": {
    "server_name": "服务名",
    "tools": [
      {
        "name": "工具1",
        "param_name": "input",
        "param_type": "str",
        "return_type": "str",
        "description": "工具描述",
        "code": "代码"
      }
    ],
    "author": "作者",
    "port": 8080
  },
  "output_path": "server.py"
}
    """)


async def main():
    """主函数"""
    print("🚀 MCPBuilder API 使用示例")
    print("=" * 50)
    
    # 显示 API 对比
    show_api_comparison()
    
    # 测试各种 API
    await test_generate_mcp_api()
    await test_preview_mcp_api()
    await test_legacy_generate_api()
    
    print("\n🎉 API 测试完成!")
    print("\n💡 使用提示:")
    print("  1. 确保 API 服务器正在运行 (http://localhost:8000)")
    print("  2. MCPBuilder API 支持多工具和预览功能")
    print("  3. 传统 API 仍然可用，用于简单场景")
    print("  4. 可以通过 HTTP 客户端或 curl 调用这些接口")


if __name__ == "__main__":
    asyncio.run(main())
