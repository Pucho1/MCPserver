from fastmcp import FastMCP
from core.lifespan import app_lifespan

mcp = FastMCP(
    "Filesystem-server",
    lifespan=app_lifespan
)