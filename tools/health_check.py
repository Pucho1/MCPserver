from core.mcp_instance import mcp
from fastmcp import Context


@mcp.tool()
async def health_check(context: Context,) -> dict:
    """
    Check the health of the server.
    """

    health_status = await context.lifespan_context["health_service"].check()

    return health_status