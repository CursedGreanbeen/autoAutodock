import list_files


# proteins, ligands = [], []
# proteins, ligands = list_files.list_names(proteins, ligands)

# with open('total_nrg.txt', 'w+') as res:
#     for prot in proteins:
#         for lig in ligands:
#             with open(f'{prot}_{lig}_log.txt') as log:
#                 lines = 25
#                 for i in range(lines):
#                     line = log.readline()
#                     if 'WARNING' in line:
#                         log.readline()
#                 res.write(f'{prot} {lig} {log.readline()}')
#         res.write(f'{'=' * 60}\n')


with open('total_nrg.txt', 'r') as f:
    lines = f.readlines()

with open('total_nrg.txt', 'w') as f:
    for line in lines:
        line = line.strip()
        if '=' in line:
            f.write(line + '\n')
        else:
            parts = line.split()
            if len(parts) >= 6:
                f.write(f"{parts[0]} {parts[1]} {parts[3]}\n")
            else:
                f.write(line + '\n')
