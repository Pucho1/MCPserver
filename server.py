import asyncio
import subprocess
from fastmcp import Context

from pathlib import Path
import sys

from core.mcp_instance import mcp
from middleware.debug import DebugMiddleware
import tools.notes
import tools.filesystem


mcp.add_middleware(
    DebugMiddleware()
)

# -----PROMPTS ------

@mcp.prompt()
def summarize_file(filename: str) -> str:
    """
    Generate a summarization prompt for a file.
    """

    return f"Please summarize the contents of {filename}"


# ----- TOOLS ------



# ----- SHELL ------

@mcp.tool()
async def run_git_status() -> str:
    """
    Run git status command safely and return the output.
    """

    try:

        result = await asyncio.to_thread(
            subprocess.run,
            ["git", "status"],
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.returncode != 0:

            error_message = result.stderr.decode().strip()

            raise Exception(
                f"Error running git status: {error_message}"
            )

        return result.stdout.strip()

    except asyncio.TimeoutError:

        raise TimeoutError(
            "git status command timed out"
        )

    except Exception as e:

        raise Exception(
            f"Unexpected error running git status: {str(e)}"
        )


# -----RESOUCERS ------


@mcp.resource("filesystem://cwd")
async def current_directory() -> str:
    """
    Current working directory.
    """

    return str(Path.cwd())





if __name__ == "__main__":
    mcp.run(transport="stdio")
