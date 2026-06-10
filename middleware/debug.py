from time import perf_counter
import uuid

from fastmcp.server.middleware import (
    Middleware,
    MiddlewareContext
)
from core.logger import logger
from core.observability import build_tool_event


class DebugMiddleware(Middleware):
    """
    Middleware de observabilidad para llamadas a herramientas.

    Su responsabilidad es envolver la ejecución real de cada tool para:
    - identificar qué herramienta se invocó,
    - medir cuánto tarda,
    - generar un id único por petición,
    - registrar un evento de inicio, éxito o error.

    Esto centraliza el logging técnico en un solo punto y evita repetir
    esta lógica dentro de cada herramienta individual.
    """

    async def on_call_tool(
        self,
        # `context` contiene la información de la llamada actual que FastMCP
        # está procesando, incluido el mensaje con el nombre de la tool.
        context: MiddlewareContext,
        call_next
    ):
        # Extraemos el nombre de la herramienta para incluirlo en logs.
        # `getattr` evita que falle si por algún motivo el mensaje no trae `name`.
        tool_name = getattr(context.message, "name", "<sin nombre>")

        # Marcamos el instante inicial con un reloj de alta precisión para
        # calcular la duración real de la ejecución en milisegundos.
        start = perf_counter()

        # Generamos un identificador único por llamada. Sirve para poder
        # relacionar fácilmente en logs el evento de inicio con el de éxito
        # o error de la misma petición.
        request_id = str(uuid.uuid4())

        # Registramos que la ejecución acaba de empezar. Esto ayuda a saber
        # qué tool fue invocada incluso si después falla antes de completarse.
        tool_event = build_tool_event(
            tool=tool_name,
            status="start",
            request_id=request_id,
        )

        logger.info(tool_event)

        try:
            # `call_next` delega la ejecución al siguiente middleware o a la
            # herramienta final. Sin esto, la petición se detendría aquí.
            result = await call_next(context)

        except Exception as e:
            # Si la tool falla, medimos cuánto tardó hasta el error y lo
            # registramos para poder diagnosticar problemas de latencia o fallos.
            duration_ms = round((perf_counter() - start) * 1000, 2)
            tool_event = build_tool_event(
                tool=tool_name,
                status="error",
                error=str(e),
                duration_ms=duration_ms,
                request_id=request_id,
            )
            logger.error(tool_event)
            # Re-lanzamos la excepción para no ocultar el error real al resto
            # del sistema; este middleware solo observa y registra.
            raise

        # Si no hubo error, calculamos la duración total de la llamada exitosa.
        duration_ms = round((perf_counter() - start) * 1000, 2)

        tool_event = build_tool_event(
            tool=tool_name,
            status="success",
            duration_ms=duration_ms,
            request_id=request_id,
        )
        logger.info(tool_event)

        # Devolvemos el resultado original para no alterar el comportamiento
        # normal de la herramienta, solo enriquecerlo con observabilidad.
        return result
