from fastmcp import FastMCP, Context
from mcp.types import SamplingMessage, TextContent
from fastmcp.server.lifespan import lifespan

from pathlib import Path
import httpx


@lifespan
async def app_lifespan(server):

    print("Creando cliente HTTP compartido")

    client = httpx.AsyncClient()

    yield {
        "http_client": client
    }

    print("Cerrando cliente HTTP")

    await client.aclose()

mcp = FastMCP(name="Filesystem-server", lifespan=app_lifespan)




# -----PROMPTS ------

@mcp.prompt()
def summarize_file(filename: str) -> str:
    """
    Generate a summarization prompt for a file.
    """

    return f"Please summarize the contents of {filename}"





# ----- TOOLS ------

@mcp.tool()
async def list_files(path: str = ".") -> list[str]:
    # De aqui sale la descripcion de la tool
    """
    List files in a directory. 
    """

    import os

    return os.listdir(path)






# -----RESOUCERS ------


@mcp.resource("filesystem://cwd")
async def current_directory() -> str:
    """
    Current working directory.
    """

    return str(Path.cwd())




if __name__ == "__main__":
    mcp.run(transport="stdio")