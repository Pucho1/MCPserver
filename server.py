import asyncio
import subprocess
from fastmcp import Context

from pathlib import Path
import sys

from core.mcp_instance import mcp
from core.logger import logger
from middleware.debug import DebugMiddleware
from services import filesystem_service
import tools.notes


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


# ----- FILESYSTEM ------

@mcp.tool()
async def list_files(path: str = ".") -> list[str]:
    # De aqui sale la descripcion de la tool
    """
    List files in a directory.
    """

    listed_files = filesystem_service.list_files(path)

    return listed_files


@mcp.tool()
async def read_file(path: str) -> str:
    """
    Read a file content.
    """
    file_content = filesystem_service.read_file(path)

    return file_content



@mcp.tool()
async def write_file(
    path: str,
    content: str,
) -> str:
    """
    Write content into a file.
    """
    result = filesystem_service.write_file(path, content)

    return result


@mcp.tool()
async def create_directory(
    path: str
) -> str:
    """
    Create directory.
    """

    result = filesystem_service.create_directory(path)

    return result




# ----- REST API ------

@mcp.tool()
async def get_post(
    post_id: int,
    context: Context
) -> dict:
    """
    Fetch a post from a post id.
    """
    
    rest_service = context.lifespan_context["rest_service"]
    
    post_data = await rest_service.get_post(post_id)

    return post_data




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
