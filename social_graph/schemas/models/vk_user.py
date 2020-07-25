from dataclasses import dataclass, field
from typing import Optional, List, Any

from marshmallow.validate import OneOf, Range
from marshmallow_dataclass import class_schema


@dataclass
class VKUser:
    id_: int = field(metadata=dict(data_key='id'))
    first_name: str
    last_name: str
    deactivated: Optional[str] = field(metadata=dict(
        validate=OneOf(('deleted', 'banned'))
    ))
    is_closed: bool
    can_access_closed: bool


@dataclass
class VKUserFieldRelative:
    id_: int = field(metadata=dict(data_key='id'))
    name: str
    type_: str = field(metadata=dict(
        data_key='type',
        validate=OneOf((
            'child', 'sibling', 'parent', 'grandparent', 'grandchild'
        )),
    ))


@dataclass
class VKUserSchool:
    id_: Optional[int] = field(metadata=dict(data_key='id'))
    country: Optional[int]
    city: Optional[int]
    name: Optional[str]
    year_from: Optional[int]
    year_to: Optional[int]
    year_graduated: Optional[int]
    class_: Optional[str] = field(metadata=dict(data_key='class'))
    speciality: Optional[str]
    type: Optional[int] = field(metadata=dict(validate=Range(min=0, max=13)))
    type_str: Optional[str]


@dataclass
class VKUserUniversity:
    id_: Optional[int] = field(metadata=dict(data_key='id'))
    country: Optional[int]
    city: Optional[int]
    name: Optional[str]
    faculty: Optional[int]
    faculty_name: Optional[str]
    chair: Optional[int]
    chair_name: Optional[str]
    graduation: Optional[int]
    education_form: Optional[str]
    education_status: Optional[str]


@dataclass
class VKUserMilitary:
    unit: Optional[str]
    unit_id: Optional[int]
    country_id: Optional[int]
    from_: Optional[int] = field(metadata=dict(data_key='from'))
    until: Optional[int]


@dataclass
class VKUserCareer:
    group_id: Optional[int]
    company: Optional[str]
    country_id: Optional[int]
    city_id: Optional[int]
    city_name: Optional[str]
    from_: Optional[int] = field(metadata=dict(data_key='from'))
    until: Optional[int]
    position: Optional[str]


@dataclass
class VKUserWithFields(VKUser):
    screen_name: Optional[str]
    maiden_name: Optional[str]
    relatives: Optional[List[VKUserFieldRelative]]

    relation: Optional[int] = field(
        metadata=dict(validate=Range(min=0, max=8))
    )
    # ``relation_partner`` depends on ``relation`` field
    relation_partner: Optional['VKUser']

    home_town: Optional[str]
    schools: Optional[List[VKUserSchool]]
    universities: Optional[List[VKUserUniversity]]
    military: Optional[List[VKUserMilitary]]
    career: Optional[List[VKUserCareer]]
    counters: Optional[Any]


VKUserSchema = class_schema(VKUser)
VKUserWithFieldsSchema = class_schema(VKUserWithFields)
