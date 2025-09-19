"""
MCPBuilder 测试模块

测试 MCPBuilder 类的各种功能
"""

import pytest
import tempfile
import os
from pathlib import Path
from minder import MCPBuilder, Tool


class TestMCPBuilder:
    """MCPBuilder 测试类"""
    
    def test_basic_chain_calls(self):
        """测试基本的链式调用"""
        builder = (MCPBuilder()
                   .for_mcp_server("测试服务")
                   .add_tool("test_tool", "input", "str", "str", "测试工具", "output = 'test'")
                   .set_up("http://localhost:8000/api", "测试作者"))
        
        assert builder._server_name == "测试服务"
        assert len(builder._tools) == 1
        assert builder._api_url == "http://localhost:8000/api"
        assert builder._author == "测试作者"
    
    def test_multiple_tools(self):
        """测试添加多个工具"""
        builder = (MCPBuilder()
                   .for_mcp_server("多工具服务")
                   .add_tool("tool1", "param1", "str", "str", "工具1", "output = 'tool1'")
                   .add_tool("tool2", "param2", "int", "str", "工具2", "output = 'tool2'")
                   .add_tool("tool3", "param3", "bool", "str", "工具3", "output = 'tool3'")
                   .set_up("http://localhost:8000/api"))
        
        assert len(builder._tools) == 3
        assert builder._tools[0].name == "tool1"
        assert builder._tools[1].name == "tool2"
        assert builder._tools[2].name == "tool3"
    
    def test_build_config(self):
        """测试构建配置"""
        builder = (MCPBuilder()
                   .for_mcp_server("配置测试")
                   .add_tool("test_tool", "input", "str", "str", "测试工具", "output = 'test'")
                   .set_up("http://localhost:8000/api", "测试作者", 8080))
        
        config = builder.build()
        
        assert config["server_name"] == "配置测试"
        assert config["api_url"] == "http://localhost:8000/api"
        assert config["author"] == "测试作者"
        assert config["port"] == 8080
        assert len(config["tools"]) == 1
        assert config["tools"][0]["name"] == "test_tool"
    
    def test_validation_errors(self):
        """测试验证错误"""
        # 测试缺少服务器名称
        builder1 = MCPBuilder().add_tool("test_tool").set_up("http://localhost:8000/api")
        with pytest.raises(ValueError, match="必须设置服务器名称"):
            builder1.build()
        
        # 测试缺少工具
        builder2 = MCPBuilder().for_mcp_server("测试服务").set_up("http://localhost:8000/api")
        with pytest.raises(ValueError, match="必须至少添加一个工具"):
            builder2.build()
        
        # 测试缺少API地址
        builder3 = MCPBuilder().for_mcp_server("测试服务").add_tool("test_tool")
        with pytest.raises(ValueError, match="必须设置API服务地址"):
            builder3.build()
    
    def test_generate_template_content(self):
        """测试生成模板内容"""
        builder = (MCPBuilder()
                   .for_mcp_server("模板测试")
                   .add_tool("test_tool", "input", "str", "str", "测试工具", "output = 'test'")
                   .set_up("http://localhost:8000/api", "测试作者", 8080))
        
        content = builder.generate_template_content()
        
        assert "MCP服务器模板" in content
        assert "模板测试" in content
        assert "测试作者" in content
        assert "async def test_tool" in content
        assert "8080" in content
    
    def test_save_template(self):
        """测试保存模板到文件"""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = os.path.join(temp_dir, "test_server.py")
            
            builder = (MCPBuilder()
                       .for_mcp_server("保存测试")
                       .add_tool("test_tool", "input", "str", "str", "测试工具", "output = 'test'")
                       .set_up("http://localhost:8000/api"))
            
            success = builder.save_template(output_path)
            
            assert success is True
            assert os.path.exists(output_path)
            
            # 验证文件内容
            with open(output_path, 'r', encoding='utf-8') as f:
                content = f.read()
                assert "保存测试" in content
                assert "async def test_tool" in content


class TestTool:
    """Tool 类测试"""
    
    def test_tool_creation(self):
        """测试工具创建"""
        tool = Tool("test_tool", "input", "str", "str", "测试工具", "output = 'test'")
        
        assert tool.name == "test_tool"
        assert tool.param_name == "input"
        assert tool.param_type == "str"
        assert tool.return_type == "str"
        assert tool.description == "测试工具"
        assert tool.code == "output = 'test'"
    
    def test_tool_to_dict(self):
        """测试工具转换为字典"""
        tool = Tool("test_tool", "input", "str", "str", "测试工具", "output = 'test'")
        tool_dict = tool.to_dict()
        
        expected = {
            "name": "test_tool",
            "param_name": "input",
            "param_type": "str",
            "return_type": "str",
            "description": "测试工具",
            "code": "output = 'test'"
        }
        
        assert tool_dict == expected


if __name__ == "__main__":
    pytest.main([__file__])
