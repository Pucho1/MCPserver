from time import perf_counter

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
        start = perf_counter()
        tool_event = build_tool_event(tool=tool_name, status="start")

        logger.info(tool_event)

        try:

            result = await call_next(context) # Permite que la peticion fluya que no se corte en este midelware

        except Exception as e:
            duration_ms = round((perf_counter() - start) * 1000, 2)
            tool_event = build_tool_event(tool=tool_name, status="error", error=str(e), duration_ms=duration_ms)
            logger.error(tool_event)
            raise

        duration_ms = round((perf_counter() - start) * 1000, 2)

        tool_event = build_tool_event(tool=tool_name, status="success", duration_ms=duration_ms)
        logger.info(tool_event)

        return result