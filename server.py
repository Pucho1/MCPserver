import asyncio
import subprocess
from fastmcp import Context
from fastmcp.server.middleware import (
    Middleware,
    MiddlewareContext
)

from pathlib import Path
import httpx
import sys


from core.mcp_instance import mcp
from core.logger import logger
from services.notes_service import NotesService

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
async def create_note(content: str, context: Context,) -> str:
    """
        Create a note in the database.
    """

    # accedo a la conexion de la base de datos que cree en el lifespan a traves del context.lifespan_context
    service = context.lifespan_context["notes_service"]


    last_row_id = await service.create_note(content)

    # el lastrowid es un atributo del cursor que devuelve el id de la 
    # ultima fila insertada en la base de datos, en este caso el id de la nota que acabamos de crear.
    return f"Note created with id {last_row_id}"


@mcp.tool()
async def get_single_note(
    note_id:int,
    context:Context,
) -> dict:
    """
    Fetch a note from the database.
    """

    # accedo a la conexion de la base de datos que cree en el lifespan a traves del context.lifespan_context 
    # y lo guardo en una variable para usarlo en esta funcion
    db_conn = context.lifespan_context["db_connection"] 

    # hago la consulta a la base de datos de forma asíncrona usando aiosqlite
    cursor = await db_conn.execute(
        "SELECT * FROM notes WHERE id = ?",
        (note_id,)
    )

    row = await cursor.fetchone()

    if row is None:
       raise ValueError(f"No se encontró ninguna nota con id {note_id}")

    return {"id": row[0], "content": row[1]}

@mcp.tool()
async def get_list_notes(context:Context,) -> dict:
    """
    Fetch all notes from the database.
    """

    # accedo a la conexion de la base de datos que cree en el lifespan a traves del context.lifespan_context 
    # y lo guardo en una variable para usarlo en esta funcion
    db_conn = context.lifespan_context["db_connection"] 

    # hago la consulta a la base de datos de forma asíncrona usando aiosqlite
    cursor = await db_conn.execute(
        "SELECT * FROM notes"
    )

    rows = await cursor.fetchall()


    if not rows:
       raise ValueError("No se encontró ninguna nota")

    return {"notes": [{"id": row[0], "content": row[1]} for row in rows]}


@mcp.tool()
async def update_note(
    note_id: int,
    new_content: str,
    context: Context,
) -> str:
    
    """
    Update a note in the database.
    """
    db_conn = context.lifespan_context["db_connection"]

    cursor  = await db_conn.execute(
        """
            UPDATE notes
            SET
            content=?,
            updated_at=
            datetime(
                'now',
                'localtime'
            )
            WHERE id=?
        """,
        (new_content, note_id)
    )


    if cursor.rowcount == 0:
        raise ValueError(
            f"Nota {note_id} no encontrada"
        )
    
    await db_conn.commit()

    return f"Note updated with id {note_id}"

@mcp.tool()
async def delete_note(
    note_id: int,
    context: Context,
) -> str:
    """
    Delete a note from the database.
    """
    db_conn = context.lifespan_context["db_connection"]

    cursor = await db_conn.execute(
        "DELETE FROM notes WHERE id = ?",
        (note_id,)
    )

    if cursor.rowcount == 0:
        raise ValueError(
            f"Nota {note_id} no encontrada"
        )

    await db_conn.commit()

    return f"Note deleted with id {note_id}"



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
