from compas_fea.structure import Structure

from connect import analyse_and_extract
from marshall import obj_to_json
from marshall_pickel import bin_to_obj, obj_to_bin

if __name__ == '__main__':
    s = Structure('/tmp/', 'test')

    res = analyse_and_extract('ws://localhost:8080', s, software='abaqus')
    print(res)