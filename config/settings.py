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
    db_path: str = "notes.db"
    LANGFUSE_SECRET_KEY: str = "change-me"
    LANGFUSE_PUBLIC_KEY: str = "change-me"
    LANGFUSE_BASE_URL: str = "https://cloud.langfuse.com"
    auth_audience: str = "your-audience"
    auth_issuer: str = "https://your-issuer.com/"
    # jwt_options = { "verify_signature": True}
    auth_jwks_url: str = "https://your-issuer.com/.well-known/jwks.json"  # URL to fetch JWKS for token verification

def load_settings() -> Settings:
    """Load settings from the .env file."""

    # Override default settings with environment variables if they exist. 
    return Settings(
        port=int(os.getenv("PORT", Settings.port)),
        host=os.getenv("HOST", Settings.host),
        transport=os.getenv("TRANSPORT", Settings.transport),
        api_key=os.getenv("MCP_API_KEY", Settings.api_key),
        db_path=os.getenv("DB_PATH", Settings.db_path),
        LANGFUSE_SECRET_KEY=os.getenv("LANGFUSE_SECRET_KEY", Settings.LANGFUSE_SECRET_KEY),
        LANGFUSE_PUBLIC_KEY=os.getenv("LANGFUSE_PUBLIC_KEY", Settings.LANGFUSE_PUBLIC_KEY),
        LANGFUSE_BASE_URL=os.getenv("LANGFUSE_BASE_URL", Settings.LANGFUSE_BASE_URL),
        auth_audience=os.getenv("AUTH_AUDIENCE", Settings.auth_audience),
        auth_issuer=os.getenv("AUTH_ISSUER", Settings.auth_issuer),
        auth_jwks_url=os.getenv("AUTH_JWKS_URL", Settings.auth_jwks_url),
        # jwt_options={
        #     "verify_signature": os.getenv("JWT_VERIFY_SIGNATURE", "True").lower() in ("true", "1", "t")
        # }
    )