from dataclasses import dataclass
from typing import Any, Optional


__all__ = 'VKResponseBase'


@dataclass
class VKResponseBase:
    response: Optional[Any]
    error: Optional[Any]
    execute_errors: Optional[Any]
