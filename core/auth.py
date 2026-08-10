from fastmcp.server.auth.providers.jwt import JWTVerifier

from config.settings import Settings


def create_auth_provider(settings: Settings) -> JWTVerifier:
    return JWTVerifier(
        issuer=settings.auth_issuer,
        jwks_uri=settings.jwks_uri,
        audience=settings.auth_audience,
        required_scopes=["access:mcp"],
        base_url=settings.auth_base_url,
    )