"""
MCPBuilder 使用示例

展示如何使用 MCPBuilder 类来构建 MCP 服务器模板
"""

import asyncio
from minder import MCPBuilder


def example_basic_usage():
    """基本使用示例"""
    print("=== 基本使用示例 ===")
    
    # 创建构建器并链式调用
    builder = (MCPBuilder()
               .for_mcp_server("天气查询")
               .add_tool(
                   name="query_tianqi",
                   param_name="input",
                   param_type="str",
                   return_type="str",
                   description="天气查询工具",
                   code="# 实现天气查询逻辑\n    output = \"天气是阴天\""
               )
               .set_up(
                   api_url="http://localhost:8000/api/generate-mcp",
                   author="开发者",
                   port=8080
               ))
    
    # 生成本地模板内容
    template_content = builder.generate_template_content()
    print("生成的模板内容:")
    print(template_content)
    print("\n" + "="*50 + "\n")


def example_multiple_tools():
    """多工具示例"""
    print("=== 多工具示例 ===")
    
    builder = (MCPBuilder()
               .for_mcp_server("多功能服务")
               .add_tool(
                   name="get_weather",
                   param_name="city",
                   param_type="str",
                   return_type="str",
                   description="获取城市天气",
                   code="# 获取天气信息\n    output = f\"{city}的天气是晴天\""
               )
               .add_tool(
                   name="get_time",
                   param_name="timezone",
                   param_type="str",
                   return_type="str",
                   description="获取指定时区时间",
                   code="# 获取时间信息\n    import datetime\n    output = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')"
               )
               .add_tool(
                   name="calculate",
                   param_name="expression",
                   param_type="str",
                   return_type="str",
                   description="计算数学表达式",
                   code="# 计算表达式\n    try:\n        result = eval(expression)\n        output = str(result)\n    except:\n        output = \"计算错误\""
               )
               .set_up(
                   api_url="http://localhost:8000/api/generate-mcp",
                   author="多功能开发者"
               ))
    
    # 保存模板到本地文件
    success = builder.save_template("examples/generated_multi_tool_server.py")
    if success:
        print("多工具服务器模板已保存到 examples/generated_multi_tool_server.py")
    print("\n" + "="*50 + "\n")


async def example_api_deployment():
    """API部署示例"""
    print("=== API部署示例 ===")
    
    builder = (MCPBuilder()
               .for_mcp_server("API部署测试")
               .add_tool(
                   name="test_api",
                   param_name="data",
                   param_type="str",
                   return_type="str",
                   description="测试API功能",
                   code="# 测试API功能\n    output = f\"处理数据: {data}\""
               )
               .set_up(
                   api_url="http://localhost:8000/api/generate-mcp",
                   author="API测试者"
               ))
    
    # 尝试通过API生成和部署
    success = await builder.generate_and_deploy("api_test_server.py")
    if success:
        print("通过API成功生成和部署了服务器")
    else:
        print("API部署失败，可能是API服务未启动")
    print("\n" + "="*50 + "\n")


def example_validation():
    """验证示例"""
    print("=== 验证示例 ===")
    
    # 测试缺少服务器名称的情况
    try:
        builder = MCPBuilder().add_tool("test_tool").set_up("http://localhost:8000/api/generate-mcp")
        builder.build()
    except ValueError as e:
        print(f"预期的错误: {e}")
    
    # 测试缺少工具的情况
    try:
        builder = MCPBuilder().for_mcp_server("测试服务").set_up("http://localhost:8000/api/generate-mcp")
        builder.build()
    except ValueError as e:
        print(f"预期的错误: {e}")
    
    # 测试缺少API地址的情况
    try:
        builder = MCPBuilder().for_mcp_server("测试服务").add_tool("test_tool")
        builder.build()
    except ValueError as e:
        print(f"预期的错误: {e}")
    
    print("\n" + "="*50 + "\n")


def main():
    """主函数"""
    print("MCPBuilder 使用示例\n")
    
    # 运行各种示例
    example_basic_usage()
    example_multiple_tools()
    example_validation()
    
    # 运行异步示例
    print("运行异步API部署示例...")
    asyncio.run(example_api_deployment())
    
    print("所有示例运行完成！")


if __name__ == "__main__":
    main()
