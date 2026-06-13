from fastmcp.server.dependencies import get_http_headers 

class AuthMiddleware:

    headers = get_http_headers()
    authorization = headers.get("authorization")