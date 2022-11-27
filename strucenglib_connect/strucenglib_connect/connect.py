

from strucenglib_connect.marshall import json_to_obj, obj_to_json
from compas.rpc import Proxy

def analyse_and_extract(server, structure, **kwargs):
    data = {
        'args': kwargs,
        'structure': obj_to_json(structure)
    }
    print('a')
    try:
        client = Proxy('strucenglib_connect.wrapper')
    except Exception as e:
        print(e)
        raise (e)


    print('b')
    response = client.do_analyse_and_extract(server, data)
    print('c')
    print(response)
    # if not response:
    #     print('response is null, error')
    #     return None
    #
    # print(response.get('stdout'))
    # success = response.get('success')
    # payload = response.get('payload')
    # if success and payload is not None:
    #     return json_to_obj(response['payload'])

    return None

#
# if __name__ == '__main__':
#     from compas_fea.structure import Structure
#     s = Structure('/tmp/', 'test')
#     res = analyse_and_extract('ws://localhost:8007', s, software='abaqus')
#     print(res)
