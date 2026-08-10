from fastmcp import Client
from fastmcp.client.auth import OAuth
import asyncio

# TU_CLIENT_ID_DE_AUTH0 = "dIJTmb5sGNaHthqQGZaWG9gNSKGWBTA7"

# oauth = OAuth(
#     client_id="dIJTmb5sGNaHthqQGZaWG9gNSKGWBTA7",
#     callback_port=8080,  # <- Fuerza que el callback sea http://localhost:8080/callback
#     scopes=["openid", "access:mcp"],
# )

access_token = "....iX4v4ZzHl1v56TLi0yfLz8eCs------......." # asi por ahora, luego se puede usar el flujo de OAuth para obtenerlo dinámicamente

async def main():
    
    # The client will automatically handle Auth0 OAuth flows
    async with Client("http://localhost:8000/mcp", auth=access_token) as client:
        # First-time connection will open Auth0 login in your browser
        print("✓ Authenticated with Auth0!")

        # Test the protected tool
        result = await client.call_tool("admin_operation")
        # token_info = result.data
        print(f"Auth0 token info: {result }")

if __name__ == "__main__":
    asyncio.run(main())