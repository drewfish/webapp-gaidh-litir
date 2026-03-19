from fastapi import FastAPI, Response
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from app import api_v1, geamaichean, innealan
from app.middleware import RequestLoggingMiddleware

from .eisimealachdan import RendererDep

app = FastAPI(
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
    default_response_class=HTMLResponse,
)
app.add_middleware(RequestLoggingMiddleware)
app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(api_v1.router)
app.include_router(geamaichean.router)
app.include_router(innealan.router)


@app.head("/")
def head_homepage() -> str:
    return ""


@app.get("/")
async def read_homepage(render: RendererDep) -> Response:
    return render("homepage.html")
