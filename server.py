from core.mcp_instance import mcp
from middleware.auth import AuthMiddleware
from middleware.debug import DebugMiddleware
from config.settings import load_settings

# ---Tools ---
from middleware.ratel_imiter import RateLimitMiddleware
import tools.notes
import tools.filesystem
import tools.rest_post
import tools.health_check

# ---Resources ---
import resources.filesystem

# ---Prompts ---
import prompts.summarize

settings = load_settings()



mcp.add_middleware(
    DebugMiddleware(),
)

mcp.add_middleware(
    AuthMiddleware(settings=settings),
)

# mcp.add_middleware(
#     RateLimitMiddleware(requests_per_minute=settings.requests_per_minute),
# )

def main():
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


if __name__ == "__main__":
    main()