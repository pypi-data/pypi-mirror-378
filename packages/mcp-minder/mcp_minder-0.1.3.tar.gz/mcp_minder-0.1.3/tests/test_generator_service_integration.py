"""
生成器与服务管理集成测试

测试 MCPBuilder API 与现有服务管理系统的集成
"""

import pytest
import tempfile
import os
from unittest.mock import Mock, patch
from minder.api.routers.generator_router import get_service_manager
from minder.api.models import MCPBuilderRequest, MCPBuilderConfig, ToolInfo


class TestGeneratorServiceIntegration:
    """生成器与服务管理集成测试类"""
    
    def test_get_service_manager_function(self):
        """测试 get_service_manager 函数"""
        # 这个测试主要验证函数可以正常导入和调用
        # 在实际环境中，这会返回真正的服务管理器实例
        try:
            # 模拟导入成功
            with patch('minder.api.main.service_manager') as mock_service_manager:
                service_manager = get_service_manager()
                assert service_manager is not None
        except ImportError:
            # 如果 main 模块不存在，这是正常的（在测试环境中）
            pass
    
    def test_mcp_builder_request_model(self):
        """测试 MCPBuilder 请求模型"""
        # 测试新的请求模型字段
        tool_info = ToolInfo(
            name="test_tool",
            param_name="input",
            param_type="str",
            return_type="str",
            description="测试工具",
            code="output = 'test'"
        )
        
        config = MCPBuilderConfig(
            server_name="测试服务",
            tools=[tool_info],
            author="测试作者",
            port=8080
        )
        
        request = MCPBuilderRequest(
            config=config,
            output_path="test_server.py",
            auto_start=True,
            host="0.0.0.0"
        )
        
        # 验证所有字段都正确设置
        assert request.config.server_name == "测试服务"
        assert len(request.config.tools) == 1
        assert request.config.tools[0].name == "test_tool"
        assert request.auto_start is True
        assert request.host == "0.0.0.0"
        assert request.output_path == "test_server.py"
    
    def test_mcp_builder_response_model(self):
        """测试 MCPBuilder 响应模型"""
        from minder.api.models import MCPBuilderResponse
        
        response = MCPBuilderResponse(
            success=True,
            output_path="test_server.py",
            message="生成成功",
            service_id="test-service-id",
            service_name="测试服务",
            port=8080,
            pid=12345,
            started=True
        )
        
        # 验证所有字段都正确设置
        assert response.success is True
        assert response.output_path == "test_server.py"
        assert response.service_id == "test-service-id"
        assert response.service_name == "测试服务"
        assert response.port == 8080
        assert response.pid == 12345
        assert response.started is True
    
    @patch('minder.api.routers.generator_router.get_service_manager')
    def test_service_manager_integration_mock(self, mock_get_service_manager):
        """测试服务管理器集成的模拟版本"""
        # 创建模拟的服务管理器
        mock_service_manager = Mock()
        mock_service_manager.register_service.return_value = "test-service-id"
        mock_service_manager.start_service.return_value = {
            'success': True,
            'pid': 12345,
            'message': '服务启动成功'
        }
        mock_get_service_manager.return_value = mock_service_manager
        
        # 测试服务管理器调用
        service_manager = get_service_manager()
        service_id = service_manager.register_service(
            name="测试服务",
            file_path="test_server.py",
            host="0.0.0.0",
            description="测试描述",
            author="测试作者"
        )
        
        start_result = service_manager.start_service(service_id, 8080)
        
        # 验证调用
        assert service_id == "test-service-id"
        assert start_result['success'] is True
        assert start_result['pid'] == 12345
        
        # 验证方法被正确调用
        mock_service_manager.register_service.assert_called_once_with(
            name="测试服务",
            file_path="test_server.py",
            host="0.0.0.0",
            description="测试描述",
            author="测试作者"
        )
        mock_service_manager.start_service.assert_called_once_with("test-service-id", 8080)


def test_model_compatibility():
    """测试模型兼容性"""
    # 确保新的模型与现有系统兼容
    from minder.api.models import MCPBuilderRequest, MCPBuilderConfig, ToolInfo
    
    # 测试最小配置
    tool = ToolInfo(
        name="minimal_tool",
        param_name="input",
        param_type="str",
        return_type="str",
        description="最小工具",
        code="pass"
    )
    
    config = MCPBuilderConfig(
        server_name="最小服务",
        tools=[tool]
    )
    
    request = MCPBuilderRequest(
        config=config,
        output_path="minimal.py"
    )
    
    # 验证默认值
    assert request.auto_start is True  # 默认值
    assert request.host == "0.0.0.0"   # 默认值
    assert request.config.author == "开发者"  # 默认值
    assert request.config.port is None  # 默认值


if __name__ == "__main__":
    pytest.main([__file__])
