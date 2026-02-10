def convert_to_template(input_file, output_file=None):

    if output_file is None:
        output_file = input_file

    with open(input_file, 'r') as f:
        content = f.read().strip()

    receptor = None
    center = None
    npts = None

    lines = content.split('\n')
    for line in lines:
        line = line.strip()
        if not line:
            continue

        if receptor is None and '.' not in line and '=' not in line:
            receptor = line.strip()

        if line.startswith('center'):
            parts = line.split()
            if len(parts) >= 4:
                center = f"{parts[1]} {parts[2]} {parts[3]}"

        elif line.startswith('npts'):
            parts = line.split()
            if len(parts) >= 4:
                npts = f"{parts[1]} {parts[2]} {parts[3]}"

    if receptor and center and npts:
        cx, cy, cz = center.split()
        sx, sy, sz = npts.split()

        ligand_name = receptor.replace('_clean', '') + '.pdbqt'
        receptor_name = receptor + '.pdbqt'

        template = f"""receptor = {receptor_name}
ligand = {ligand_name}

center_x = {cx}
center_y = {cy}
center_z = {cz}
size_x = {sx}
size_y = {sy}
size_z = {sz}

energy_range = 4
exhaustiveness = 16"""

        with open(output_file, 'w') as f:
            f.write(template)
        return True
    else:
        print("Не удалось извлечь все необходимые данные")
        return False


if __name__ == "__main__":
    configs = ['3PBL', '6LUQ', '8I3V', '8IRT', '8Y2D']

    for prot in configs:
        convert_to_template(f"{prot}_config.txt")

    # Для пакетной обработки всех txt файлов в папке
    # import glob
    # for file in glob.glob("*.txt"):
    #     convert_to_template(file)
