import asyncio
import json
import logging

import websockets
from compas_fea.structure import Structure

from comm_utils import websocket_receive, websocket_send
from marshall import json_to_obj, obj_to_json, set_whitelist
from whitelist import FEA_WHITE_LIST

set_whitelist(FEA_WHITE_LIST)


def analyse_and_extract(server, structure, **kwargs):
    exec = {
        'args': kwargs,
        'structure': obj_to_json(structure)
    }
    c = Client(server)
    response = c.execute('analyse_and_extract', exec)

    if not response:
        return None

    success = response.get('success')
    payload = response.get('payload')
    if success and payload is not None:
        return json_to_obj(response['payload'])

    return None


logger = logging.getLogger(__name__)


class Client:
    def __init__(self, host):
        self.host = host
        self.is_alive = False
        self.result = None
        pass

    async def check_alive(self):
        while self.is_alive:
            print('server is alive')
            await asyncio.sleep(20)

    def execute(self, message_type, payload):
        self.result = {
            'success': False,
            'payload': None
        }
        asyncio.get_event_loop().run_until_complete(asyncio.wait([
            self.check_alive(),
            self.async_processing(message_type, payload)
        ]))

        return self.result

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

    async def async_processing(self, message_type, payload):
        async with websockets.connect(self.host) as websocket:
            await websocket_send(websocket, message_type, payload)
            while True:
                try:
                    type, payload = await websocket_receive(websocket)

                    if type == 'trace':
                        print(payload)

                    elif type == 'analyse_and_extract_result':
                        self.result = {
                            'success': True,
                            'payload': payload
                        }
                    elif type == 'error':
                        print('Error from server: ' + payload)
                        self.is_alive = False
                        break
                    else:
                        print('unknown type:', type, 'payload: ', payload)

                except Exception as e:
                    print(e)
                    self.is_alive = False
                    break


if __name__ == '__main__':
    test = {
        'test': 'test'
    }
    s = Structure('/tmp/', 'test')
    analyse_and_extract('ws://localhost:8007', s, software='abaqus')
