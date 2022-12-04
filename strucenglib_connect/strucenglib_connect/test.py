from compas_fea.structure import Structure

from connect import analyse_and_extract

if __name__ == '__main__':
    s = Structure('/tmp/', 'test')

    res = analyse_and_extract('ws://ibkpika.ethz.ch:8080', s)
    print(res)