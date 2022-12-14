import asyncio
import logging
import os
import sys
import traceback
from contextlib import contextmanager
from io import StringIO

import websockets

from strucenglib_connect.comm_utils import websocket_receive, websocket_send
from strucenglib_connect.config import SERIALIZE_CLIENT_TO_SERVER, SERIALIZE_SERVER_TO_CLIENT
from strucenglib_connect.serialize_pickle import serialize, \
    unserialize

logger = logging.getLogger('strucenglib_server')
WORKING_DIR = 'C:\\Temp\\'


class WriteProxy(object):
    """
    Proxy to delegate stdout to callback
    """

    def __init__(self, orig, callback):
        self.orig = orig
        self.callback = callback

    def write(self, text):
        self.orig.write(text)
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


async def _send_error(websocket, msg):
    logger.debug('sending error: %s', msg)
    await websocket_send(websocket, 'error', msg)


async def _send_log_output(websocket, msg):
    logger.debug('trace %s', msg)
    await websocket_send(websocket, 'trace', msg)


async def _send_result(websocket, msg):
    logger.debug('analyse_and_extract_result %s', '[payload]')
    await websocket_send(websocket, 'analyse_and_extract_result', msg)


class WsServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        pass

    def serve(self):
        start_server = websockets.serve(self.handle_client, self.host, self.port, ping_interval=None)
        asyncio.get_event_loop().run_until_complete(start_server)
        asyncio.get_event_loop().run_forever()

    async def handle_client(self, ws, path):
        logger.info('handle_client %s', path)

        try:
            await self._do_handle(ws, path)
        except Exception as e:
            logger.error('Error in request', e)
            msg = traceback.format_exc()
            try:
                await _send_error(ws, msg)
            except:
                # XXX: if this fails we ignore signaling
                pass

    async def _do_handle(self, ws, path):
        method, payload = await websocket_receive(ws)
        if method is None:
            await _send_error(ws, 'no method given')
            return
        await self._method_dispatch(ws, path, method, payload)

    async def _method_dispatch(self, ws, path, method, payload):
        logger.info('handle request type: %s', method)

        supported_types = ['analyse_and_extract']
        if method is None or method not in supported_types:
            await _send_error(ws, 'unsuppoted message_type, supported: '
                              + str(supported_types))
            return

        if method == 'analyse_and_extract':
            await self._do_analyze_and_extract(ws, path, method, payload)

    async def _do_analyze_and_extract(self, ws, path, method, payload):
        execute_args = payload.get('args')
        structure_data = payload.get('structure')
        logger.info('handle request type: %s', str(execute_args))

        stdout = StringIO()

        def on_stdout_message(text):
            # XXX: This may be very slow
            # asyncio.create_task(_send_log_output(ws, text))
            stdout.write(text)

        structure = unserialize(structure_data, method=SERIALIZE_CLIENT_TO_SERVER)
        if structure is None:
            await _send_error(ws, 'structure is invalid. got None')
            return

        # XXX: Basic sanitzation
        filename = structure.name.replace('\\', '_').replace('/', '_').replace('..', '_')
        structure.name = os.path.basename(filename)
        structure.path = WORKING_DIR

        success = False
        error_msg = ''
        with prefix_stdout(on_stdout_message):
            try:
                structure.analyse_and_extract(**execute_args)
                success = True
            except Exception:
                error_msg = traceback.format_exc()

        if success:
            structure_data = serialize(structure, method=SERIALIZE_SERVER_TO_CLIENT)
            exec_res = {
                'stdout': stdout.getvalue(),
                'structure': structure_data,
                'structure_type': SERIALIZE_SERVER_TO_CLIENT,
            }
            await _send_result(ws, exec_res)
        else:
            await _send_error(ws, error_msg)


def main():
    logging.basicConfig(level=logging.INFO,
                        format='%(name)s (%(levelname)s): %(message)s')
    logging.getLogger('strucenglib_server').setLevel(logging.DEBUG)
    s = WsServer('0.0.0.0', 8080)
    s.serve()


if __name__ == '__main__':
    main()
