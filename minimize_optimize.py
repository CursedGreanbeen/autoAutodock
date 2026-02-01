import os
from rdkit import Chem
from rdkit.Chem import AllChem
from openbabel import pybel
from openbabel import openbabel


def generate_and_optimize(smiles, mol_name, output_dir="optimized_refs"):

    os.makedirs(output_dir, exist_ok=True)
    print(f"Обработка: {mol_name} ({smiles})")

    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        print(f"Invalid SMILES {smiles}")
        return None

    mol = Chem.AddHs(mol)

    print(f"  Генерация 3D структуры...")
    params = AllChem.ETKDGv3()
    params.randomSeed = 42
    success = AllChem.EmbedMolecule(mol, params)

    if success == -1:
        print(f"  Не удалось сгенерировать 3D структуру")
        return None

    try:
        AllChem.MMFFOptimizeMolecule(mol, maxIters=100)
        print(f"  Предварительная оптимизация RDKit завершена")
    except:
        print(f"  Предварительная оптимизация не удалась, продолжаем")

    temp_sdf = os.path.join(output_dir, f"temp_{mol_name}.sdf")
    writer = Chem.SDWriter(temp_sdf)
    writer.write(mol)
    writer.close()

    print(f"  Оптимизация OpenBabel...")
    try:
        ob_mol = next(pybel.readfile("sdf", temp_sdf))
        ob_mol.localopt(forcefield='mmff94', steps=500)
        output_pdb = os.path.join(output_dir, f"{mol_name}_optimized.pdb")
        ob_mol.write(format="pdb", filename=output_pdb, overwrite=True)
        print(f"  Сохранено: {output_pdb}")

        obConversion = openbabel.OBConversion()
        obConversion.SetInAndOutFormats("pdb", "pdbqt")

        mol = openbabel.OBMol()
        if obConversion.ReadFile(mol, output_pdb):
            # Optional: add hydrogens and compute charges
            # mol.AddHydrogens()
            output_pdbqt = os.path.join(output_dir, f"{mol_name}_optimized.pdbqt")
            obConversion.WriteFile(mol, output_pdbqt)
            print(f"Converted {output_pdb} to {output_pdbqt}")
        else:
            print("Conversion failed")

        os.remove(temp_sdf)

        return output_pdb

    except Exception as e:
        print(f"  Ошибка OpenBabel: {e}")
        print(f"  Сохранение неоптимизированной структуры")

        output_pdb = os.path.join(output_dir, f"{mol_name}_no_opt.pdb")
        writer = Chem.PDBWriter(output_pdb)
        writer.write(mol)
        writer.close()

        return output_pdb


# def batch_process_smiles(smiles_file, output_dir="optimized_molecules"):
#
#     results = {}
#
#     for line in smiles_file.readlines():
#         name, smiles = line.split()
#         print(f"\n{'=' * 50}")
#         result = generate_and_optimize(smiles, name, output_dir)
#         if result:
#             results[name] = result

def batch_process_smiles(smiles, output_dir="optimized_refs"):

    results = {}

    for line in smiles:
        name, smile = line.split()
        print(f"\n{'=' * 50}")
        result = generate_and_optimize(smile, name, output_dir)
        if result:
            results[name] = result

    report_file = os.path.join(output_dir, "report.txt")
    with open(report_file, 'w') as f:
        f.write("Отчет по оптимизации молекул\n")
        f.write("=" * 50 + "\n\n")
        for name, filepath in results.items():
            f.write(f"{name}: {filepath}\n")

    print(f"\n{'=' * 50}")
    print(f"Обработка завершена!")
    print(f"Результаты в папке: {output_dir}")
    print(f"Отчет: {report_file}")

    return results


if __name__ == "__main__":
    # with open('squares_smiles.txt', 'r') as file:
    #     results = batch_process_smiles(file)
    smiles = ['mirtazapine CN1CCN2C(C1)C3=CC=CC=C3CC4=C2N=CC=C4']
    res = batch_process_smiles(smiles)
