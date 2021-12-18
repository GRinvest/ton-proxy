import asyncio

from fastapi import FastAPI
from starlette.datastructures import State
from uvicorn.main import logger

from api.views import router as router_api
from tasks import core
from wss import connector
from wss.views import router as router_wss

app = FastAPI(
    title="API endpoints for Ton miner",
    description=f"Proxy server for Ton miner",
    version="1.0"
)
app.include_router(router_api, prefix='/api')
app.include_router(router_wss, prefix='/ws')


@app.on_event("startup")
async def startup() -> None:
    State.giver = State.args.giver
    if State.giver == 'auto':
        State.task_auto = asyncio.create_task(core.task_auto())
    State.task_job = asyncio.create_task(core.task_job())
    State.manager = connector.ConnectionManager()


@app.on_event("shutdown")
async def shutdown() -> None:
    task_job = State.task_job
    task_job.cancel()
    try:
        await task_job
    except asyncio.CancelledError:
        logger.info("Task job is cancelled now")
    if State.args.giver == 'auto':
        task_auto = State.task_auto
        task_auto.cancel()
        try:
            await task_auto
        except asyncio.CancelledError:
            logger.info("Task auto is cancelled now")
