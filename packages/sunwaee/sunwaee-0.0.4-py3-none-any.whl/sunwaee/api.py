# standard
# third party
import fastapi

# custom
from sunwaee.aegen._api._router import aegen_router

app = fastapi.FastAPI(
    title="Sunwæe API",
    summary="The almost-everything API.",
    version="0.0.1",
)

app.include_router(aegen_router)
