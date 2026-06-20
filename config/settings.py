import os
from dataclasses import dataclass
from dotenv      import load_dotenv


load_dotenv()

@dataclass
class Settings:
    port: int = 8000
    host: str = "127.0.0.1"
    transport: str = "stdio"
    api_key: str = "change-me"
    requests_per_minute: int = 100  # Default rate limit for RateLimitMiddleware



def load_settings() -> Settings:
    """Load settings from the .env file."""

    # Override default settings with environment variables if they exist. 
    return Settings(
        port=int(os.getenv("PORT", Settings.port)),
        host=os.getenv("HOST", Settings.host),
        transport=os.getenv("TRANSPORT", Settings.transport),
        api_key=os.getenv("MCP_API_KEY", Settings.api_key),
    )