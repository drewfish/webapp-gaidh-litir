from typing import Any
from urllib.parse import urlunsplit
import datetime
import os
import traceback
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

_COLORS: dict[str, str] = {
    "blue": "34",
    "green": "32",
    "grey": "1;30",
    "red": "31",
    "yellow": "33",
}
_NO_COLOR = os.getenv("RENDER", "") == "true"


def _color(color: str, raw: str) -> str:
    if _NO_COLOR:
        return raw
    code = _COLORS.get(color, "")
    if not code:
        return raw
    return f"\033[{code}m" + raw + "\033[0m"


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    based roughly on
        https://oneuptime.com/blog/post/2026-01-27-fastapi-logging/view
        #custom-logging-middleware-for-requests
    """

    async def dispatch(self, request: Request, call_next: Any) -> Any:
        req_start = datetime.datetime.now(datetime.UTC)
        client_ip = request.client.host if request.client else "unknown"
        conn_type = request.scope.get("type", {})
        asgi_version = request.scope.get("asgi", {}).get("version", "")
        proto = conn_type + "/" + asgi_version
        method = request.method
        path = urlunsplit(("", "", request.url.path, request.url.query, ""))
        referer = request.headers.get("referer", "")

        def _log(res_end: datetime.datetime, status_code: int) -> None:
            start = req_start.isoformat(timespec="milliseconds").replace("+00:00", "Z")
            duration_ms = int((res_end - req_start).total_seconds() * 1000)
            code = str(status_code)
            if status_code < 200:
                code = _color("blue", code)
            elif status_code < 300:
                code = _color("green", code)
            elif status_code < 400:
                code = _color("grey", code)
            elif status_code < 500:
                code = _color("yellow", code)
            else:
                code = _color("red", code)
            print(
                "REQUEST",
                _color("grey", start),
                f"{duration_ms:4}",
                method,
                code,
                path,
                _color("grey", client_ip),
                proto,
                _color("grey", referer),
            )

        try:
            response = await call_next(request)
            res_end = datetime.datetime.now(datetime.UTC)
            _log(res_end, response.status_code)
        except Exception as exc:
            res_end = datetime.datetime.now(datetime.UTC)
            _log(res_end, 500)
            print("EXCEPTION", type(exc).__name__, str(exc), traceback.format_exc())
            return JSONResponse(
                status_code=500, content={"error": "internal server error"}
            )
        return response
