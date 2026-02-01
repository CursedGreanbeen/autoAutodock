import os
import subprocess
import sys


prot = '8dpf'
lig = 'mirtazapine_optimized'

cmd = r'"C:\Program Files (x86)\The Scripps Research Institute\Vina\vina_1_2_3.exe"' \
      f' --receptor {prot}_clean.pdbqt' \
      f' --ligand {lig}.pdbqt {lig}.pdbqt' \
      f' --config {prot}_config.txt' \
      f' --out {prot}_double_{lig}_out.pdbqt'

result = subprocess.run(
    cmd,
    capture_output=True,
    text=True,
    encoding='utf-8',
    errors='replace',
    shell=True
)

log_file = f'{prot}_double_{lig}_log.txt'

with open(log_file, 'w', encoding='utf-8') as f:
    f.write(result.stdout)
