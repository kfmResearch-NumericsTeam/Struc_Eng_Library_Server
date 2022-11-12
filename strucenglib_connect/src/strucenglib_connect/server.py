import asyncio
import json

import websockets

from marshall import json_to_obj, obj_to_json, set_whitelist
from strucenglib_connect import message_from_string
from whitelist import FEA_WHITE_LIST

set_whitelist(FEA_WHITE_LIST)

from contextlib import contextmanager
import sys


class WriteProxy(object):
    def __init__(self, orig, callback):
        self.orig = orig
        self.callback = callback

    def write(self, text):
        self.orig.write('>>>> ' + text)
        self.callback(text)

    def __getattr__(self, attr):
        return getattr(self.orig, attr)


@contextmanager
def prefix_stdout(callback):
    current_out = sys.stdout
    try:
        sys.stdout = WriteProxy(current_out, callback)
        yield
    finally:
        sys.stdout = current_out


async def handle_type(websocket, type, payload):
    print('handle_type', type, payload)

    supported_types = ['execute_1_0']
    if type is None or type not in supported_types:
        await websocket.send('unsuppoted message_type')
        return


    if type == 'execute_1_0':
        execute_args = payload.get('args')
        structure_json = payload.get('structure')

        async def on_message(text):
            # XXX: Log type prefix
            await websocket.send(text)
            pass

        structure = json_to_obj(structure_json)
        print('a')
        print(structure)
        if structure is None:
            await websocket.send('structure is None')
            return

        with prefix_stdout(on_message):
            structure.analyse_and_extract(*execute_args)

            result = obj_to_json(structure)
            await websocket.send({
                'message_type': 'exec',
                'payload': result
            })

        # TODO: only send result not entire structure


        pass


async def hello(websocket, path):
    resp = await websocket.recv()
    print('message from client', resp)
    payload = None

    type, message = message_from_string(resp)

    if type is None:
        await websocket.send('no type or message')
        return

    try:
        await handle_type(websocket, type, message)
    except Exception as e:
        print(e)
        await websocket.send('error in request: ' + str(e))


if __name__ == '__main__':
    print('main')
    start_server = websockets.serve(hello, 'localhost', 8765)
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()
