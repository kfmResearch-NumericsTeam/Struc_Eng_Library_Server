from compas_fea.structure import Structure

# from marshall import json_to_obj, obj_to_json

from compas.rpc import Proxy

def analyse_and_extract(server, structure, **kwargs):
    # exec = {
    #     'args': kwargs,
    #     'structure': obj_to_json(structure)
    # }
    # try:
    #     client = Proxy('client')
    # except:
    #     client = Proxy('strucenglib_connect.client')
    #
    # response = client.do_analyse_and_extract(server, exec)
    # if not response:
    #     print('response is null, error')
    #     return None
    #
    # print(response.get('stdout'))
    # success = response.get('success')
    # payload = response.get('payload')
    # if success and payload is not None:
    #     return json_to_obj(response['payload'])
    #
    return None


if __name__ == '__main__':
    s = Structure('/tmp/', 'test')
    res = analyse_and_extract('ws://localhost:8007', s, software='abaqus')
    print(res)
