import asyncio
import io
import logging
import sys
import traceback
from contextlib import contextmanager

import websockets

from strucenglib_connect.comm_utils import websocket_receive, websocket_send
from strucenglib_connect.marshall import json_to_obj, obj_to_json, set_whitelist
from strucenglib_connect.whitelist import FEA_WHITE_LIST

logger = logging.getLogger('strucenglib_server')


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


def run_server(host, port):
    set_whitelist(FEA_WHITE_LIST)

    start_server = websockets.serve(handle_client, host, port)
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()


async def _send_error(websocket, msg):
    logger.debug('sending error: %s', msg)
    await websocket_send(websocket, 'error', msg)


async def _send_log_output(websocket, msg):
    await websocket_send(websocket, 'trace', msg)


async def _send_analyse_and_extract_result(websocket, msg):
    await websocket_send(websocket, 'analyse_and_extract_result', msg)


async def handle_client_message(websocket, type, payload):
    logger.info('handle request type: %s', type)

    supported_types = ['analyse_and_extract']
    if type is None or type not in supported_types:
        await _send_error(websocket, 'unsuppoted message_type, supported: ' + str(supported_types))
        return

    if type == 'analyse_and_extract':
        execute_args = payload.get('args')
        structure_json = payload.get('structure')
        logger.info('handle request type: %s', str(execute_args))


        def on_stdout_message(text):
            # XXX: This may be very slow
            asyncio.create_task(_send_log_output(websocket, text))

        structure = json_to_obj(structure_json)
        if structure is None:
            await _send_error(websocket, 'structure is invalid. got None')
            return

        with prefix_stdout(on_stdout_message):
            await _execute_analyse_and_extract(structure, **execute_args)


        result = obj_to_json(structure)
        await websocket_send(websocket, 'analyse_and_extract_result', result)


async def _execute_analyse_and_extract(structure, **execute_args):
    # TODO: Temp dir validation
    structure.analyse_and_extract(**execute_args)
    return structure


async def _do_handle_client(websocket, path):
    message_type, message = await websocket_receive(websocket)

    if message_type is None:
        await websocket.send('no type or message')
        return

    await handle_client_message(websocket, message_type, message)


async def handle_client(websocket, path):
    try:
        await _do_handle_client(websocket, path)
    except Exception as e:
        logger.error('Error in request', e)
        msg = traceback.format_exc()
        try:
            await _send_error(websocket, msg)
        except:
            # if this fails we ignore signaling
            pass


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO,
                        format='%(name)s (%(levelname)s): %(message)s')
    logging.getLogger('strucenglib_server').setLevel(logging.DEBUG)
    run_server('localhost', 8007)
