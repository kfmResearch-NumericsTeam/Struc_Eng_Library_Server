import asyncio
import io
import json
import logging

import websockets

from strucenglib_connect.comm_utils import websocket_receive, websocket_send

logger = logging.getLogger(__name__)


def do_analyse_and_extract(server, data):
    c = Client(server)
    return c.execute('analyse_and_extract', data)


class Client:
    def __init__(self, host):
        self.host = host
        self.is_alive = False
        self.result = None
        self.stdout_buffer = io.StringIO()
        pass

    async def check_alive(self):
        while self.is_alive:
            print('server is alive')
            await asyncio.sleep(20)

    def execute(self, message_type, payload):
        self.result = {
            'success': False,
            'payload': None,
            'stdout': None,
        }
        asyncio.get_event_loop().run_until_complete(asyncio.wait([
            self.check_alive(),
            self.async_processing(message_type, payload)
        ]))

        self.result['stdout'] = self.stdout_buffer.getvalue()
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

    def _do_print(self, msg):
        print(msg)
        self.stdout_buffer.write(str(msg))

    async def async_processing(self, message_type, payload):
        try:
            async with websockets.connect(self.host) as websocket:
                await websocket_send(websocket, message_type, payload)
                while True:
                    try:
                        type, payload = await websocket_receive(websocket)

                        if type == 'trace':
                            self._do_print(payload)

                        elif type == 'analyse_and_extract_result':
                            self.result = {
                                'success': True,
                                'payload': payload
                            }
                        elif type == 'error':
                            self._do_print('Error from server: ' + payload)
                            self.is_alive = False
                            break
                        else:
                            self._do_print('unknown type:' + type + ', payload: ' + payload)

                    except Exception as e:
                        self._do_print(e)
                        self.is_alive = False
                        break
        except Exception as e:
            self._do_print(e)
