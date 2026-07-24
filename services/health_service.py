import aiosqlite

from core.tracing import trace_service

class HealthService:
    def __init__(self, db_conn: aiosqlite.Connection):
        self.db_conn = db_conn

    @trace_service
    async def check(self) -> dict: 

        try:
            await self.db_conn.execute("SELECT 1")

            return {
                "status": "healthy",
                "sqlite": True,
            }

        except Exception:
            return {
                "status": "unhealthy",
                "sqlite": False,
            }