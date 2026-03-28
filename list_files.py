import os


def list_names(proteins, ligands, path=r'your path to the docking dir'):

    list_dir = os.listdir(path)
    for file in list_dir:
        if '_clean.pdbqt' in file:
            proteins.append(file[:-12])
        if ('.pdbqt' in file) and ('clean' not in file) and ('out' not in file):
            ligands.append(file[:-6])

    return proteins, ligands


# proteins = [prot[:-12] for prot in dir_list if '_clean.pdbqt' in prot]
# ligands = [lig[:-6] for lig in dir_list if ('.pdbqt' in lig and 'clean' not in lig)]

# print(*proteins, *ligands)
