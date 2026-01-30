from typing import Any
from fastapi import FastAPI
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
async def head_root() -> str:
    return ""


@app.get("/")
async def read_root(render: RendererDep, name: str = "World") -> Any:
    return render(
        "root.html",
        name=name,
    )
