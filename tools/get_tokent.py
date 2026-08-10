from core.mcp_instance import mcp
from fastmcp.server.dependencies import get_access_token
from fastmcp.server.auth import require_scopes

from core.tracing import trace_tool


# Add a protected tool to test authentication
@mcp.tool
@trace_tool
async def get_token_info() -> dict:
    """Returns information about the Auth0 token."""

    token = get_access_token()

    return {
        "token": token,
        "issuer": token.claims.get("iss"),
        "audience": token.claims.get("aud"),
        "scope": token.claims.get("scope")
    }


@mcp.tool(auth=require_scopes("admin"))
@trace_tool
async def admin_operation() -> str:

    """Returns information about the Auth0 token."""
    return "Admin action completed"