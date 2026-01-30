from collections.abc import Callable
from typing import Annotated, Any
from fastapi import Depends, Request, Response
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")


def get_renderer(request: Request) -> Callable[[str], Response]:
    def _render_template(template_name: str, /, **kwargs: Any) -> Response:
        return templates.TemplateResponse(
            request=request,
            name=template_name,
            context=kwargs,
        )

    return _render_template


RendererDep = Annotated[Any, Depends(get_renderer)]
