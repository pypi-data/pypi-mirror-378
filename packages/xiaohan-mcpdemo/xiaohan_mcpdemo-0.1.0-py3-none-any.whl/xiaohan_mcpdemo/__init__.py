from mcp.server.fastmcp import FastMCP

mcp = FastMCP("add")

@mcp.tool
def add(a: int,b: int) -> int:
    """Add two int nummbers"""
    return a + b


def main() -> None:
    mcp.run(transport="stdio")
