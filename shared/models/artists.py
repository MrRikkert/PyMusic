from pydantic import BaseModel, Field


class ArtistLastFm(BaseModel):
    name: str = Field(...)

    class Config:
        orm_mode = True
