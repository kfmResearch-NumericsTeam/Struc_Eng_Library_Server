import base64
import pickle
from io import BytesIO, StringIO


def obj_to_bin(obj):
    bytes_io = BytesIO()
    # XXX: Iron Python only compatible with v2
    pickle.dump(obj, bytes_io, protocol=2)
    out = base64.b64encode(bytes_io.getvalue()).decode()
    bytes_io.close()
    return out


def bin_to_obj(bin, python_impl='cpython'):
    # XXX: Compatibility issues when running in a iron python interpreter
    # as of Rhino python. Workaround to use compatible wrappers
    if python_impl != 'cpython':
        bytes_io = StringIO(base64.b64decode(bin))
        data = pickle.load(bytes_io)
    else:
        # CPython
        bytes_io = BytesIO(base64.b64decode(bin))
        data = pickle.loads(bytes_io.read())
    bytes_io.close()
    return data
