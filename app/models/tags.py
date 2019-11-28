from pydantic import BaseModel, Field


class BaseTag(BaseModel):
    tag_type: str = Field(...)
    value: str = Field(...)


class TagIn(BaseTag):
    pass
