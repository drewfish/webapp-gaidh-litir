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
FAIDHLE_FACLAN = f"{DATA_DIR}/inneal/faclan-v2.json"

_FACLAN: Clàran = []


def get_faclan() -> Clàran:
    global _FACLAN, FAIDHLE_FACLAN
    if not _FACLAN:
        with open(FAIDHLE_FACLAN, encoding="utf-8") as faidhle:
            _FACLAN = json.load(faidhle)
    return _FACLAN


def get_renderer(request: Request) -> Callable[[str], Response]:
    def _render_template(template_name: str, /, **kwargs: Any) -> Response:
        return templates.TemplateResponse(
            request=request,
            name=template_name,
            context=kwargs,
        )

    return _render_template


FaclanDep = Annotated[Any, Depends(get_faclan)]
RendererDep = Annotated[Any, Depends(get_renderer)]
