from core.mcp_instance import mcp
from middleware.debug import DebugMiddleware
from config.settings import load_settings

# ---Tools ---
import tools.notes
import tools.filesystem
import tools.rest_post
import tools.health_check

# ---Resources ---
import resources.filesystem

# ---Prompts ---
import prompts.summarize


mcp.add_middleware(
    DebugMiddleware()
)


settings = load_settings()


if __name__ == "__main__":
    if settings.transport == "stdio":
        mcp.run(
            transport=settings.transport
        )
    elif settings.transport == "streamable-http":
        mcp.run(
            transport=settings.transport,
            host=settings.host,
            port=settings.port,
        )
    else:
        raise ValueError(f"Unsupported transport: {settings.transport}")