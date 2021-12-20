from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from starlette.datastructures import State
from uvicorn.main import logger
from websockets.exceptions import ConnectionClosedError
import asyncio

router = APIRouter()


@router.websocket("/connect")
async def websocket_endpoint(websocket: WebSocket):
    await State.manager.connect(websocket)
    if State.job:
        await State.manager.send_personal_message({
            "ok": True,
            "data": State.job
            }, websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        await State.manager.disconnect(websocket)
        logger.info(
            f"{websocket.scope['client']} - Websocket Client [close connection]")
    except ConnectionClosedError:
        await State.manager.disconnect(websocket)
        logger.info(
            f"{websocket.scope['client']} - Websocket Client [close connection]")
