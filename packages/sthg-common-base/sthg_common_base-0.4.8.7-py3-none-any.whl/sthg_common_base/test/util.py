from sthg_common_base.response.httpCodeEnum import ResponseEnum
from sthg_common_base.response.response import BaseResponse

fields = [
    {'field_name': 'ad_date', 'field_type': 'DATE', 'is_nullable': False, 'is_primary_key': False, 'is_unique': False, 'is_indexed': False},
    {'field_name': 'ad_id', 'field_type': 'INTEGER', 'is_nullable': False, 'is_primary_key': False, 'is_unique': False, 'is_indexed': False},
    {'field_name': 'impressions', 'field_type': 'INTEGER', 'is_nullable': True, 'is_primary_key': False, 'is_unique': False, 'is_indexed': False},
    {'field_name': 'clicks', 'field_type': 'INTEGER', 'is_nullable': True, 'is_primary_key': False, 'is_unique': False, 'is_indexed': False},
    {'field_name': 'conversions', 'field_type': 'INTEGER', 'is_nullable': True, 'is_primary_key': False, 'is_unique': False, 'is_indexed': False}
]

BaseResponse(ResponseEnum.OK,fields)