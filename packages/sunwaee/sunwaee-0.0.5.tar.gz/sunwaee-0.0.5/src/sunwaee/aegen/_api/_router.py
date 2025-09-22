# standard
# third party
import fastapi

# custom

aegen_router = fastapi.APIRouter(prefix="/aegen", tags=["aegen"])

from . import completion
from . import agents
from . import models
from . import providers
