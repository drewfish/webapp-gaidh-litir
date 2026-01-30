from typing import Annotated, Any
from fastapi import Depends, Request
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")
TemplateResponse = Any


def get_renderer(request: Request) -> Any:
    def _render_template(template_name: str, **kwargs: Any) -> Any:
        return templates.TemplateResponse(
            request=request,
            name=template_name,
            context=kwargs,
        )

    return _render_template


RendererDep = Annotated[Any, Depends(get_renderer)]
