from dataclasses import dataclass
from typing import List

from social_graph.schemas.models import VKUser


@dataclass
class VKProcedureResponse:
    user_info: VKUser
    num_friends: int
    friends_user_info: List[VKUser]
