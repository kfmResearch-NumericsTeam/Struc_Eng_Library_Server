import asyncio
import functools
import logging
import os
import sys
import traceback
from contextlib import contextmanager
from io import StringIO

import websockets

from strucenglib_connect.server.browser_log import BrowserLogHandler
from strucenglib_connect.comm_utils import websocket_receive, websocket_send
from strucenglib_connect.config import SERIALIZE_CLIENT_TO_SERVER, SERIALIZE_SERVER_TO_CLIENT
from strucenglib_connect.serialize_pickle import serialize, \
    unserialize
from strucenglib_connect.server.static_server import serve_file_request

LOG_FILE = "my_app.log"
logger = logging.getLogger('strucenglib_server')
browserLog = BrowserLogHandler(LOG_FILE)

WORKING_DIR = 'C:\\Temp\\'

API_PREFIX = '/api'


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
        self.openComputeClients = set()
        pass

    def serve(self):
        script_dir = os.path.dirname(os.path.realpath(__file__))
        handler = functools.partial(serve_file_request, script_dir)
        start_server = websockets.serve(self.handle_client, self.host, self.port,
                                        ping_interval=None,
                                        process_request=handler)

        asyncio.get_event_loop().run_until_complete(start_server)
        asyncio.get_event_loop().run_forever()

    def _is_compute(self, path):
        return path == f'{API_PREFIX}/compute'

    def _is_log(self, path):
        return path == f'{API_PREFIX}/log'

    def _open_connection(self, ws, path):
        if self._is_compute(path):
            self.openComputeClients.add(ws)
        if self._is_log(path):
            browserLog.add_client(ws)

    def _close_connection(self, ws, path):
        if self._is_compute(path):
            self.openComputeClients.remove(ws)
        if self._is_log(path):
            browserLog.remove_client(ws)

    async def handle_client(self, ws, path):
        self._open_connection(ws, path)
        try:
            if self._is_log(path):
                await self._log(ws, path)
            elif self._is_compute(path):
                await self._compute(ws, path)
            else:
                logger.warning('unknown path: %s', path)

        except ConnectionError as e:
            pass
        except Exception as e:
            logger.error('Error in request', e)
            msg = traceback.format_exc()
            try:
                await _send_error(ws, msg)
            except:
                # XXX: if this fails we ignore signaling
                pass
        finally:
            self._close_connection(ws, path)

    async def _log(self, ws, path):
        async for msg in ws:
            # For now we dont do anything, we just forward log messages
            # once they are emitted
            pass

    async def _compute(self, ws, path):
        method, payload = await websocket_receive(ws)
        if method is None:
            await _send_error(ws, 'no method given')
            return
        await self._compute_method_dispatch(ws, path, method, payload)

    async def _compute_method_dispatch(self, ws, path, method, payload):
        logger.info('handle request type: %s', method)

        supported_types = ['analyse_and_extract']
        if method is None or method not in supported_types:
            await _send_error(ws, 'unsuppoted message_type, supported: '
                              + str(supported_types))
            return

        if method == 'analyse_and_extract':
            await self._compute_analyze_and_extract(ws, path, method, payload)

    async def _compute_analyze_and_extract(self, ws, path, method, payload):
        execute_args = payload.get('args')
        structure_data = payload.get('structure')
        logger.info('handle request type: %s', str(execute_args))

        stdout = StringIO()

        def on_stdout_message(text):
            text = text.replace("b''", '')
            text = text.strip()
            if len(text) > 0:
                # XXX: This may be very slow
                # asyncio.create_task(_send_log_output(ws, text))
                logger.info(text)
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


FORMATTER = logging.Formatter("%(asctime)s; %(levelname)s; %(message)s")


def configure_logger():
    logger = logging.getLogger('strucenglib_server')
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(FORMATTER)

    browserLog.setFormatter(FORMATTER)
    logger.addHandler(browserLog)
    logger.addHandler(console_handler)
    logger.propagate = False
    logger.setLevel(logging.DEBUG)
    logging.basicConfig(level=logging.INFO)

def main():
    s = WsServer('0.0.0.0', 8080)
    configure_logger()

    s.serve()


if __name__ == '__main__':
    main()
