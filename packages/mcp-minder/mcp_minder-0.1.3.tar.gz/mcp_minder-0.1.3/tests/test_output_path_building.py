"""
输出路径构建测试

测试 MCPBuilder 和 API 接口的输出路径构建功能
"""

import pytest
import tempfile
import os
from pathlib import Path
from minder import MCPBuilder


class TestOutputPathBuilding:
    """输出路径构建测试类"""
    
    def test_mcp_builder_path_building(self):
        """测试 MCPBuilder 的路径构建"""
        builder = MCPBuilder().for_mcp_server("测试服务")
        
        # 测试相对路径
        output_path = builder._build_output_path("server.py")
        assert "mcpserver" in output_path
        assert "测试服务" in output_path
        assert output_path.endswith("server.py")
        
        # 测试绝对路径
        abs_path = "/tmp/test_server.py"
        result = builder._build_output_path(abs_path)
        assert result == abs_path
    
    def test_mcp_builder_path_building_with_filename_only(self):
        """测试只指定文件名的情况"""
        builder = MCPBuilder().for_mcp_server("天气服务")
        
        output_path = builder._build_output_path("weather.py")
        assert "mcpserver" in output_path
        assert "天气服务" in output_path
        assert output_path.endswith("weather.py")
    
    def test_mcp_builder_path_building_with_default(self):
        """测试默认文件名的情况"""
        builder = MCPBuilder().for_mcp_server("计算服务")
        
        output_path = builder._build_output_path("main.py")
        assert "mcpserver" in output_path
        assert "计算服务" in output_path
        assert output_path.endswith("main.py")
    
    def test_mcp_builder_save_template_with_path(self):
        """测试保存模板时的路径构建"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # 临时修改工作目录
            original_cwd = os.getcwd()
            os.chdir(temp_dir)
            
            try:
                builder = (MCPBuilder()
                           .for_mcp_server("路径测试服务")
                           .add_tool("test_tool", "input", "str", "str", "测试工具", "output = 'test'"))
                
                # 测试保存到相对路径
                success = builder.save_template("test_server.py")
                assert success is True
                
                # 验证文件是否保存在正确的位置
                expected_path = Path(temp_dir) / "mcpserver" / "路径测试服务" / "test_server.py"
                assert expected_path.exists()
                
            finally:
                os.chdir(original_cwd)


class TestAPIPathBuilding:
    """API 路径构建测试类"""
    
    def test_api_path_building_function(self):
        """测试 API 路径构建函数"""
        from minder.api.routers.generator_router import _build_output_path
        
        # 测试相对路径
        output_path = _build_output_path("测试服务", "server.py")
        assert "mcpserver" in output_path
        assert "测试服务" in output_path
        assert output_path.endswith("server.py")
        
        # 测试绝对路径
        abs_path = "/tmp/api_test_server.py"
        result = _build_output_path("测试服务", abs_path)
        assert result == abs_path
    
    def test_api_path_building_with_filename_only(self):
        """测试 API 只指定文件名的情况"""
        from minder.api.routers.generator_router import _build_output_path
        
        output_path = _build_output_path("API测试服务", "api_server.py")
        assert "mcpserver" in output_path
        assert "API测试服务" in output_path
        assert output_path.endswith("api_server.py")
    
    def test_api_path_building_with_default_filename(self):
        """测试 API 默认文件名的情况"""
        from minder.api.routers.generator_router import _build_output_path
        
        output_path = _build_output_path("默认服务", "main.py")
        assert "mcpserver" in output_path
        assert "默认服务" in output_path
        assert output_path.endswith("main.py")


class TestPathStructure:
    """路径结构测试类"""
    
    def test_directory_creation(self):
        """测试目录创建"""
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = os.getcwd()
            os.chdir(temp_dir)
            
            try:
                builder = MCPBuilder().for_mcp_server("目录测试")
                
                # 构建路径（这会创建目录）
                output_path = builder._build_output_path("test.py")
                
                # 验证目录是否被创建
                service_dir = Path(temp_dir) / "mcpserver" / "目录测试"
                assert service_dir.exists()
                assert service_dir.is_dir()
                
            finally:
                os.chdir(original_cwd)
    
    def test_multiple_services_directory_structure(self):
        """测试多个服务的目录结构"""
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = os.getcwd()
            os.chdir(temp_dir)
            
            try:
                # 创建多个服务
                services = ["服务1", "服务2", "服务3"]
                paths = []
                
                for service_name in services:
                    builder = MCPBuilder().for_mcp_server(service_name)
                    path = builder._build_output_path("server.py")
                    paths.append(path)
                
                # 验证所有服务目录都被创建
                mcpserver_dir = Path(temp_dir) / "mcpserver"
                assert mcpserver_dir.exists()
                
                for service_name in services:
                    service_dir = mcpserver_dir / service_name
                    assert service_dir.exists()
                    assert service_dir.is_dir()
                
            finally:
                os.chdir(original_cwd)


if __name__ == "__main__":
    pytest.main([__file__])
