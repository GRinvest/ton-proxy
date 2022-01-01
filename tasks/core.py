import asyncio

from liteclient import LiteClient
from starlette.datastructures import State
from uvicorn.main import logger

GIVERS = {
    'Ef-kkdY_B7p-77TLn2hUhM6QidWrrsl8FYWCIvBMpZKprKDH': 'PoW Giver 1',
    'Ef8SYc83pm5JkGt0p3TQRkuiM58O9Cr3waUtR9OoFq716uj0': 'PoW Giver 2',
    'Ef-FV4QTxLl-7Ct3E6MqOtMt-RGXMxi27g4I645lw6MTWg0f': 'PoW Giver 3',
    'Ef_NSzfDJI1A3rOM0GQm7xsoUXHTgmdhN5-OrGD8uwL2JHBa': 'PoW Giver 4',
    'Ef8gf1PQy4u2kURl-Gz4LbS29eaN4sVdrVQkPO-JL80VhFww': 'PoW Giver 5',
    'Ef8kO6K6Qh6YM4ddjRYYlvVAK7IgyW8Zet-4ZvNrVsmQ4PgP': 'PoW Giver 6',
    'Ef-P_TOdwcCh0AXHhBpICDMxStxHenWdLCDLNH5QcNpwMMn2': 'PoW Giver 7',
    'Ef91o4NNTryJ-Cw3sDGt9OTiafmETdVFUMvylQdFPoOxInls': 'PoW Giver 8',
    'Ef9iWhwk9GwAXjtwKG-vN7rmXT3hLIT23RBY6KhVaynRrDkx': 'PoW Giver 9',
    'Ef8JfFUEJhhpRW80_jqD7zzQteH6EBHOzxiOhygRhBdt44YH': 'PoW Giver 10'
}


class Miner(LiteClient):

    async def result_pow_params(self, powAddr) -> dict:
        result = await self.get_pow_params(powAddr)
        if result.get('seed', False):
            result["giver"] = powAddr
            return result
        return False

    async def best_giver(self) -> str:
        best_pow = list(GIVERS.keys())[0]
        best_complexity = 0
        for giver in GIVERS.keys():
            params = await self.result_pow_params(giver)
            if params:
                if best_complexity == 0:
                    best_complexity = params["complexity"]
                    best_pow = giver
                if params["complexity"] > best_complexity:
                    best_pow = giver
                    best_complexity = params["complexity"]
        return best_pow


async def task_job() -> None:
    logger.info("Run task_job()")
    miner = Miner(State.args.liteclient, State.args.config)
    State.job = {}
    while True:
        if State.giver != 'auto' and State.run_auto is False:
            State.run_job = True
            result = await miner.result_pow_params(State.giver)
            if result and result['seed'] != State.job.get('seed', ''):
                State.job.update(result)
                await State.manager.broadcast(result)
                logger.info(f"| {GIVERS[State.giver]} | New job: {hex(result['seed'])[2:]} Giver: {State.giver}")
            State.run_job = False
            await asyncio.sleep(9)
        await asyncio.sleep(1)


async def task_auto() -> None:
    logger.info("Run task_auto()")
    miner = Miner(State.args.liteclient, State.args.config)
    await asyncio.sleep(2)
    while True:
        State.run_auto = True
        result = await miner.best_giver()
        if State.giver != result:
            State.giver = result
            logger.info(f"New Best Giver: {State.giver}")
        State.run_auto = False
        await asyncio.sleep(60)


async def task_last() -> None:
    logger.info("Run task_last()")
    miner = Miner(State.args.liteclient, State.args.config)
    while True:
        if State.run_job is False and State.run_auto is False:
            await miner.get_last()
        await asyncio.sleep(2)
