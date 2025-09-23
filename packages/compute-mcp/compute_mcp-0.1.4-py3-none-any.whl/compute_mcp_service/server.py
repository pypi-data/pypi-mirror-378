from fastmcp import FastMCP
import math
mcp = FastMCP("ComputeService")
# 算术工具组
@mcp.tool()
def add(a: float, b: float) -> float:
    """执行浮点数加法运算"""
    return a + b
@mcp.tool()
def subtract(a: float, b: float) -> float:
    """执行浮点数减法运算"""
    return a - b
@mcp.tool()
def multiply(a: float, b: float) -> float:
    """执行浮点数乘法运算"""
    return a * b
@mcp.tool()
def sqrt(number: float) -> float:
    """计算平方根"""
    return math.sqrt(number)
if __name__ == "__main__":
    mcp.run(transport="stdio")