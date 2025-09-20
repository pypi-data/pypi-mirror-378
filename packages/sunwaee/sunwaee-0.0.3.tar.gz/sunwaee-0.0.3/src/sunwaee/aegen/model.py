# standard
# third party
from pydantic import BaseModel

# custom


class Model(BaseModel):
    name: str
    display_name: str
    origin: str
    version: str | None = None
