from pydantic import Field

from shared.models import CustomBaseModel


class BaseTag(CustomBaseModel):
    tag_type: str = Field(...)
    value: str = Field(...)


class TagIn(BaseTag):
    pass
