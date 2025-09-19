"""
基于函数的 MCPBuilder 测试模块

测试 MCPBuilder 类的函数解析和自动工具创建功能
"""

import pytest
import tempfile
import os
from minder import MCPBuilder, Tool, FunctionParser


# 定义测试函数
async def test_weather_function(city: str) -> str:
    """
    测试天气查询函数
    
    Args:
        city: 城市名称
        
    Returns:
        天气信息
    """
    output = f"{city}的天气是晴天"
    return output


def test_calculate_function(expression: str) -> str:
    """
    计算数学表达式
    
    Args:
        expression: 数学表达式
        
    Returns:
        计算结果
    """
    try:
        result = eval(expression)
        output = str(result)
    except:
        output = "计算错误"
    return output


async def test_no_params_function() -> str:
    """无参数函数"""
    output = "无参数函数执行成功"
    return output


def test_default_param_function(name: str = "默认名称") -> str:
    """带默认参数的函数"""
    output = f"你好, {name}!"
    return output


class TestFunctionParser:
    """FunctionParser 测试类"""
    
    def test_parse_async_function(self):
        """测试解析异步函数"""
        func_info = FunctionParser.parse_function(test_weather_function)
        
        assert func_info["name"] == "test_weather_function"
        assert len(func_info["params"]) == 1
        assert func_info["params"][0]["name"] == "city"
        assert func_info["params"][0]["type"] == "str"
        assert func_info["return_type"] == "str"
        assert "测试天气查询函数" in func_info["description"]
        assert "output = f\"{city}的天气是晴天\"" in func_info["code"]
    
    def test_parse_sync_function(self):
        """测试解析同步函数"""
        func_info = FunctionParser.parse_function(test_calculate_function)
        
        assert func_info["name"] == "test_calculate_function"
        assert len(func_info["params"]) == 1
        assert func_info["params"][0]["name"] == "expression"
        assert func_info["params"][0]["type"] == "str"
        assert func_info["return_type"] == "str"
        assert "计算数学表达式" in func_info["description"]
    
    def test_parse_no_params_function(self):
        """测试解析无参数函数"""
        func_info = FunctionParser.parse_function(test_no_params_function)
        
        assert func_info["name"] == "test_no_params_function"
        assert len(func_info["params"]) == 0
        assert func_info["return_type"] == "str"
        assert "无参数函数执行成功" in func_info["code"]
    
    def test_parse_default_param_function(self):
        """测试解析带默认参数的函数"""
        func_info = FunctionParser.parse_function(test_default_param_function)
        
        assert func_info["name"] == "test_default_param_function"
        assert len(func_info["params"]) == 1
        assert func_info["params"][0]["name"] == "name"
        assert func_info["params"][0]["type"] == "str"
        assert func_info["params"][0]["default"] == "默认名称"
        assert func_info["return_type"] == "str"


class TestToolFromFunction:
    """从函数创建工具的测试类"""
    
    def test_tool_from_async_function(self):
        """测试从异步函数创建工具"""
        tool = Tool.from_function(test_weather_function)
        
        assert tool.name == "test_weather_function"
        assert tool.param_name == "city"
        assert tool.param_type == "str"
        assert tool.return_type == "str"
        assert "测试天气查询函数" in tool.description
        assert "output = f\"{city}的天气是晴天\"" in tool.code
    
    def test_tool_from_sync_function(self):
        """测试从同步函数创建工具"""
        tool = Tool.from_function(test_calculate_function)
        
        assert tool.name == "test_calculate_function"
        assert tool.param_name == "expression"
        assert tool.param_type == "str"
        assert tool.return_type == "str"
        assert "计算数学表达式" in tool.description
    
    def test_tool_from_no_params_function(self):
        """测试从无参数函数创建工具"""
        tool = Tool.from_function(test_no_params_function)
        
        assert tool.name == "test_no_params_function"
        assert tool.param_name == "input"  # 默认参数名
        assert tool.param_type == "str"    # 默认参数类型
        assert tool.return_type == "str"
    
    def test_tool_from_default_param_function(self):
        """测试从带默认参数的函数创建工具"""
        tool = Tool.from_function(test_default_param_function)
        
        assert tool.name == "test_default_param_function"
        assert tool.param_name == "name"
        assert tool.param_type == "str"
        assert tool.return_type == "str"


