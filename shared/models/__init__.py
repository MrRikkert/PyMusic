from pydantic import BaseModel


class CustomBaseModel(BaseModel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for k in args:
            setattr(self, k, args[k])

    def __getitem__(self, item):
        return getattr(self, item)
