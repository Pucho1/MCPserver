from fastmcp import FastMCP
from core.lifespan import app_lifespan
from core.auth import create_auth_provider


from config.settings import load_settings
from middleware.security.fast_mcp_middleware import get_middleware


settings = load_settings()

mcp = FastMCP(
    "Filesystem-server",
    lifespan=app_lifespan,
    auth=create_auth_provider(settings),
    middleware= get_middleware()
)