class TestMCPBuilderWithFunctions:
    """使用函数的 MCPBuilder 测试类"""
    
    def test_add_function_tool(self):
        """测试添加函数工具"""
        builder = (MCPBuilder()
                   .for_mcp_server("函数测试服务")
                   .add_tool(test_weather_function)  # 直接传入函数
                   .set_up("http://localhost:8000/api"))
        
        assert len(builder._tools) == 1
        tool = builder._tools[0]
        assert tool.name == "test_weather_function"
        assert tool.param_name == "city"
        assert tool.param_type == "str"
    
    def test_add_multiple_function_tools(self):
        """测试添加多个函数工具"""
        builder = (MCPBuilder()
                   .for_mcp_server("多函数服务")
                   .add_tool(test_weather_function)
                   .add_tool(test_calculate_function)
                   .add_tool(test_no_params_function)
                   .set_up("http://localhost:8000/api"))
        
        assert len(builder._tools) == 3
        assert builder._tools[0].name == "test_weather_function"
        assert builder._tools[1].name == "test_calculate_function"
        assert builder._tools[2].name == "test_no_params_function"
    
    def test_mixed_tool_adding(self):
        """测试混合添加工具（函数 + 手动定义）"""
        builder = (MCPBuilder()
                   .for_mcp_server("混合服务")
                   .add_tool(test_weather_function)  # 函数
                   .add_tool(                        # 手动定义
                       "manual_tool",
                       "data",
                       "str",
                       "str",
                       "手动工具",
                       "output = 'manual'"
                   )
                   .set_up("http://localhost:8000/api"))
        
        assert len(builder._tools) == 2
        assert builder._tools[0].name == "test_weather_function"
        assert builder._tools[1].name == "manual_tool"
    
    def test_build_with_functions(self):
        """测试使用函数构建配置"""
        builder = (MCPBuilder()
                   .for_mcp_server("构建测试")
                   .add_tool(test_weather_function)
                   .add_tool(test_calculate_function)
                   .from_market("http://localhost:8000")
                   .set_up("函数开发者"))
        
        config = builder.build()
        
        assert config["server_name"] == "构建测试"
        assert config["author"] == "函数开发者"
        assert len(config["tools"]) == 2
        
        # 检查第一个工具（从函数创建）
        tool1 = config["tools"][0]
        assert tool1["name"] == "test_weather_function"
        assert tool1["param_name"] == "city"
        assert tool1["param_type"] == "str"
        assert tool1["return_type"] == "str"
        
        # 检查第二个工具（从函数创建）
        tool2 = config["tools"][1]
        assert tool2["name"] == "test_calculate_function"
        assert tool2["param_name"] == "expression"
        assert tool2["param_type"] == "str"
        assert tool2["return_type"] == "str"
    
    def test_generate_template_with_functions(self):
        """测试使用函数生成模板"""
        builder = (MCPBuilder()
                   .for_mcp_server("模板测试")
                   .add_tool(test_weather_function)
                   .from_market("http://localhost:8000")
                   .set_up("模板开发者"))
        
        content = builder.generate_template_content()
        
        assert "模板测试" in content
        assert "模板开发者" in content
        assert "async def test_weather_function" in content
        assert "city: str" in content
        assert "output = f\"{city}的天气是晴天\"" in content
    
    def test_save_template_with_functions(self):
        """测试保存包含函数的模板"""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = os.path.join(temp_dir, "function_server.py")
            
            builder = (MCPBuilder()
                       .for_mcp_server("保存测试")
                       .add_tool(test_weather_function)
                       .set_up("http://localhost:8000/api"))
            
            success = builder.save_template(output_path)
            
            assert success is True
            assert os.path.exists(output_path)
            
            # 验证文件内容
            with open(output_path, 'r', encoding='utf-8') as f:
                content = f.read()
                assert "保存测试" in content
                assert "async def test_weather_function" in content
                assert "city: str" in content


if __name__ == "__main__":
    pytest.main([__file__])
