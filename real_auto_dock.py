import os
# import subprocess


proteins = ['7txt', '8dpf', '8hff', '8v6u', '9cbl']
ligands = ['sulfon', 'tietan']
path = r'cd "C:\Users\Nadezhda\OneDrive\Desktop\Dock"'
os.system(path)

with open('total_nrg.txt', 'w+') as res:
    for prot in proteins:
        for lig in ligands:
            cmd = r'"C:\Program Files (x86)\The Scripps Research Institute\Vina\vina.exe"' \
                  f' --receptor {prot}_clean.pdbqt --ligand {lig}.pdbqt --config {prot}_config.txt' \
                  f' --log {prot}_{lig}_log.txt --out {prot}_{lig}_out.pdbqt'
            os.system(cmd)
            with open(f'{prot}_{lig}_log.txt') as log:
                for i in range(26):
                    log.readline()
                res.write(f'{prot} {lig} {log.readline()}')
        res.write('______________________\n')

