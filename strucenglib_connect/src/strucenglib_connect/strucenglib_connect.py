import asyncio
import json
import logging

import websockets
from compas_fea.structure import Structure

from marshall import json_to_obj, obj_to_json, set_whitelist
from whitelist import FEA_WHITE_LIST

set_whitelist(FEA_WHITE_LIST)


def analyse_and_extract(structure, software='abaqus', **kwargs):
    exec = {
        'args': kwargs,
        'structure': obj_to_json(structure)
    }
    payload = message_to_string('execute_1_0', exec)

    c = Client()
    response = c.execute(payload)

    if not response:
        return None

    type, payload = message_from_string(response)

    if not type:
        return None

    if 'success' in payload and payload['success'] == True:
        return json_to_obj(response['payload'])
    return None


logger = logging.getLogger(__name__)


def message_to_string(type, payload):
    msg = {
        'message_type': type,
        'message': json.dumps(payload)
    }
    return json.dumps(msg)


def message_from_string(json_msg):
    try:
        unwrap = json.loads(json_msg)
        type = unwrap.get('message_type')
        message = json.loads(unwrap.get('message'))
        return type, message
    except Exception as e:
        print(e)
        return False, None


class Client:
    def __init__(self):
        self.is_alive = False
        pass

    async def alive(self):
        while self.is_alive:
            print('alive')
            await asyncio.sleep(1)

    def execute(self, message):
        asyncio.get_event_loop().run_until_complete(asyncio.wait([
            self.alive(),
            self.async_processing(message)
        ]))

        return {
            'success': False
        }

    def _handle_response(self, response):
        print('response from server: ', response)
        try:
            resp = json.loads(response)
            type = resp.get('type')

            if type == 'success':
                payload = resp.get('payload')
                return False, payload

        except Exception as e:
            print(response)

        return True, None

    async def async_processing(self, message):
        print('async_processing')
        async with websockets.connect('ws://localhost:8765') as websocket:
            await websocket.send(message)
            while True:
                try:
                    res = await websocket.recv()
                    status, payload = self._handle_response(res)
                    if not status:
                        break

                except Exception as e:
                    print('ConnectionClosed')
                    self.is_alive = False
                    break


# def execute_on_server(message):
#     is_alive = True
#
#     async def alive():
#         print('alive')
#         nonlocal is_alive
#         while is_alive:
#             print('alive')
#             await asyncio.sleep(1)
#
#     async def async_processing():
#         nonlocal is_alive
#         print('async_processing')
#         async with websockets.connect('ws://localhost:8765') as websocket:
#             await websocket.send('payload')
#             while True:
#                 try:
#                     message = await websocket.recv()
#                     print(message)
#
#                 except Exception as e:
#                     print(e)
#                     print('ConnectionClosed')
#                     is_alive = False
#                     break
#
#     asyncio.get_event_loop().run_until_complete(asyncio.wait([
#         alive(),
#         async_processing()
#     ]))
#

if __name__ == '__main__':
    test = {
        'test': 'test'
    }
    s = Structure('', '')
    analyse_and_extract(s)
