"""
MCP Minder API 使用示例

演示如何使用统一的API客户端管理MCP服务
"""

import asyncio
from minder.client.api_client import MCPMinderAPIClient


async def main():
    """主函数 - 演示异步API使用"""
    
    # 创建API客户端
    async with MCPMinderAPIClient("http://localhost:8000") as client:
        
        print("🔍 健康检查...")
        health = await client.async_health_check()
        print(f"状态: {health}")
        
        print("\n📋 获取服务列表...")
        services = await client.async_get_services()
        print(f"服务数量: {services.get('total', 0)}")
        
        # 创建新服务示例
        print("\n🆕 创建新服务...")
        service_data = {
            "name": "example_service",
            "file_path": "mcpserver/example.py",
            "host": "127.0.0.1",
            "description": "示例MCP服务",
            "author": "示例用户"
        }
        
        try:
            result = await client.async_create_service(service_data)
            if result.get("success"):
                print(f"✅ 服务创建成功: {result.get('message')}")
                service_id = result.get("service", {}).get("id")
                
                # 启动服务
                print("\n🚀 启动服务...")
                start_result = await client.async_start_service(service_id)
                if start_result.get("success"):
                    print(f"✅ 服务启动成功: {start_result.get('message')}")
                    
                    # 获取服务日志
                    print("\n📄 获取服务日志...")
                    logs = await client.async_get_service_logs(service_id, lines=10)
                    if logs.get("success"):
                        print(f"日志内容:\n{logs.get('logs', '无日志')}")
                    
                    # 停止服务
                    print("\n⏹️ 停止服务...")
                    stop_result = await client.async_stop_service(service_id)
                    if stop_result.get("success"):
                        print(f"✅ 服务停止成功: {stop_result.get('message')}")
                
                # 删除服务
                print("\n🗑️ 删除服务...")
                delete_result = await client.async_delete_service(service_id)
                if delete_result.get("success"):
                    print(f"✅ 服务删除成功: {delete_result.get('message')}")
            else:
                print(f"❌ 服务创建失败: {result.get('error')}")
                
        except Exception as e:
            print(f"❌ 操作失败: {e}")


def sync_example():
    """同步API使用示例"""
    
    # 创建API客户端
    with MCPMinderAPIClient("http://localhost:8000") as client:
        
        print("🔍 健康检查...")
        health = client.health_check()
        print(f"状态: {health}")
        
        print("\n📋 获取服务列表...")
        services = client.get_services()
        print(f"服务数量: {services.get('total', 0)}")
        
        # 获取MCP服务列表
        print("\n🔗 获取MCP服务列表...")
        mcp_services = client.get_mcp_services()
        if mcp_services.get("success"):
            print(f"可用MCP服务: {mcp_services.get('count', 0)}")
            for service in mcp_services.get("services", []):
                print(f"  - {service.get('name')}: {service.get('status')}")
        
        # 同步服务状态
        print("\n🔄 同步服务状态...")
        sync_result = client.sync_service_status()
        if sync_result.get("success"):
            print(f"✅ 同步成功: {sync_result.get('message')}")
        
        # 文件上传示例（需要实际的文件）
        print("\n📦 文件上传示例:")
        print("注意：此示例需要提供实际的MCP服务器文件")
        
        # Python文件上传示例
        print("\n🐍 Python文件上传示例:")
        # result = client.upload_python_file(
        #     file_path="path/to/your/mcp_server.py",
        #     service_name="uploaded_python_service",
        #     description="从Python文件部署的服务",
        #     auto_start=True
        # )
        # if result.get("success"):
        #     print(f"✅ Python文件上传成功: {result.get('message')}")
        #     print(f"服务ID: {result.get('service_id')}")
        #     print(f"文件路径: {result.get('file_path')}")
        
        # 压缩包上传示例
        print("\n📦 压缩包上传示例:")
        # result = client.upload_package(
        #     file_path="path/to/your/mcp_server.zip",
        #     service_name="uploaded_package_service",
        #     description="从zip文件部署的服务",
        #     auto_start=True
        # )
        # if result.get("success"):
        #     print(f"✅ 压缩包上传成功: {result.get('message')}")
        #     print(f"服务ID: {result.get('service_id')}")
        #     print(f"入口文件: {result.get('entry_file')}")


if __name__ == "__main__":
    print("🚀 MCP Minder API 使用示例")
    print("=" * 50)
    
    # 运行异步示例
    print("\n📱 异步API示例:")
    asyncio.run(main())
    
    print("\n" + "=" * 50)
    
    # 运行同步示例
    print("\n🔄 同步API示例:")
    sync_example()
    
    print("\n✅ 示例运行完成!")
