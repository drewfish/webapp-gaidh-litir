from fastapi import FastAPI, Response
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from app import gaemaichean

from .dependencies import RendererDep

app = FastAPI(
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
    default_response_class=HTMLResponse,
)
app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(gaemaichean.router)


@app.head("/")
def head_homepage() -> str:
    return ""


@app.get("/")
async def read_homepage(render: RendererDep) -> Response:
    return render("homepage.html")
