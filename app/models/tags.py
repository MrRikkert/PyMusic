from pydantic import BaseModel, Schema


class BaseTag(BaseModel):
    tag_type: str = Schema(...)
    value: str = Schema(...)


class TagIn(BaseTag):
    pass
