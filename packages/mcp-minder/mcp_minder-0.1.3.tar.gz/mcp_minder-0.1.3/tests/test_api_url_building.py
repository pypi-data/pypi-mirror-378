"""
API URL 构建测试

测试 MCPBuilder 的 API URL 自动构建功能
"""

import pytest
from minder import MCPBuilder


class TestAPIURLBuilding:
    """API URL 构建测试类"""
    
    def test_build_api_url_with_domain_only(self):
        """测试只指定域名的情况"""
        builder = MCPBuilder()
        builder._api_url = "http://localhost:8000"
        
        api_url = builder._build_api_url()
        assert api_url == "http://localhost:8000/api/generate-mcp"
    
    def test_build_api_url_with_domain_and_port(self):
        """测试指定域名和端口的情况"""
        builder = MCPBuilder()
        builder._api_url = "http://example.com:8080"
        
        api_url = builder._build_api_url()
        assert api_url == "http://example.com:8080/api/generate-mcp"
    
    def test_build_api_url_with_trailing_slash(self):
        """测试带末尾斜杠的情况"""
        builder = MCPBuilder()
        builder._api_url = "http://localhost:8000/"
        
        api_url = builder._build_api_url()
        assert api_url == "http://localhost:8000/api/generate-mcp"
    
    def test_build_api_url_with_existing_api_path(self):
        """测试已经包含 API 路径的情况"""
        builder = MCPBuilder()
        builder._api_url = "http://localhost:8000/api/generate-mcp"
        
        api_url = builder._build_api_url()
        assert api_url == "http://localhost:8000/api/generate-mcp"
    
    def test_build_api_url_with_api_endpoint(self):
        """测试以 /api 结尾的情况"""
        builder = MCPBuilder()
        builder._api_url = "http://localhost:8000/api"
        
        api_url = builder._build_api_url()
        assert api_url == "http://localhost:8000/api"
    
    def test_build_api_url_with_other_path(self):
        """测试包含其他路径的情况"""
        builder = MCPBuilder()
        builder._api_url = "http://localhost:8000/v1/api/generate-mcp"
        
        api_url = builder._build_api_url()
        assert api_url == "http://localhost:8000/v1/api/generate-mcp"
    
    def test_build_api_url_with_https(self):
        """测试 HTTPS 协议的情况"""
        builder = MCPBuilder()
        builder._api_url = "https://api.example.com"
        
        api_url = builder._build_api_url()
        assert api_url == "https://api.example.com/api/generate-mcp"
    
    def test_build_api_url_with_subdomain(self):
        """测试子域名的情况"""
        builder = MCPBuilder()
        builder._api_url = "http://mcp-api.example.com:9000"
        
        api_url = builder._build_api_url()
        assert api_url == "http://mcp-api.example.com:9000/api/generate-mcp"


def test_integration_with_set_up():
    """测试与 set_up 方法的集成"""
    builder = (MCPBuilder()
               .for_mcp_server("测试服务")
               .add_tool("test_tool", "input", "str", "str", "测试工具", "output = 'test'")
               .set_up("http://localhost:8000", "测试作者"))
    
    # 验证 API URL 被正确设置
    assert builder._api_url == "http://localhost:8000"
    
    # 验证构建的 URL
    api_url = builder._build_api_url()
    assert api_url == "http://localhost:8000/api/generate-mcp"


if __name__ == "__main__":
    pytest.main([__file__])
