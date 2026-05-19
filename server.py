from mcp.server.fastmcp import FastMCP, Context
from mcp.types import SamplingMessage, TextContent

from pathlib import Path

mcp = FastMCP(name="Filesystem-server")

@mcp.tool()
async def summarize(text_to_summarize: str, ctx: Context):

    """
        Resumen texto
    """

    result = await ctx.sample(
        prompt=f"Por favor, resume el siguiente texto de forma concisa: {text_to_summarize}",
        max_tokens=500
    )
    
    # result ya es un objeto que contiene la respuesta procesada por el cliente
    # FastMCP suele mapear el contenido directamente o como una lista de contenidos
    if hasattr(result, "content") and result.content:
        return result.content[0].text
    
    return str(result)

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