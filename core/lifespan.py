from fastmcp import FastMCP
from fastmcp.server.lifespan import lifespan

import httpx
import aiosqlite

from core.logger import logger
from core.langfuse_config import langfuse_client
from core.tracing import trace_operation


from services.health_service import HealthService
from services.notes_service import NotesService
from services.rest_service import PostService
from config.settings import load_settings


@lifespan
async def app_lifespan(server: FastMCP):

    """
    Controla el arranque y apagado del servidor MCP.
    gestor del ciclo de vida del servidor, se ejecuta al iniciar y cerrar el servidor.
    Maneja todas la conexiónes de forma concurrente y segura.
    Integra Langfuse tracing para observabilidad.
    """

    logger.info("Creando cliente compartiddos para el servidor")

    # Trace initialization
    async with trace_operation("mcp_server_startup", tags=["startup"]) as trace:
        # 1. Creamos el cliente HTTP asíncrono
        http_client = httpx.AsyncClient()

        settings = load_settings()

        # 2. Conectamos de forma asíncrona a SQLite con aiosqlite
        db_conn = await aiosqlite.connect(settings.db_path)

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

        # 4. Creamos instancias de los servicios que usaremos en las herramientas del servidor, 
        # pasandoles las conexiones necesarias 
        notes_service  = NotesService(db_conn)

        rest_service   = PostService(http_client)

        health_service = HealthService(db_conn)
        
        # Record startup configuration
        trace.update(
            output={
                "status": "initialized",
                "db_path": settings.db_path,
                "transport": settings.transport,
                "langfuse_enabled": langfuse_client is not None,
            }
        )

        yield {
            "http_client": http_client,
            "db_connection": db_conn,
            "notes_service": notes_service,
            "rest_service": rest_service,
            "health_service": health_service,
        }

    logger.info("Cerrando cliente compartidos para el servidor")
    
    # Trace shutdown
    async with trace_operation("mcp_server_shutdown", tags=["shutdown"]):
        # Cerramos las conexiones de forma asíncrona al apagar el servidor
        await db_conn.close()
        await http_client.aclose()
        
        # Flush any remaining Langfuse events
        if langfuse_client:
            langfuse_client.flush()


