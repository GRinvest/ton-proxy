import asyncio
import json
from typing import Dict

from starlette.datastructures import State
from uvicorn.main import logger


async def Pars(text, search, search2=None):
    if search is None or text is None:
        return None
    if search not in text:
        return None
    text = text[text.find(search) + len(search):]
    if search2 is not None and search2 in text:
        text = text[:text.find(search2)]
    return text


class LiteClient:

    def __init__(self):
        self.app_path = State.args.liteclient
        self.config_path = State.args.сonfig

    async def run(self, cmd, timeout=2):
        args = ['--global-config', self.config_path,
                "--verbosity", "0", "--cmd", cmd]
        process = await asyncio.create_subprocess_exec(self.app_path, *args, stdin=asyncio.subprocess.PIPE, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.STDOUT)
        try:
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=timeout)
        except asyncio.exceptions.TimeoutError:
            logger.debug(f"Command {cmd} timed out")
        else:
            if stderr:
                logger.error(f"Error lite-client: {stderr.decode()}")
            else:
                return stdout.decode()
        finally:
            try:
                process.kill()
            except OSError:
                pass


class Miner:

    def __init__(self):
        self.lite_client = LiteClient()

    async def get_pow_params(self, powAddr):
        params = dict()
        cmd = f"runmethod {powAddr} get_pow_params"
        i = 1
        while True:
            result = await self.lite_client.run(cmd, i)
            if result:
                break
            i += 1
        data = await self.result_list(result)
        params["giver"] = powAddr
        params["seed"] = data[0]
        params["complexity"] = data[1]
        params["iterations"] = data[2]
        return params

    async def result_list(self, text):
        buff = await Pars(text, "result:", "\n")
        if buff is None or "error" in buff:
            return
        buff = buff.replace(')', ']')
        buff = buff.replace('(', '[')
        buff = buff.replace(']', ' ] ')
        buff = buff.replace('[', ' [ ')
        arr = buff.split()

        # Get good raw data
        output = ""
        arrLen = len(arr)
        for i in range(arrLen):
            item = arr[i]
            # get next item
            if i+1 < arrLen:
                nextItem = arr[i+1]
            else:
                nextItem = None
            # add item to output
            if item == '[':
                output += item
            elif nextItem == ']':
                output += item
            elif '{' in item or '}' in item:
                output += "\"{item}\", ".format(item=item)
            elif i+1 == arrLen:
                output += item
            else:
                output += item + ', '
        data = json.loads(output)
        return data

    async def best_giver(self):
        givers = ["kf-kkdY_B7p-77TLn2hUhM6QidWrrsl8FYWCIvBMpZKprBtN", "kf8SYc83pm5JkGt0p3TQRkuiM58O9Cr3waUtR9OoFq716lN-", "kf-FV4QTxLl-7Ct3E6MqOtMt-RGXMxi27g4I645lw6MTWraV", "kf_NSzfDJI1A3rOM0GQm7xsoUXHTgmdhN5-OrGD8uwL2JMvQ", "kf8gf1PQy4u2kURl-Gz4LbS29eaN4sVdrVQkPO-JL80VhOe6",
                  "kf8kO6K6Qh6YM4ddjRYYlvVAK7IgyW8Zet-4ZvNrVsmQ4EOF", "kf-P_TOdwcCh0AXHhBpICDMxStxHenWdLCDLNH5QcNpwMHJ8", "kf91o4NNTryJ-Cw3sDGt9OTiafmETdVFUMvylQdFPoOxIsLm", "kf9iWhwk9GwAXjtwKG-vN7rmXT3hLIT23RBY6KhVaynRrIK7", "kf8JfFUEJhhpRW80_jqD7zzQteH6EBHOzxiOhygRhBdt4z2N"]
        best_pow = givers[0]
        best_complexity = 0
        for giver in givers:
            params = await self.get_pow_params(giver)
            if best_complexity == 0:
                best_complexity = params["complexity"]
                best_pow = giver
            if params["complexity"] > best_complexity:
                best_pow = giver
                best_complexity = params["complexity"]
        return best_pow


async def task_job() -> Dict:
    logger.info("Run task_job()")
    instance = Miner()
    State.job = {}
    while True:
        if State.giver != 'auto':
            result = await instance.get_pow_params(State.giver)
            if result['seed'] != State.job.get('seed', ''):
                State.job.update(result)
                await State.manager.broadcast(result)
        await asyncio.sleep(2)


async def task_auto():
    logger.info("Run task_auto()")
    instance = Miner()
    while True:
        State.giver = await instance.best_giver()
        await asyncio.sleep(60)
