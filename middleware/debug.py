from fastmcp.server.middleware import (
    Middleware,
    MiddlewareContext
)
from core.logger import logger
from core.observability import build_tool_event


class DebugMiddleware(Middleware):

    async def on_call_tool(
        self,
        context: MiddlewareContext, # me da acceso a toda la request   method/source/timestamp/type/message...
        call_next
    ):
        tool_name = getattr(context.message, "name", "<sin nombre>")
        tool_event = build_tool_event(tool=tool_name, status="started")

        logger.info(tool_event)

        try:

            result = await call_next(context) # Permite que la peticion fluya que no se corte en este midelware

        except Exception as e:
            tool_event = build_tool_event(tool=tool_name, status="failed", error=str(e))
            logger.error(tool_event)
            raise


        tool_event = build_tool_event(tool=tool_name, status="completed")
        logger.info(tool_event)

        return result