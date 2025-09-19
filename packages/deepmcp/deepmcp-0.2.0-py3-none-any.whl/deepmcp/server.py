import os

from nacos_mcp_wrapper.server.nacos_mcp import NacosMCP
from nacos_mcp_wrapper.server.nacos_settings import NacosSettings

# Create an MCP server instance
nacos_settings = NacosSettings()
nacos_settings.SERVER_ADDR = "127.0.0.1:8848" # <nacos_server_addr> e.g. 127.0.0.1:8848
nacos_settings.USERNAME="nacos"
nacos_settings.PASSWORD="nacos"
mcp = NacosMCP("nacos-calculator-mcp-server", nacos_settings=nacos_settings, version="0.1.0", port=18001)
# Register an addition tool
@mcp.tool()
def add(a: float, b: float) -> float:
    """Adds two numbers (int or float)."""
    return a + b
# Register a subtract tool
@mcp.tool()
def subtract(a: float, b: float) -> float:
    """Subtracts two numbers (int or float)."""
    return a - b
# Register a multiply tool
@mcp.tool()
def multiply(a: float, b: float) -> float:
    """Multiplies two numbers (int or float)."""
    return a * b
# Register a divide tool
@mcp.tool()
def divide(a: float, b: float) -> float:
    """Divides two numbers (int or float)."""
    if b == 0:
        raise ValueError("Cannot divide by zero.")
    return a / b
# Register a power tool
@mcp.tool()
def power(base: float, exponent: float) -> float:
    """Raises a number to the power of another number."""
    return base ** exponent


def init():
    mode = os.getenv("NACOS_ENABLE", False)
    if not mode:
        raise ValueError("env var: NACOS_ENABLE needs to be set to True, False for later")
def main():
    try:
        init()
        mcp.run(transport="sse")
        # mcp.run(transport="stdio")
        # mcp.run(transport="streamable-http")
    except Exception as e:
        print(f"Runtime error: {e}")

