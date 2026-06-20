from fastmcp.server.middleware import (
    Middleware,
    MiddlewareContext
)

from dataclasses import dataclass
from datetime import datetime


@dataclass
class SessionRateLimit:
    count: int
    reset_at: datetime
    last_seen: datetime


class RateLimitMiddleware(Middleware):

    def __init__(
        self,
        requests_per_minute: int = 100,
    ):
        self.requests_per_minute = requests_per_minute
        self.sessions: dict[str, SessionRateLimit] = {}


    async def on_request(self, context, call_next):
        session_id = context.message.session_id
        
        print(f"Session ID=======>: {session_id}")

        if session_id not in self.sessions:
            self.sessions[session_id] = SessionRateLimit(count=0, reset_at=datetime.now(), last_seen=datetime.now())
        else:
            self.sessions[session_id].last_seen = datetime.now()
        return await super().on_request(context, call_next)