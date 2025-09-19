import asyncio
from mcp.server.fastmcp import FastMCP
from tools.item_delivery_tool import register_item_delivery_tool

mcp = FastMCP(name="配送服务",port=8009,debug=True)

mcp = register_item_delivery_tool(mcp)

if __name__ == "__main__":
    asyncio.run(mcp.run(transport="streamable-http"))
 