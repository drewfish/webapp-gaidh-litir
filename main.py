from typing import Any
import os
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def read_root(name: str = "World") -> Any:
    return {"message": f"Hello {name}"}

@app.get("/drew/debug")
def drew_debug() -> Any:
    return {
        "env": dict(os.environ)
    }
