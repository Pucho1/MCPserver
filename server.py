from fastmcp import FastMCP, Context
from fastmcp.server.lifespan import lifespan
from fastmcp.server.middleware import (
    Middleware,
    MiddlewareContext
)

from pathlib import Path
import httpx
import logging
import sys



# creo el archivo para guardar mis logs 
logger = logging.getLogger("mcp_server")
logger.setLevel(logging.INFO)

if not logger.handlers:
    handler = logging.FileHandler("server.log", encoding="utf-8")
    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)




@lifespan
async def app_lifespan(server):

    logger.info("Creando cliente HTTP compartido")

    client = httpx.AsyncClient()

    yield {
        "http_client": client
    }

    logger.info("Cerrando cliente HTTP")

    await client.aclose()



class DebugMiddleware(Middleware):

    async def on_call_tool(
        self,
        context: MiddlewareContext, # me da acceso a toda la request   method/source/timestamp/type/message...
        call_next
    ):
        tool_name = getattr(context.message, "name", "<sin nombre>")
        before_message = f"ANTES -> method={context.method} tool={tool_name}"
        
        logger.info(before_message)

        # print(
        #     "ANTES",
        #     file=sys.stderr
        # )

        # print(
        #     f"→ {context.method}",
        #     file=sys.stderr
        # )

        result = await call_next(context) # Permite que la peticion fluya que no se corte en este midelware

        # print(
        #     f"→ {context.method}",
        #     file=sys.stderr
        # )

        # print(
        #     f"← {context.method}",
        #     file=sys.stderr
        # )

        after_message = f"DESPUES -> method={context.method} tool={tool_name}"
        logger.info(after_message)

        return result





mcp = FastMCP(name="Filesystem-server", lifespan=app_lifespan)

mcp.add_middleware(DebugMiddleware())



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

@mcp.tool()
async def read_file(path: str) -> str:
    """
    Read a file content.
    """

    from pathlib import Path

    return Path(path).read_text(
        encoding="utf-8"
    )


@mcp.tool()
async def write_file(
    path: str,
    content: str
) -> str:
    """
    Write content into a file.
    """

    from pathlib import Path

    Path(path).write_text(
        content,
        encoding="utf-8"
    )

    return "File written"


@mcp.tool()
async def create_directory(
    path: str
) -> str:
    """
    Create directory.
    """

    from pathlib import Path

    Path(path).mkdir(
        parents=True,
        exist_ok=True
    )

    return "Directory created"




# --------TEST---------

@mcp.tool()
async def fetch_page(
    url: str,
    ctx: Context
):

    client = ctx.lifespan_context["http_client"]

    response = await client.get(url)

    return {
        "status": response.status_code,
        "size": len(response.text)
    }





# -----RESOUCERS ------


@mcp.resource("filesystem://cwd")
async def current_directory() -> str:
    """
    Current working directory.
    """

    return str(Path.cwd())




if __name__ == "__main__":
    mcp.run(transport="stdio")
