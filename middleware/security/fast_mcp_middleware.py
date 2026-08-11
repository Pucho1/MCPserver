from fastmcp.server.auth import AuthContext
from fastmcp.server.middleware import AuthMiddleware
from fastmcp.resources.base import Resource
from fastmcp.resources.template import ResourceTemplate
from fastmcp.tools.base import Tool


def authorize_component(ctx: AuthContext) -> bool:
    ''' Manejo de autorización a nivel de componentes (recursos, plantillas de recursos y herramientas) en MCP. '''

    if ctx.token is None:
        return False

    scopes = set(ctx.token.scopes)

    # Permite recursos y plantillas de recursos.
    if isinstance(ctx.component, (Resource, ResourceTemplate)):
        return "resources:read" in scopes

    # Permite herramientas.
    if isinstance(ctx.component, Tool):
        return "tools:use" in scopes

    # Prompts u otros componentes no contemplados: denegados.
    return False


def get_middleware() -> list[AuthMiddleware]:

    return [
        AuthMiddleware(
            auth=authorize_component
        )
    ]