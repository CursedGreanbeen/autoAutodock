import os
from docking_model import process_single_docking


def collect_res(proteins, ligands, path=None):
    if not path:
        path = os.getcwd()

    cmd = 'cd ' + path
    os.system(cmd)

    with open('total_nrg.txt', 'w+') as res:
        for prot in proteins:
            for lig in ligands:
                energy = process_single_docking(prot, lig)
                res.write(f'{prot} {lig} {energy}')

            res.write('_______________________________________\n')


def list_names(path=None):
    if not path:
        path = os.getcwd()

    list_dir = os.listdir(path)
    proteins, ligands = [], []

    for file in list_dir:
        if '_clean.pdbqt' in file:
            proteins.append(file[:-12])
        if ('.pdbqt' in file) and ('clean' not in file) and ('out' not in file):
            ligands.append(file[:-6])

    return proteins, ligands


# proteins = [prot[:-12] for prot in dir_list if '_clean.pdbqt' in prot]
# ligands = [lig[:-6] for lig in dir_list if ('.pdbqt' in lig and 'clean' not in lig)]
