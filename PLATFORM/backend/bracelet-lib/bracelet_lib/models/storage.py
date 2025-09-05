from pydantic import Field, validator
from typing import Optional, List
from bracelet_lib.models.common import CustomBaseModel


class BlobOpType:
    put                = 'put'
    delete             = 'delete'
    post               = 'post'
    get                = 'get'


class SignedUrlRequest(CustomBaseModel):
    class PostSignedUrlRequest(CustomBaseModel):
        filename   : str                         = Field(..., example='video20220702.mp4')
        num_parts  : int                         = Field(..., example=1)
        id         : Optional[int]               = Field(None, example=2605)

        # noinspection PyMethodParameters
        @validator('num_parts')
        def valid_num_parts(cls, v):
            if v < 1:
                raise ValueError("Parts number must be higher than 0")

            return v

    class PutSignedUrlRequest(CustomBaseModel):
        filename   : str                         = Field(..., example='video20220702.mp4')
        num_parts  : int                         = Field(..., example=1)

        # noinspection PyMethodParameters
        @validator('num_parts')
        def valid_num_parts(cls, v):
            if v < 1:
                raise ValueError("Parts number must be higher than 0")

            return v


class SignedUrlResponse(CustomBaseModel):
    class GetSignedUrlResponse(CustomBaseModel):
        display_url  : str                       = Field(..., example='https://www.aws.com/video2022.mp4')

    class DeleteSignedUrlResponse(CustomBaseModel):
        delete_url   : str                       = Field(..., example='https://www.aws.com/video2022.mp4')

    class PostSignedUrlResponse(CustomBaseModel):
        reserved_id  : Optional[str]             = Field(None, example=2605)
        upload_id    : Optional[str]             = Field(None, example='5342fsf2342ASDF2')
        urls         : List[str]                 = Field(..., example=['https://www.aws.com/video2022.mp4'])
        display_url  : str                       = Field(..., example='https://www.aws.com/video2022.mp4')
        delete_url   : str                       = Field(..., example='https://www.aws.com/video2022.mp4')
        complete_url : Optional[str]             = Field(None, example='https://www.aws.com/video2022.mp4')
        abort_url    : Optional[str]             = Field(None, example='https://www.aws.com/video2022.mp4')

    class PutSignedUrlResponse(CustomBaseModel):
        upload_id    : Optional[str]             = Field(None, example='5342fsf2342ASDF2')
        urls         : List[str]                 = Field(..., example=['https://www.aws.com/video2022.mp4'])
        display_url  : str                       = Field(..., example='https://www.aws.com/video2022.mp4')
        delete_url   : str                       = Field(..., example='https://www.aws.com/video2022.mp4')
        complete_url : Optional[str]             = Field(None, example='https://www.aws.com/video2022.mp4')
        abort_url    : Optional[str]             = Field(None, example='https://www.aws.com/video2022.mp4')
