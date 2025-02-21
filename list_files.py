import os


def list_names(proteins, ligands, path=r'C:\Users\Nadezhda\OneDrive\Рабочий стол\Dock'):
    list_dir = os.listdir(path)

    for file in list_dir:
        if '_clean.pdbqt' in file:
            proteins.append(file[:-12])
        if ('.pdbqt' in file) and ('clean' not in file) and ('out' not in file):
            ligands.append(file[:-6])

    return proteins, ligands
