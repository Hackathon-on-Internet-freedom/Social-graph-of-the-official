from dataclasses import dataclass
from typing import List, Optional

from marshmallow_dataclass import class_schema

from social_graph.schemas.models import VKUserWithFields
from social_graph.schemas.responses import VKResponse


__all__ = [
    'VKProcedureResponsePayload', 'VKProcedureResponse',
    'VKProcedureResponseSchema', 'VKProcedureResponsePayloadSchema'
]


@dataclass
class VKProcedureResponsePayload:
    user_info: Optional[VKUserWithFields]
    num_friends: Optional[int]
    friends_info: Optional[List[VKUserWithFields]]
    error_info: Optional[str]


@dataclass
class VKProcedureResponse(VKResponse):
    response: Optional[VKProcedureResponsePayload]


VKProcedureResponseSchema = class_schema(VKProcedureResponse)
VKProcedureResponsePayloadSchema = class_schema(VKProcedureResponsePayload)
