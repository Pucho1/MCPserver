from core.mcp_instance import mcp
from pathlib import Path


@mcp.resource("filesystem://cwd")
async def current_directory() -> str:
    """
    Current working directory.
    """

    return str(Path.cwd())


