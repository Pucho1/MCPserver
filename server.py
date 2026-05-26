
from fastmcp import FastMCP, Context
from fastmcp.server.lifespan import lifespan
from fastmcp.server.middleware import (
    Middleware,
    MiddlewareContext
)

from pathlib import Path
import httpx
import aiosqlite
import logging
import sys



# creo un archivo para guardar mis logs 
logger = logging.getLogger("mcp_server")
logger.setLevel(logging.INFO)

if not logger.handlers:
    handler = logging.FileHandler("server.log", encoding="utf-8")
    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)




@lifespan
async def app_lifespan(server: FastMCP):

    """
    Controla el arranque y apagado del servidor MCP.
    Maneja la conexión a la base de datos de forma concurrente y segura.
    """

    logger.info("Creando cliente compartiddos para el servidor")

    # 1. Creamos el cliente HTTP asíncrono
    client = httpx.AsyncClient()

    # 2. Conectamos de forma asíncrona a SQLite con aiosqlite
    db_conn = await aiosqlite.connect("notes.db")

    # Habilitamos esto para poder interactuar con la BD de forma segura en entornos async
    await db_conn.execute("PRAGMA journal_mode=WAL;")

    # 3. Creamos la tabla de notas asíncronamente si no existe
    await db_conn.execute(
        """
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
            updated_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
        )
        """
    )

    await db_conn.commit()

    yield {
        "http_client": client,
        "db_connection": db_conn
    }

    logger.info("Cerrando cliente compartidos para el servidor")
    
    await db_conn.close()
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




# Inicializamos el servidor registrando tu lifespan
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


# ----- FILESYSTEM ------

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
    content: str,
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


# ----- REST API ------

@mcp.tool()
async def get_post(
    post_id: int,
    context: Context
) -> dict:
    """
    Fetch a post from a post id.
    """
    try:
    
        client = context.lifespan_context["http_client"]

        response_api = await client.get(
            f"https://jsonplaceholder.typicode.com/posts/{post_id}", timeout=10.0
        )


        if response_api.status_code != 200:
            logger.error(f"Error fetching post with id {post_id}: {response_api.status_code}")
            raise httpx.HTTPError(f"Error fetching post with id {post_id}: {response_api.status_code}")
        
        payload = response_api.json()

        response = { "body": payload.get("body"),  "title": payload.get("title") }

    except httpx.TimeoutException:
        logger.error(f"Error: Timeout when fetching post with id {post_id}")

        raise httpx.TimeoutException(f"Timeout when fetching post with id {post_id}")

    except httpx.ConnectError:
        logger.error(f"Error: Connection error when fetching post with id {post_id}")

        raise httpx.ConnectError(f"Connection error when fetching post with id {post_id}")

    except Exception as e:
        logger.error(f"Error: Unexpected error when fetching post with id {post_id} - {str(e)}")

        raise Exception(f"Unexpected error when fetching post with id {post_id} - {str(e)}")
    

    logger.info(response)
    return response





# ----- SQLITE ------

@mcp.tool()
async def create_note(content: str, context: Context) -> str:
    """
    Create a note in the database.
    """

    db_conn = context.lifespan_context["db_connection"]

    cursor = await db_conn.execute(
        "INSERT INTO notes (content) VALUES (?)",
        (content,)
    )

    await db_conn.commit()

    return f"Note created with id {cursor.lastrowid}"







# -----RESOUCERS ------


@mcp.resource("filesystem://cwd")
async def current_directory() -> str:
    """
    Current working directory.
    """

    return str(Path.cwd())




if __name__ == "__main__":
    mcp.run(transport="stdio")
