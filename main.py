import argparse
import pathlib

import uvicorn
from starlette.datastructures import State

VERSION = "0.1.1"

BASE_DIR = pathlib.Path(__file__).parent


def createParser():

    parser = argparse.ArgumentParser(
        prog='proxy-toncoin',
        description="Proxy server for toncoin miner",
        epilog='(c) GRinvest 2021. The author of the program, as always, assumes no responsibility for anything.',
        add_help=False
    )
    parent_group = parser.add_argument_group(title='Parameters')
    path = BASE_DIR / "global.config.json"
    parent_group.add_argument(
        '-с',
        dest="сonfig",
        default=path,
        metavar="global.config.json",
        help=f'path global.config.json (default: {path})'
    )
    path = BASE_DIR / "lite-client"
    parent_group.add_argument(
        '-l',
        dest="liteclient",
        default=path,
        metavar="lite-client",
        help=f'path lite-client (default: {path})'
    )

    parent_group.add_argument(
        '-u',
        dest="host",
        default="0.0.0.0",
        metavar='host',
        help='host to connect (default: 0.0.0.0)'
    )
    parent_group.add_argument(
        '-p',
        dest="port",
        default=8080,
        metavar='port',
        help='port for connect (default: 8080)',
        type=int
    )
    parent_group.add_argument(
        '-g',
        dest="giver",
        default='auto',
        metavar='giver_wallet',
        help='wallet giver or auto An easy giver is selected (default: auto)'
    )
    parent_group.add_argument(
        '-L',
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
    parser = createParser()
    State.args = parser.parse_args()
    print(State.args.сonfig)
    uvicorn.run("app:app", host=State.args.host, port=State.args.port,
                log_level=State.args.logger, reload=False)
