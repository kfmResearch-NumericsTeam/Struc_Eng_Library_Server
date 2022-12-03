import base64
import pickle
from io import BytesIO


def obj_to_bin(obj):
    bytes_io = BytesIO()
    pickle.dump(obj, bytes_io, 2)
    out = base64.b64encode(bytes_io.getvalue()).decode()
    bytes_io.close()
    return out


def bin_to_obj(bin):
    bytes_io = BytesIO(base64.b64decode(bin))
    data = pickle.loads(bytes_io.read())
    bytes_io.close()
    return data
