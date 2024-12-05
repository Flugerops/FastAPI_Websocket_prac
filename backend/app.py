from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, Request, WebSocketDisconnect
from uvicorn import run as run_asgi

from utils import ConnectionManager


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.connection_manager = ConnectionManager()
    yield


app = FastAPI(lifespan=lifespan)


@app.websocket("/ws/{room_id}")
async def chess_room(websocket: WebSocket, room_id: int):
    connection_manager = app.state.connection_manager
    await connection_manager.connect(websocket, room_id)
    try:
        while True:
            data = await websocket.receive_json()
            print(data)
            await connection_manager.broadcast(room_id, data)

    except WebSocketDisconnect:
        connection_manager.disconnect(websocket, room_id)
        await connection_manager.broadcast(room_id, {"Message": "Player left the game"})


if __name__ == "__main__":
    run_asgi(app=app)
