import asyncio
import random
import sys
from fastmcp import FastMCP
from tools.item_delivery_tool import register_item_delivery_tool

mcp = FastMCP(name="配送服务",port=8009,debug=True)

mcp = register_item_delivery_tool(mcp)

if __name__ == "__main__":
        # 检查命令行参数中的端口
    port = None
    for i, arg in enumerate(sys.argv):
        if arg == "--port" and i + 1 < len(sys.argv):
            try:
                port = int(sys.argv[i + 1])
                break
            except ValueError:
                pass
    
    # 如果没有指定端口，使用随机端口
    if port is None:
        port = random.randint(10001, 18000)

    
    mcp.run(transport="streamable-http", host="0.0.0.0", port=port, path="/mcp", stateless_http=True)
 