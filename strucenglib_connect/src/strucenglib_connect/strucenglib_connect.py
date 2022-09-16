from marshall import obj_to_obj


def analyse_and_extract(structure, software='abaqus', fields=[]):
    print('starting obj to obj ')
    res = obj_to_obj(structure)
    print('end obj to obj ')

    print('analyse_and_extract')
    res.analyse_and_extract(software=software, fields=fields)
    return res
