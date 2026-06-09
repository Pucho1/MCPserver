from datetime import datetime
import logging
import json

class JsonFormatter(logging.Formatter):
     def format(
        self,
        record: logging.LogRecord # el mensaje que se va a loguear, con toda su metadata (timestamp, level, etc)
    ) -> str:

        base_event = {
            "timestamp": datetime.utcnow().isoformat(),
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
    handler = logging.FileHandler("server.log", encoding="utf-8")

    formatter = JsonFormatter() # para que mis logs se guarden en formato json y sean mas faciles de parsear y analizar

    handler.setFormatter(formatter)
    logger.addHandler(handler)


    # formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
