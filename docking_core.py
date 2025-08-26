import os
import subprocess


def prepare_config(config_file, lig):
    try:
        with open(config_file, 'r') as config:
            data = config.readlines()
            data[1] = f'ligand = {lig}.pdbqt\n'
            return ''.join(data)

    except IOError as e:
        print(f"Error reading file: {e}")


def run_docking(prot, lig, path=r"C:\Program Files (x86)\The Scripps Research Institute\Vina\vina.exe"):
    cmd = f'{path}' \
          f' --receptor {prot}_clean.pdbqt' \
          f' --ligand {lig}.pdbqt' \
          f' --config {prot}_config.txt' \
          f' --log {prot}_{lig}_log.txt'\
          f' --out {prot}_{lig}_out.pdbqt'

    try:
        subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True)
    except subprocess.CalledProcessError:
        pass


def parse_docking_result(log_file):
    with open(log_file) as log:
        for _ in range(26):
            next(log)
            if 'WARNING: The search space volume > 27000 Angstrom^3 (See FAQ)' in log:
                next(log)
    return log.readline().split()[1]


def auto_autodock(proteins, ligands, path=r"C:\Users\Nadezhda\OneDrive\Desktop\Dock"):
    cmd = 'cd ' + path
    os.system(cmd)

    with open('total_nrg.txt', 'w+') as res:
        for prot in proteins:
            config_file = f'{prot}_config.pdbqt'
            for lig in ligands:
                data = prepare_config(config_file, lig)
                with open(config_file, 'w') as out:
                    out.writelines(data)

                run_docking(prot, lig)
                log_file = f'{prot}_{lig}_log.txt'
                energy = parse_docking_result(log_file)
                res.write(f'{prot} {lig} {energy}')

            res.write('_______________________________________\n')
