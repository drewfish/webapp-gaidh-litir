#!/usr/bin/env python3

import datetime
import os
import os.path
import zoneinfo

DATA_DIR = os.environ.get(
    "GAIDH_LITIR_DATA_DIR",
    os.path.abspath(os.path.dirname(__file__) + "/../data"),
)
GAME_DATA_DIR = os.path.join(DATA_DIR, "geama/liosta-fhaclan")


def main() -> None:
    print("--START--")
    tz = zoneinfo.ZoneInfo("America/Los_Angeles")
    today = datetime.datetime.now(tz=tz).strftime("%Y-%m-%d")
    doomed: list[str] = []
    for file_name in os.listdir(GAME_DATA_DIR):
        if not file_name.endswith("-geama-liosta-fhaclan.json"):
            continue
        if file_name < today:
            doomed.append(file_name)
    for file_name in sorted(doomed):
        file_path = os.path.join(GAME_DATA_DIR, file_name)
        print("--DELETING--", file_path)
        os.remove(file_path)
    print("--DONE--")


if __name__ == "__main__":
    main()
