from pathlib import Path
from typing import Annotated
from uuid import UUID, uuid4

from fastapi import Cookie, FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from .game_manager import GameManager
from .messages import Message

app = FastAPI()

manager = GameManager()
static_dir = Path(__file__).parent.parent / "ui" / "dist"
app.mount("/play", StaticFiles(directory=static_dir, html=True))


@app.get("/")
async def root(client_id: Annotated[str | None, Cookie()] = None):
    return RedirectResponse("/play")


@app.get("/favicon.ico")
async def favicon():
    return RedirectResponse("/play/favicon.ico")


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    client_id: Annotated[str | None, Cookie()] = None,
):
    if client_id is None or UUID(client_id) not in manager.known_clients:
        cid = uuid4()
        await manager.connect(websocket, cid)
        await manager.send(
            Message.set_cookie(name="client_id", value=str(cid)),
            cid,
        )
    else:
        cid = UUID(client_id)
        await manager.connect(websocket, cid)

    try:
        while True:
            data = await websocket.receive_json()
            await manager.handle_message(Message(**data), cid)
    except WebSocketDisconnect:
        manager.disconnect(cid)
