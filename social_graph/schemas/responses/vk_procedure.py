from dataclasses import dataclass
from typing import List, Optional

from marshmallow_dataclass import class_schema

from social_graph.schemas.models import VKUserWithFields
from social_graph.schemas.responses import VKResponseBase


__all__ = ['VKProcedureResponse', 'VKResponse', 'VKResponseSchema']


@dataclass
class VKProcedureResponse:
    user_info: VKUserWithFields
    num_friends: int
    friends_info: List[VKUserWithFields]


@dataclass
class VKResponse(VKResponseBase):
    response: Optional[VKProcedureResponse]


VKResponseSchema = class_schema(VKResponse)
