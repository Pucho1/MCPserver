from jwt import PyJWKClient
import jwt

from config.settings import Settings
from middleware.security.models import AuthenticatedPrincipal

from middleware.security.exceptions import AuthenticationError, InvalidTokenError

# 1. Leer el JWT.
# 2. Verificar la firma.
# 3. Validar issuer.
# 4. Validar audience.
# 5. Validar expiración.
# 6. Construir AuthenticatedPrincipal.


class TokenVerifier:

    def __init__(self, settings: Settings):
        self._settings    = settings
        self._jwks_client = PyJWKClient(settings.auth_jwks_url) # Clinete para obtener las claves públicas desde el JWKS endpoint

   
    def verify(self, token: str) -> AuthenticatedPrincipal:

        # Debe devolver un objeto de nuestro dominio que represente la entidad autenticada, por ejemplo AuthenticatedPrincipal.

        try:
            # Obtengo la clave pública que utilizamos para verificar el tokent enviado por el cliente.....
            # ..... las saca del Kid en el header y busca el los archivo  publicoas de JWKS.
            signing_key = self._jwks_client.get_signing_key_from_jwt(token)

            claims = self._decode_token(token, signing_key)
            
        except jwt.ExpiredSignatureError as e:
            raise AuthenticationError("Token expired") from e
        
        except jwt.InvalidTokenError as e:
            raise InvalidTokenError("Invalid token") from e


        return self._build_authenticated_principal(claims)

    def _decode_token(self, token: str, signing_key) -> dict:

        # Convierte la cadena de texto ilegible del token de vuelta a un objeto
        # Usa la clave pública (signing_key.key) y el algoritmo (RS256) para asegurarse de que nadie manipuló el token en el camino.
        # Comprueba automáticamente que el token no esté expirado, que venga del emisor correcto (issuer) y que esté dirigido a tu servidor (audience).
        return jwt.decode(
            token,
            signing_key.key,
            algorithms  = ["RS256"],
            audience    = self._settings.auth_audience, # Verifica que el token sea para nuestra aplicación
            issuer      = self._settings.auth_issuer,
            options     = self._settings.jwt_options,
        )
        # devuelve el contenido interno (el payload)

    def _build_authenticated_principal(self, claims: dict) -> AuthenticatedPrincipal:
        return AuthenticatedPrincipal(
            subject  = claims["sub"],
            issuer   = claims["iss"],
            audience = claims["aud"],
            scopes   = frozenset(claims.get("scope", "").split()),
        )