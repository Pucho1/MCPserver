from dataclasses import dataclass
from typing import FrozenSet


@dataclass(frozen=True, slots=True)
class AuthenticatedUser:
    subject: str
    issuer: str
    audience: str
    scopes: FrozenSet[str]