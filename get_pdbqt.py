import os
from rdkit import Chem
from rdkit.Chem import AllChem
from openbabel import pybel  # или from openbabel import openbabel
from openbabel import openbabel
from pathlib import Path


def generate_and_optimize(input_sdf, output_dir="pdbqts"):

    os.makedirs(output_dir, exist_ok=True)
    print(f"  Conversion to pdbqt...")
    try:
        ob_mol = next(pybel.readfile("sdf", input_sdf))
        mol_name = input_sdf[:-4]
        output_pdb = os.path.join(output_dir, f"{mol_name}.pdb")
        ob_mol.write(format="pdb", filename=output_pdb, overwrite=True)
        print(f"  Сохранено: {output_pdb}")

        obConversion = openbabel.OBConversion()
        obConversion.SetInAndOutFormats("pdb", "pdbqt")

        mol = openbabel.OBMol()
        if obConversion.ReadFile(mol, output_pdb):
            # Optional: add hydrogens and compute charges
            # mol.AddHydrogens()
            output_pdbqt = os.path.join(output_dir, f"{mol_name}.pdbqt")
            obConversion.WriteFile(mol, output_pdbqt)
            print(f"Converted {output_pdb} to {output_pdbqt}")
            return output_pdbqt
        else:
            print("Conversion failed")

    except Exception as e:
        print(f"  Ошибка OpenBabel: {e}")
        return None


path = os.listdir(r'C:\Users\Nadezhda\OneDrive\Рабочий стол\Dock')
for file in path:
    if '.sdf' in file:
        result = generate_and_optimize(file)

