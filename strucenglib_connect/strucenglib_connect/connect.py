from compas.rpc import Proxy

from strucenglib_connect.marshall import json_to_obj, obj_to_json


def analyse_and_extract(server, structure, **kwargs):
    data = {
        'args': kwargs,
        'structure': obj_to_json(structure)
    }
    try:
        client = Proxy('strucenglib_connect.wrapper')
    except Exception as e:
        print(e)
        raise (e)
    response = client.do_analyse_and_extract(server, data)
    if not response:
        print('response is null, error')
        return None

    print(response.get('stdout'))
    success = response.get('success')
    payload = response.get('payload')

    print('success', success)
    if success and payload is not None:
        res = json_to_obj(response['payload'])
        print('obj_to_json successful')
        return res
    else:
        return structure
