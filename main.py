import argparse
import os
import pathlib
import sys

import uvicorn
from starlette.datastructures import State

VERSION = "0.1.5"

BASE_DIR = pathlib.Path(__file__).parent


def createParser():

    parser = argparse.ArgumentParser(
        prog='ton-proxy',
        description="Proxy server for toncoin miner",
        epilog='(c) GRinvest 2021. The author of the program, as always, assumes no responsibility for anything.',
        add_help=False
    )
    parent_group = parser.add_argument_group(title='Parameters')
    path = BASE_DIR /"global.config.json"
    parent_group.add_argument(
        '-C',
        dest="config",
        default=path,
        metavar="global.config.json",
        help=f'path global.config.json (default: {path})'
    )
    path = BASE_DIR /"lite-client"
    parent_group.add_argument(
        '-L',
        dest="liteclient",
        default=path,
        metavar="lite-client",
        help=f'path lite-client (default: {path})'
    )

    parent_group.add_argument(
        '-H',
        dest="host",
        default="0.0.0.0",
        metavar='host',
        help='host to connect (default: 0.0.0.0)'
    )
    parent_group.add_argument(
        '-P',
        dest="port",
        default=8080,
        metavar='port',
        help='port for connect (default: 8080)',
        type=int
    )
    parent_group.add_argument(
        '-G',
        dest="giver",
        default='auto',
        metavar='giver_wallet',
        help='wallet giver or auto An easy giver is selected (default: auto)'
    )
    parent_group.add_argument(
        '-D',
        dest="logger",
        default="info",
        metavar="info",
        help=f'Logger level (default: info)'
    )
    parser.add_argument('--help', '-h', action='help', help='This is help')
    parser.add_argument('--version', '-v', action='version',
                        help='Print version number', version='%(prog)s {}'.format(VERSION))

    return parser


if __name__ == '__main__':
    os.chdir(sys._MEIPASS)
    parser = createParser()
    State.args = parser.parse_args()
    uvicorn.run("app:app", host=State.args.host, port=State.args.port,
                log_level=State.args.logger, reload=False)
