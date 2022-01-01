import asyncio
import base64
import json
import os
from decimal import Decimal

import crc16


async def Pars(text, search, search2=None):
    if search is None or text is None:
        return None
    if search not in text:
        return None
    text = text[text.find(search) + len(search):]
    if search2 is not None and search2 in text:
        text = text[:text.find(search2)]
    return text


async def ng2g(ng):
    return Decimal(str(int(ng)/10**9))


class LiteClient:
    STATE_INDEX = 0

    def __init__(self, app_path, config_path):
        self.app_path = app_path
        self.config_path = config_path

    async def __run(self, cmd, timeout=0):
        
        if timeout == 0:
            timeout = 3
        while True:
            args = ['--global-config', self.config_path,
                "--verbosity", "0", '-i', str(LiteClient.STATE_INDEX), "--cmd", cmd]
            process = await asyncio.create_subprocess_exec(self.app_path, *args, stdin=asyncio.subprocess.PIPE, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
            try:
                stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=timeout)
            except asyncio.exceptions.TimeoutError:
                if LiteClient.STATE_INDEX > 8:
                    LiteClient.STATE_INDEX = 0
                else:
                    LiteClient.STATE_INDEX += 1
                if timeout <= 20:
                    timeout += 1
            else:
                if stderr:
                    print(f"Error lite-client: {stderr.decode()}")
                    timeout = 5
                    await asyncio.sleep(3)
                    continue
                else:
                    return stdout.decode()
            finally:
                try:
                    process.terminate()
                except OSError:
                    pass

    async def get_last(self) -> None:
        await self.__run('last')

    async def get_pow_params(self, powAddr: str) -> dict:
        params = {}
        result = await self.__run(f"runmethod {powAddr} get_pow_params")
        data = await self.result_2list(result)
        if data is not None:
            params["seed"] = data[0]
            params["complexity"] = data[1]
            params["iterations"] = data[2]
        return params

    async def send_file(self, filename: str) -> None:
        assert os.path.isfile(filename), f"File not found: {filename}"
        await self.__run("sendfile " + filename)

    async def get_account(self, wallet: str, convert: bool = True) -> dict:
        cmd = f"getaccount {wallet}"
        result = await self.__run(cmd)
        storage = await self.get_var_from_worker_output(result, "storage")
        assert storage is not None, "Storage wallet not found"
        balance = await self.get_var_from_worker_output(storage, "balance")
        grams = await self.get_var_from_worker_output(balance, "grams")
        value = await self.get_var_from_worker_output(grams, "value")
        state = await self.get_var_from_worker_output(storage, "state")
        status = await Pars(state, "account_", '\n')
        if convert:
            balance = await ng2g(value)
        lt = await Pars(result, "lt = ", ' ')
        hash = await Pars(result, "hash = ", '\n')
        return {
            'wallet': wallet,
            'status': status,
            'balance': balance,
            'lt': lt,
            'hash': hash
        }

    async def get_account_history(self, wallet, limit):
        account = await self.get_account(wallet)
        history = []
        lt = account['lt']
        hash = account['hash']
        ready = 0
        while True:
            result = await self.__run(f"lasttrans {wallet} {lt} {hash}")
            buff = await Pars(result, "previous transaction has", '\n')
            lt = await Pars(buff, "lt ", ' ')
            hash = await Pars(buff, "hash ", ' ')
            arr = result.split("transaction #0")
            for item in arr:
                ready += 1
                if "from block" not in item:
                    continue
                if "VALUE:" not in item:
                    continue
                params = await asyncio.gather(
                    asyncio.create_task(Pars(item, "from block ", '\n')),
                    asyncio.create_task(Pars(item, "time=", ' ')),
                    asyncio.create_task(Pars(item, "outmsg_cnt=", '\n'))
                )
                outmsg = int(params[2])
                if outmsg == 1:
                    item = await Pars(item, "outbound message")
                buff = {}
                buff["block"] = params[0]
                buff["time"] = int(params[1])
                buff["outmsg"] = outmsg
                params = await asyncio.gather(
                    asyncio.create_task(Pars(item, "FROM: ", ' ')),
                    asyncio.create_task(Pars(item, "TO: ", ' ')),
                    asyncio.create_task(Pars(item, "VALUE:", '\n'))
                )
                buff["from"] = await self.hex_addr_2base_64_addr(params[0].lower())
                buff["to"] = await self.hex_addr_2base_64_addr(params[1].lower())
                value = params[2]
                if '+' in value:
                    value = value[:value.find('+')]
                buff["value"] = await ng2g(value)
                history.append(buff)
            if lt is None or ready >= limit:
                return history

    async def get_seqno(self, wallet):
        result = await self.__run(f"runmethod {wallet} seqno")
        if "cannot run any methods" in result:
            return None
        if "result" not in result:
            return 0
        seqno = await self.get_var_from_worker_output(result, "result")
        seqno = seqno.replace(' ', '')
        seqno = await Pars(seqno, '[', ']')
        seqno = int(seqno)
        return seqno

    async def hex_addr_2base_64_addr(self, fullAddr, bounceable=True, testnet=False):
        buff = fullAddr.split(':')
        workchain = int(buff[0])
        addr_hex = buff[1]
        assert len(
            addr_hex) == 64, "HexAddr2Base64Addr error: Invalid length of hexadecimal address"
        b = bytearray(36)
        b[0] = 0x51 - bounceable * 0x40 + testnet * 0x80
        b[1] = workchain % 256
        b[2:34] = bytearray.fromhex(addr_hex)
        buff = bytes(b[:34])
        crc = crc16.crc16xmodem(buff)
        b[34] = crc >> 8
        b[35] = crc & 0xff
        result = base64.b64encode(b)
        result = result.decode()
        result = result.replace('+', '-')
        result = result.replace('/', '_')
        return result

    async def result_2list(self, text):
        buff = await Pars(text, "result:", "\n")
        if buff is None or "error" in buff:
            return
        buff = buff.replace(')', ']')
        buff = buff.replace('(', '[')
        buff = buff.replace(']', ' ] ')
        buff = buff.replace('[', ' [ ')
        arr = buff.split()
        output = ""
        arrLen = len(arr)
        for i in range(arrLen):
            item = arr[i]
            if i+1 < arrLen:
                nextItem = arr[i+1]
            else:
                nextItem = None
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

    async def get_var_from_worker_output(self, text, search):
        if ':' not in search:
            search += ':'
        if search is None or text is None:
            return None
        if search not in text:
            return None
        start = text.find(search) + len(search)
        count = 0
        bcount = 0
        textLen = len(text)
        end = textLen
        for i in range(start, textLen):
            letter = text[i]
            if letter == '(':
                count += 1
                bcount += 1
            elif letter == ')':
                count -= 1
            if letter == ')' and count < 1:
                end = i + 1
                break
            elif letter == '\n' and count < 1:
                end = i
                break
        result = text[start:end]
        if count != 0 and bcount == 0:
            result = result.replace(')', '')
        return result
