"""
基于函数的 MCPBuilder 使用示例

展示如何直接传入函数来构建 MCP 服务器模板
"""

import asyncio
from minder import MCPBuilder


# 定义一些示例函数
async def query_tianqi(input: str) -> str:
    """
    天气查询工具,
    :param input: input input
    :return: output result
    """
    # 实现天气查询逻辑
    output = "天气是阴天"
    return output


async def get_weather(city: str) -> str:
    """
    获取城市天气信息
    
    Args:
        city: 城市名称
        
    Returns:
        天气信息字符串
    """
    # 模拟天气查询
    weather_data = {
        "北京": "晴天，温度25°C",
        "上海": "多云，温度22°C", 
        "广州": "小雨，温度28°C"
    }
    output = weather_data.get(city, f"{city}的天气信息暂不可用")
    return output


async def calculate(expression: str) -> str:
    """
    计算数学表达式
    
    Args:
        expression: 数学表达式字符串
        
    Returns:
        计算结果
    """
    try:
        # 安全的数学表达式计算
        allowed_chars = set('0123456789+-*/().')
        if all(c in allowed_chars or c.isspace() for c in expression):
            result = eval(expression)
            output = str(result)
        else:
            output = "表达式包含非法字符"
    except Exception as e:
        output = f"计算错误: {str(e)}"
    
    return output


async def get_time(timezone: str = "Asia/Shanghai") -> str:
    """
    获取指定时区的时间
    
    Args:
        timezone: 时区名称，默认为上海时区
        
    Returns:
        格式化的时间字符串
    """
    import datetime
    now = datetime.datetime.now()
    output = now.strftime(f'%Y-%m-%d %H:%M:%S ({timezone})')
    return output


def example_function_based_usage():
    """基于函数的使用示例"""
    print("=== 基于函数的使用示例 ===")
    
    # 直接传入函数，自动解析函数信息
    builder = (MCPBuilder()
               .for_mcp_server("天气查询服务")
               .add_tool(query_tianqi)  # 直接传入函数
               .from_market("http://localhost:8000")  # 设置镜像源
               .set_up("函数开发者"))  # 设置作者
    
    # 生成本地模板内容
    template_content = builder.generate_template_content()
    print("生成的模板内容:")
    print(template_content)
    print("\n" + "="*50 + "\n")


def example_multiple_functions():
    """多函数示例"""
    print("=== 多函数示例 ===")
    
    builder = (MCPBuilder()
               .for_mcp_server("多功能服务")
               .add_tool(get_weather)      # 天气查询函数
               .add_tool(calculate)        # 计算函数
               .add_tool(get_time)         # 时间查询函数
               .from_market("http://localhost:8000")  # 设置镜像源
               .set_up("多功能开发者"))  # 设置作者
    
    # 保存模板到本地文件
    success = builder.save_template("examples/generated_function_based_server.py")
    if success:
        print("基于函数的服务器模板已保存到 examples/generated_function_based_server.py")
    
    # 显示构建的配置信息
    config = builder.build()
    print("\n构建的配置信息:")
    print(f"服务器名称: {config['server_name']}")
    print(f"工具数量: {len(config['tools'])}")
    for i, tool in enumerate(config['tools'], 1):
        print(f"  工具{i}: {tool['name']} - {tool['description']}")
    print("\n" + "="*50 + "\n")


def example_mixed_usage():
    """混合使用示例（函数 + 手动定义）"""
    print("=== 混合使用示例 ===")
    
    builder = (MCPBuilder()
               .for_mcp_server("混合服务")
               .add_tool(get_weather)  # 使用函数
               .add_tool(              # 手动定义工具
                   "custom_tool",
                   "data",
                   "str", 
                   "str",
                   "自定义工具",
                   "# 自定义逻辑\n    output = f'处理数据: {data}'"
               )
               .from_market("http://localhost:8000")  # 设置镜像源
               .set_up("混合开发者"))  # 设置作者
    
    # 显示所有工具信息
    print("混合服务包含的工具:")
    for i, tool in enumerate(builder._tools, 1):
        print(f"  工具{i}: {tool.name}")
        print(f"    参数: {tool.param_name} ({tool.param_type})")
        print(f"    返回: {tool.return_type}")
        print(f"    描述: {tool.description}")
        print()
    print("="*50 + "\n")


async def example_api_deployment_with_functions():
    """使用函数进行API部署示例"""
    print("=== 使用函数进行API部署示例 ===")
    
    builder = (MCPBuilder()
               .for_mcp_server("函数API服务")
               .add_tool(calculate)
               .add_tool(get_time)
               .from_market("http://localhost:8000")  # 设置镜像源
               .set_up("函数API测试者"))  # 设置作者
    
    # 尝试通过API生成和部署
    success = await builder.generate_and_deploy("function_api_server.py")
    if success:
        print("通过API成功生成和部署了基于函数的服务器")
    else:
        print("API部署失败，可能是API服务未启动")
    print("\n" + "="*50 + "\n")


def example_function_parsing():
    """函数解析示例"""
    print("=== 函数解析示例 ===")
    
    from minder import FunctionParser
    
    # 解析单个函数
    func_info = FunctionParser.parse_function(query_tianqi)
    print("query_tianqi 函数解析结果:")
    print(f"  函数名: {func_info['name']}")
    print(f"  参数: {func_info['params']}")
    print(f"  返回类型: {func_info['return_type']}")
    print(f"  描述: {func_info['description']}")
    print(f"  代码: {func_info['code'][:100]}...")
    print()
    
    # 解析带默认参数的函数
    func_info2 = FunctionParser.parse_function(get_time)
    print("get_time 函数解析结果:")
    print(f"  函数名: {func_info2['name']}")
    print(f"  参数: {func_info2['params']}")
    print(f"  返回类型: {func_info2['return_type']}")
    print()
    
    print("="*50 + "\n")


def main():
    """主函数"""
    print("基于函数的 MCPBuilder 使用示例\n")
    
    # 运行各种示例
    example_function_based_usage()
    example_multiple_functions()
    example_mixed_usage()
    example_function_parsing()
    
    # 运行异步示例
    print("运行异步API部署示例...")
    asyncio.run(example_api_deployment_with_functions())
    
    print("所有示例运行完成！")


if __name__ == "__main__":
    main()
