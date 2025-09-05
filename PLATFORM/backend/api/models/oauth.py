from typing import Optional

from pydantic import Field

from bracelet_lib.models.common import CustomBaseModel
from routes.common import StrEnum


class GrantTypeEnum(StrEnum):
    password      = 'password'
    refresh_token = 'refresh_token'


class ScopeEnum(StrEnum):
    full = 'full'
    room = 'room'


class OAuthTokenResponse(CustomBaseModel):
    access_token: str = Field(
        ...,
        example='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOjYsImlzcyI6Imh0dHBzOi8vYXBpLmxldGlxdWV0LmNvbSI'
                'sImV4cCI6MTU0MTg2MzM5NCwiaWF0IjoxNTM2Njc5Mzk0fQ.I1azA_RC5TGBwy6Nk8rTUoamfPdzmpazmaKkH6x74t4'
    )
    refresh_token: Optional[str] = Field(
        None,
        example='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOjYsImlzcyI6Imh0dHBzOi8vYXBpLmxldGlxdWV0LmNvbSI'
                'sImV4cCI6MTU0MTg2MzM5NCwiaWF0IjoxNTM2Njc5Mzk0fQ.I1azA_RC5TGBwy6Nk8rTUoamfPdzmpazmaKkH6x74t4'
    )
    expires_in: int = Field(
        ...,
        format='int32',
        minimum=0,
        example=3600
    )
    token_type: str = Field(
        ...,
        example='Bearer'
    )


class OAuthTokenRevoke(CustomBaseModel):
    token: str = Field(
        ...,
        example='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOjYsImlzcyI6Imh0dHBzOi8vYXBpLmxldGlxdWV0LmNvbSI'
                'sImV4cCI6MTU0MTg2MzM5NCwiaWF0IjoxNTM2Njc5Mzk0fQ.I1azA_RC5TGBwy6Nk8rTUoamfPdzmpazmaKkH6x74t4'
    )
