import os
from dataclasses import dataclass

@dataclass
class Settings:
    port: int = 8000
    host: str = "127.0.0.1"
    transport: str = "stdio"



def load_settings() -> Settings:
    """Load settings from the .env file."""

    return Settings(
        port=int(os.getenv("PORT", Settings.port)),
        host=os.getenv("HOST", Settings.host),
        transport=os.getenv("TRANSPORT", Settings.transport),
    )