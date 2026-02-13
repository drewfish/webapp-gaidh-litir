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
    return render(
        "geama/v2-liosta-fhaclan.html",
        game_data=game_data,
        ath_shuidhich_geama=ath_shuidhich,
    )


@router.get("/v2-liosta-fhaclan")
async def v2_liosta_fhaclan(render: RendererDep, request: Request) -> Any:
    ath_shuidhich: str = "false"
    if "reset" in request.query_params:
        ath_shuidhich = "true"
    if "ath-shuidhich" in request.query_params:
        ath_shuidhich = "true"
    game_data: Any = {
        "error": "failed to load game data",
    }
    # tz = zoneinfo.ZoneInfo("America/Los_Angeles")
    # today = datetime.datetime.now(tz=tz).strftime("%Y-%m-%d")
    today = "2026-02-11"  # sàr-mhath
    # today = "2026-02-12";   # sradagach -- no hyphen in cuimsean
    # today = "2026-02-13";   # dearrasan -- hyphen in cuimsean
    # today = "2026-02-14";   # fiùbhaidh -- no hyphen in cuimsean
    game_file = os.path.join(
        DATA_DIR,
        f"geama/liosta-fhaclan/{today}-geama-liosta-fhaclan.json",
    )
    if os.path.isfile(game_file):
        with open(game_file, encoding="utf-8") as file:
            game_data = json.load(file)
    else:
        print("MISSING game data file --", game_file)
    return render(
        "geama/v2-liosta-fhaclan.html",
        game_data=game_data,
        ath_shuidhich_geama=ath_shuidhich,
    )
