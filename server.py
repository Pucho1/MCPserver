import asyncio
import subprocess

import sys

from core.mcp_instance import mcp
from middleware.debug import DebugMiddleware

# ---Tools ---
import tools.notes
import tools.filesystem
import tools.rest_post

# ---Resources ---
import resources.filesystem

# ---Prompts ---
import prompts.summarize


mcp.add_middleware(
    DebugMiddleware()
)




if __name__ == "__main__":
    mcp.run(transport="stdio")
