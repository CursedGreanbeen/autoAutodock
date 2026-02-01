import os
import sys
import subprocess


def replace_line(file_name, line_num, text):
    lines = open(file_name, 'r').readlines()
    lines[line_num] = text
    out = open(file_name, 'w')
    out.writelines(lines)
    out.close()


def auto_autodock(proteins, ligands):
    path = r'cd "C:\Users\Nadezhda\OneDrive\Desktop\Dock"'
    os.system(path)

    with open('total_nrg.txt', 'w+', encoding='utf-8') as res:
        for prot in proteins:
            # with open(f'{prot}_blind_config.txt', 'r') as config:
            with open(f'{prot}_config.txt', 'r', encoding='utf-8') as config:
                data = config.readlines()

            for lig in ligands:
                data[1] = f'ligand = {lig}.pdbqt\n'
                # with open(f'{prot}_blind_config.txt', 'w') as out:
                with open(f'{prot}_config.txt', 'w', encoding='utf-8') as out:
                    out.writelines(data)

                # cmd = r'"C:\Program Files (x86)\The Scripps Research Institute\Vina\vina.exe"' \
                #       f' --receptor {prot}_clean.pdbqt' \
                #       f' --ligand {lig}.pdbqt' \
                #       f' --config {prot}_config.txt' \
                #       f' --out {prot}_{lig}_out.pdbqt'\
                #       f' --log {prot}_{lig}_log.txt'
                #
                # os.system(cmd)
                # lines = 25

                # double docking
                cmd = r'"C:\Program Files (x86)\The Scripps Research Institute\Vina\vina_1_2_3.exe"' \
                      f' --receptor {prot}_clean.pdbqt' \
                      f' --ligand {lig}.pdbqt {lig}.pdbqt' \
                      f' --config {prot}_config.txt' \
                      f' --out {prot}_double_{lig}_out.pdbqt'\

                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    encoding='utf-8',
                    errors='replace',
                    shell=True
                )

                with open(f'{prot}_{lig}_log.txt', 'w', encoding='utf-8') as f:
                    f.write(result.stdout)

                lines = 40

                # blind docking
                # cmd = r'"C:\Program Files (x86)\The Scripps Research Institute\Vina\vina.exe"' \
                #       f' --receptor {prot}_clean.pdbqt' \
                #       f' --ligand {lig}.pdbqt' \
                #       f' --config {prot}_blind_config.txt' \
                #       f' --out {prot}_{lig}_blind_out.pdbqt' \
                #       f' --log {prot}_{lig}_log.txt'
                #
                # os.system(cmd)
                # lines = 25

                with open(f'{prot}_{lig}_log.txt', encoding='utf-8') as log:
                    for i in range(lines):
                        line = log.readline()
                        if 'WARNING' in line:
                            log.readline()
                    res.write(f'{prot} {lig} {log.readline()}')
            res.write(f'{'=' * 60}\n')
