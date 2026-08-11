from datetime import datetime, timezone
import logging
import json

class JsonFormatter(logging.Formatter):
    def format(
        self,
        record: logging.LogRecord # el mensaje que se va a loguear, con toda su metadata (timestamp, level, etc)
    ) -> str:

        base_event = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
        }

        # Si el mensaje es un diccionario, lo integramos directamente en el evento base para que quede toda la info estructurada y fácil de parsear
        if isinstance(record.msg, dict):
            base_event.update(
                record.msg
            )

        else:

            base_event["message"] = record.getMessage()

        return json.dumps(
            base_event,
            ensure_ascii=False
        )


# creo un archivo para guardar mis logs
logger = logging.getLogger("mcp_server")
logger.setLevel(logging.INFO)

if not logger.handlers:
    handler = logging.StreamHandler() # Se emiten los logs en la consola para que asi la infraestructura de despliegue (docker, kubernetes, etc) pueda capturarlos y redirigirlos a donde corresponda (archivos, servicios de log, etc)

    formatter = JsonFormatter() # para que mis logs se guarden en formato json y sean mas faciles de parsear y analizar

    handler.setFormatter(formatter)
    logger.addHandler(handler)
