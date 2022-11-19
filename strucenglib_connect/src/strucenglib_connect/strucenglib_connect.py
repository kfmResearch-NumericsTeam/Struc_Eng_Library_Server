from marshall import json_to_obj, obj_to_json

from compas.rpc import Proxy

def analyse_and_extract(server, structure, **kwargs):
    exec = {
        'args': kwargs,
        'structure': obj_to_json(structure)
    }
    client = Proxy('client')

    response = client.do_analyse_and_extract(server, exec, None)
    # print(response)
    if not response:
        return None

    success = response.get('success')
    payload = response.get('payload')
    if success and payload is not None:
        return json_to_obj(response['payload'])

    return None

