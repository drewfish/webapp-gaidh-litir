from typing import Any
import json
from fastapi import APIRouter, Request

router = APIRouter(prefix="/api/v1")


@router.post("/debug")
async def debug(request: Request) -> Any:
    payload = await request.json()
    print("--DEBUG-REMOTE--", json.dumps(payload, indent=2))
    return ""
