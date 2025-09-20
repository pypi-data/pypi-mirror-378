from ..._models import BaseModel

__all__ = ["Translation"]


class Translation(BaseModel):
    text: str
