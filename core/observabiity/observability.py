def build_tool_event(
    tool: str,
    status: str,
    duration_ms: int | None = None,
    error: str | None = None,
    request_id: str | None = None
) -> dict:
    """
    Construye un evento de herramienta para su registro o envío a un sistema de observabilidad.
    """

    return {
        "request_id": request_id,
        "event": "tool_call",
        "tool": tool,
        "status": status,
        "duration_ms": duration_ms,
        "error": error,
    }