from fastmcp import Context
from core.mcp_instance import mcp
from core.tracing import trace_tool

# ----- REST API ------

@mcp.tool()
@trace_tool
async def get_post(
    post_id: int,
    context: Context
) -> dict:
    """
    Fetch a post from a post id.
    """
    
    rest_service = context.lifespan_context["rest_service"]
    
    post_data = await rest_service.get_post(post_id)

    return post_data

