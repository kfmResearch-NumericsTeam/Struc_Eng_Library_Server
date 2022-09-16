from marshall import CLASS_WHITE_LIST, obj_to_json, obj_to_obj, set_whitelist
from whitelist import FEA_WHITE_LIST

set_whitelist(FEA_WHITE_LIST)


def analyse_and_extract(structure, software='abaqus', fields=[]):
    print('starting obj to obj ')
    res = obj_to_obj(structure)
    print('end obj to obj ')

    print('analyse_and_extract')
    res.analyse_and_extract(software=software, fields=fields)
    print(obj_to_json(res))
    return res
