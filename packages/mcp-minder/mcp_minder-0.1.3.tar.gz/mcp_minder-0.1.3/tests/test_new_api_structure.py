"""
新的 API 结构测试

测试 MCPBuilder 的新 API 结构：set_up 只设置作者，from_market 设置镜像源
"""

import pytest
from minder import MCPBuilder


class TestNewAPIStructure:
    """新的 API 结构测试类"""
    
    def test_set_up_author_only(self):
        """测试 set_up 只设置作者"""
        builder = (MCPBuilder()
                   .for_mcp_server("测试服务")
                   .add_tool("test_tool", "input", "str", "str", "测试工具", "output = 'test'")
                   .set_up("测试作者"))
        
        assert builder._author == "测试作者"
        assert builder._api_url is None
        assert builder._api_token is None
    
    def test_set_up_default_author(self):
        """测试 set_up 使用默认作者"""
        builder = (MCPBuilder()
                   .for_mcp_server("测试服务")
                   .add_tool("test_tool", "input", "str", "str", "测试工具", "output = 'test'")
                   .set_up())
        
        assert builder._author == "开发者"
        assert builder._api_url is None
        assert builder._api_token is None
    
    def test_from_market_url_only(self):
        """测试 from_market 只设置 URL"""
        builder = (MCPBuilder()
                   .for_mcp_server("测试服务")
                   .add_tool("test_tool", "input", "str", "str", "测试工具", "output = 'test'")
                   .from_market("http://localhost:8000"))
        
        assert builder._api_url == "http://localhost:8000"
        assert builder._api_token is None
    
    def test_from_market_with_token(self):
        """测试 from_market 设置 URL 和 token"""
        builder = (MCPBuilder()
                   .for_mcp_server("测试服务")
                   .add_tool("test_tool", "input", "str", "str", "测试工具", "output = 'test'")
                   .from_market("http://localhost:8000", "test-token-123"))
        
        assert builder._api_url == "http://localhost:8000"
        assert builder._api_token == "test-token-123"
    
    def test_chain_calls_new_structure(self):
        """测试新的链式调用结构"""
        builder = (MCPBuilder()
                   .for_mcp_server("链式测试服务")
                   .add_tool("test_tool", "input", "str", "str", "测试工具", "output = 'test'")
                   .from_market("http://api.example.com:9000", "secret-token")
                   .set_up("链式作者"))
        
        assert builder._server_name == "链式测试服务"
        assert len(builder._tools) == 1
        assert builder._api_url == "http://api.example.com:9000"
        assert builder._api_token == "secret-token"
        assert builder._author == "链式作者"
    
    def test_build_with_new_structure(self):
        """测试使用新结构构建配置"""
        builder = (MCPBuilder()
                   .for_mcp_server("构建测试服务")
                   .add_tool("test_tool", "input", "str", "str", "测试工具", "output = 'test'")
                   .from_market("http://localhost:8000", "build-token")
                   .set_up("构建作者"))
        
        config = builder.build()
        
        assert config["server_name"] == "构建测试服务"
        assert config["api_url"] == "http://localhost:8000"
        assert config["api_token"] == "build-token"
        assert config["author"] == "构建作者"
        assert len(config["tools"]) == 1
    
    def test_validation_with_new_structure(self):
        """测试新结构的验证"""
        # 测试缺少镜像源的情况
        builder1 = (MCPBuilder()
                    .for_mcp_server("测试服务")
                    .add_tool("test_tool", "input", "str", "str", "测试工具", "output = 'test'")
                    .set_up("测试作者"))
        
        with pytest.raises(ValueError, match="必须设置镜像源地址，请调用 from_market\\(\\) 方法"):
            builder1.build()
        
        # 测试缺少工具的情况
        builder2 = (MCPBuilder()
                    .for_mcp_server("测试服务")
                    .from_market("http://localhost:8000")
                    .set_up("测试作者"))
        
        with pytest.raises(ValueError, match="必须至少添加一个工具，请调用 add_tool\\(\\) 方法"):
            builder2.build()
        
        # 测试缺少服务器名称的情况
        builder3 = (MCPBuilder()
                    .add_tool("test_tool", "input", "str", "str", "测试工具", "output = 'test'")
                    .from_market("http://localhost:8000")
                    .set_up("测试作者"))
        
        with pytest.raises(ValueError, match="必须设置服务器名称，请调用 for_mcp_server\\(\\) 方法"):
            builder3.build()
    
    def test_api_url_building_with_token(self):
        """测试带 token 的 API URL 构建"""
        builder = (MCPBuilder()
                   .for_mcp_server("Token测试服务")
                   .add_tool("test_tool", "input", "str", "str", "测试工具", "output = 'test'")
                   .from_market("http://localhost:8000", "test-token"))
        
        # 测试 URL 构建
        api_url = builder._build_api_url()
        assert api_url == "http://localhost:8000/api/generate-mcp"
        
        # 测试配置构建
        config = builder.build()
        assert config["api_token"] == "test-token"


class TestBackwardCompatibility:
    """向后兼容性测试"""
    
    def test_old_style_calls_still_work(self):
        """测试旧的调用方式仍然有效（通过新的方法组合）"""
        # 模拟旧的 set_up 调用方式
        builder = (MCPBuilder()
                   .for_mcp_server("兼容性测试")
                   .add_tool("test_tool", "input", "str", "str", "测试工具", "output = 'test'")
                   .from_market("http://localhost:8000")  # 相当于旧的 api_url
                   .set_up("兼容性作者"))  # 相当于旧的 author
        
        config = builder.build()
        assert config["server_name"] == "兼容性测试"
        assert config["api_url"] == "http://localhost:8000"
        assert config["author"] == "兼容性作者"


if __name__ == "__main__":
    pytest.main([__file__])
