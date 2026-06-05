from fastmcp.server.middleware import (
    Middleware,
    MiddlewareContext
)
from core.logger import logger



class DebugMiddleware(Middleware):

    async def on_call_tool(
        self,
        context: MiddlewareContext, # me da acceso a toda la request   method/source/timestamp/type/message...
        call_next
    ):
        tool_name = getattr(context.message, "name", "<sin nombre>")
        
        before_message = f"ANTES -> method={context.method} tool={tool_name}"
        logger.info(before_message)

        # print(
        #     "ANTES",
        #     file=sys.stderr
        # )

        # print(
        #     f"→ {context.method}",
        #     file=sys.stderr
        # )

        result = await call_next(context) # Permite que la peticion fluya que no se corte en este midelware

        # print(
        #     f"→ {context.method}",
        #     file=sys.stderr
        # )

        # print(
        #     f"← {context.method}",
        #     file=sys.stderr
        # )

        after_message = f"DESPUES -> method={context.method} tool={tool_name}"
        logger.info(after_message)

        return result