from typing import Any
import datetime
import json
import os.path
import zoneinfo
from fastapi import APIRouter, Request

from .dependencies import DATA_DIR, RendererDep

router = APIRouter()


@router.get("/liosta-fhaclan")
async def liosta_fhaclan(render: RendererDep, request: Request) -> Any:
    ath_shuidhich: str = "false"
    if "reset" in request.query_params:
        ath_shuidhich = "true"
    if "ath-shuidhich" in request.query_params:
        ath_shuidhich = "true"
    game_data: Any = {
        "error": "failed to load game data",
    }
    tz = zoneinfo.ZoneInfo("America/Los_Angeles")
    today = datetime.datetime.now(tz=tz).strftime("%Y-%m-%d")
    game_file = os.path.join(
        DATA_DIR,
        f"geama/liosta-fhaclan/{today}-geama-liosta-fhaclan.json",
    )
    if os.path.isfile(game_file):
        with open(game_file, encoding="utf-8") as file:
            game_data = json.load(file)
    else:
        print("MISSING game data file --", game_file)
    cuimsean = game_data.pop("cuimsean", [])
    game_data["cunntadh_cuimsean"] = len(cuimsean)
    return render(
        "geama/liosta-fhaclan.html",
        game_data=game_data,
        cuimsean=cuimsean,
        ath_shuidhich_geama=ath_shuidhich,
    )
