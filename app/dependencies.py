from collections.abc import Callable
from typing import Annotated, Any
import json
import os
from fastapi import Depends, Request, Response
from fastapi.templating import Jinja2Templates

from .seorsachan import Clàran

templates = Jinja2Templates(directory="templates", autoescape=True)
templates.env.filters["json"] = lambda v: json.dumps(v)

DATA_DIR = os.environ.get(
    "GAIDH_LITIR_DATA_DIR",
    os.path.abspath(os.path.dirname(__file__) + "/../data"),
)
FAIDHLE_CLÀRAN = f"{DATA_DIR}/inneal/clàran-v1.json"

_CLÀRAN: Clàran = []


def get_clàran() -> Clàran:
    global _CLÀRAN, FAIDHLE_CLÀRAN
    if not _CLÀRAN:
        with open(FAIDHLE_CLÀRAN, encoding="utf-8") as faidhle:
            _CLÀRAN = json.load(faidhle)
    return _CLÀRAN


def get_renderer(request: Request) -> Callable[[str], Response]:
    def _render_template(template_name: str, /, **kwargs: Any) -> Response:
        return templates.TemplateResponse(
            request=request,
            name=template_name,
            context=kwargs,
        )

    return _render_template


ClàranDep = Annotated[Any, Depends(get_clàran)]
RendererDep = Annotated[Any, Depends(get_renderer)]
