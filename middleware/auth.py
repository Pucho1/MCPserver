from fastmcp.server.dependencies import get_http_headers
from fastmcp.server.middleware import (
    Middleware,
    MiddlewareContext
)
from mcp import ErrorData, McpError

class AuthMiddleware(Middleware):
    def __init__(self, settings):
        self.api_key = settings.api_key
    

    async def on_initialize(self, context: MiddlewareContext, call_next):
        try:

            print(f"Context info====>: {context.message}")

            params = context.message.params

            # FastMCP/MCP entrega `params` como un objeto tipado durante
            # `initialize`, no como dict, así que debemos leer atributos.
            if isinstance(params, dict):
                client_info = params.get("clientInfo", {})
            else:
                client_info = getattr(params, "clientInfo", None)

            print(f"Client info: {client_info}")

            if isinstance(client_info, dict):
                client_name = client_info.get("name", "unknown")
            else:
                client_name = getattr(client_info, "name", "unknown")

            print(f"Client name>>>>>>>>>>: {client_name}")

            # Reject before call_next to send error to client
            if client_name == "blocked-client":
                raise McpError(ErrorData(code=-32000, message="Client not supported"))

            await call_next(context)
            print(f"Client {client_name} initialized")

        except Exception as e:
            print(f"Error during initialization: {e}")
            raise McpError(ErrorData(code=-32001, message=f"Error during initialization: {e}")) from e
