from typing import Any
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI(
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request, name: str = "World") -> Any:
    context = {"name": name}
    return templates.TemplateResponse(
        request=request,
        name="root.html",
        context=context,
    )
