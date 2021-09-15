from pydantic import Field
from shared.models import CustomBaseModel


class ArtistLastFm(CustomBaseModel):
    name: str = Field(...)

    class Config:
        orm_mode = True
