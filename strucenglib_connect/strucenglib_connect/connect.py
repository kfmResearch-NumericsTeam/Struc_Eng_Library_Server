from marshall_pickel import bin_to_obj, obj_to_bin

WITH_PROXY = True


def _do_call(server, data):
    if WITH_PROXY:
        from compas.rpc import Proxy
        try:
            proxy = Proxy('strucenglib_connect.rpc_wrapper')
        except Exception as e:
            print(e)
            raise e
        print('Passing message to remote server ', server)
        print('This will take some time. Check server logs')
        return proxy.rpc_analyse_and_extract(server, data)
    else:
        from rpc_wrapper import rpc_analyse_and_extract
        return rpc_analyse_and_extract(server, data)


class StrucEngLibConnectException(Exception):
    pass


def analyse_and_extract(server, structure, **kwargs):
    data = {
        'args': kwargs,
        'version': 'pickle_4',
        'structure': obj_to_bin(structure)
    }

    res_data = _do_call(server, data)
    if res_data is None:
        raise StrucEngLibConnectException('response is null, error')

    stdout = res_data.get('stdout')
    print('\n\n======= Message from Server ' + server + ' BEGIN')
    print(stdout)
    print('======= Message from Server ' + server + ' END\n\n')

    if 'status' not in res_data:
        raise StrucEngLibConnectException('response has no status, error ' + stdout)

    status = res_data.get('status')
    structure_data = res_data.get('payload')

    if status == 'success':
        try:
            structure = bin_to_obj(structure_data, 'iron')
        except:
            #: XXX: try/catch for running outside of iron python
            structure = bin_to_obj(structure_data)
        return structure
    else:
        raise StrucEngLibConnectException("Error from server " + stdout)
