from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

app = FastAPI()

@app.get("/confirm")
async def confirm():
    return "hello"

app.mount("/", StaticFiles(directory="public", html = True), name="static")
