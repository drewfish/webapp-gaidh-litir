from typing import Any
from fastapi import APIRouter

router = APIRouter(
    prefix="/gaema",
)


@router.get("/liosta-fhaclan")
async def liosta_fhaclan() -> Any:
    return "TODO"
