from typing import Any
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def read_root(name: str = "World") -> Any:
    return {"message": f"Hello {name}"}
