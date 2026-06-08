from core.logger import logger
import httpx


class PostService:

    base_route= "https://jsonplaceholder.typicode.com/posts/"

    def __init__(self, http_client):
        self.http_client = http_client


    async def get_post(self, post_id: int) -> dict:

        try:

            response_api = await self.http_client.get(
                f"{self.base_route}{post_id}", timeout=10.0
            )


            if response_api.status_code != 200:
                logger.error(f"Error fetching post with id {post_id}: {response_api.status_code}")
                raise httpx.HTTPError(f"Error fetching post with id {post_id}: {response_api.status_code}")
            
            payload = response_api.json()

            response = { "body": payload.get("body"),  "title": payload.get("title") }

        except httpx.TimeoutException:
            logger.error(f"Error: Timeout when fetching post with id {post_id}")

            raise httpx.TimeoutException(f"Timeout when fetching post with id {post_id}")

        except httpx.ConnectError:
            logger.error(f"Error: Connection error when fetching post with id {post_id}")

            raise httpx.ConnectError(f"Connection error when fetching post with id {post_id}")

        except Exception as e:
            logger.error(f"Error: Unexpected error when fetching post with id {post_id} - {str(e)}")

            raise Exception(f"Unexpected error when fetching post with id {post_id} - {str(e)}")
        
        return response