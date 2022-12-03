import asyncio
import io
import logging

import websockets

from strucenglib_connect.comm_utils import websocket_receive, websocket_send

logger = logging.getLogger(__name__)

class WsResult:
    def __init__(self):
        self.status = 'error'
        self.stdout = ''
        self.payload = None


class WsClient:
    def __init__(self, host):
        self.host = host
        self.is_alive = False
        pass

    async def check_alive(self):
        while self.is_alive:
            print('server is alive')
            await asyncio.sleep(20)

    def analyse_and_extract(self, payload):
        stdout_buffer = io.StringIO()

        result = WsResult()
        result.status = 'error'

        asyncio.get_event_loop().run_until_complete(asyncio.wait([
            self.check_alive(),
            self.async_processing(payload, stdout_buffer, result)
        ]))
        result.stdout = stdout_buffer.getvalue()
        stdout_buffer.close()
        return result

    async def async_processing(self, payload, stdout_buffer, result):
        def _do_print(msg):
            print('do_print: ', msg)
            stdout_buffer.write(msg)

        try:
            async with websockets.connect(self.host, ping_interval=None) as ws:
                await websocket_send(ws, 'analyse_and_extract', payload)
                while True:
                    method, payload = await websocket_receive(ws)

                    if method == 'trace':
                        _do_print(payload)

                    elif method == 'analyse_and_extract_result':
                        result.status = 'success'
                        result.payload = payload.get('structure')
                        _do_print(payload.get('stdout'))
                        break

                    elif method == 'error':
                        _do_print('Error from server: ' + payload)
                        break
                    else:
                        _do_print('unknown type:' + method + ', payload: ' + payload)


        except Exception as e:
            _do_print(e)

        self.is_alive = False