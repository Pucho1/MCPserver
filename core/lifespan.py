from fastmcp import FastMCP
from fastmcp.server.lifespan import lifespan

import httpx
import aiosqlite
from core.logger import logger
from services.notes_service import NotesService


@lifespan
async def app_lifespan(server: FastMCP):

    """
    Controla el arranque y apagado del servidor MCP.
    gestor del ciclod e vida del servidor, se ejecuta al iniciar y cerrar el servidor.
    Maneja todas la conexiónes de forma concurrente y segura.
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

    notes_service = NotesService(
        db_conn
    )

    yield {
        "http_client": client,
        "db_connection": db_conn,
        "notes_service": notes_service,
    }

    logger.info("Cerrando cliente compartidos para el servidor")
    
    await db_conn.close()
    await client.aclose()

