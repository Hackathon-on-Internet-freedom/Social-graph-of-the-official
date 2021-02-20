from dataclasses import dataclass
from typing import Any, Optional

from marshmallow_dataclass import class_schema

__all__ = ['VKResponse', 'VKResponseSchema']


@dataclass
class VKResponse:
    response: Optional[Any]
    error: Optional[Any]
    execute_errors: Optional[Any]


VKResponseSchema = class_schema(VKResponse)
