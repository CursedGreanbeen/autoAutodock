"""
select_flex_residues.py
-----------------------
Выбирает остатки с высоким B-фактором в сайте связывания для
гибкого докинга в AutoDock Vina (подготовка через Meeko).

Зависимости:
    pip install biopython numpy

Использование:
    python select_flex_residues.py \
        --pdb protein.pdb \
        --chain A \
        --center 10.5 20.3 30.1 \
        --radius 10.0 \
        --method stat \
        --sigma 1.0 \
        --fixed-cutoff 40.0 \
        --output flex_residues.txt
"""

import argparse
import sys
import numpy as np
from Bio import PDB


# ─────────────────────────────────────────────
# 1. Парсинг аргументов
# ─────────────────────────────────────────────

def parse_args():
    p = argparse.ArgumentParser(
        description="Выбор гибких остатков по B-фактору для AutoDock Vina"
    )
    p.add_argument("--pdb", required=True, help="Путь к PDB-файлу белка")
    p.add_argument("--chain", default=None,
                   help="ID цепи (например, A). Если не задано — все цепи")
    p.add_argument("--center", nargs=3, type=float, metavar=("X", "Y", "Z"),
                   help="Центр сайта связывания (Å). Если не задано — весь белок")
    p.add_argument("--radius", type=float, default=10.0,
                   help="Радиус сайта связывания вокруг центра (Å). По умолчанию: 10.0")
    p.add_argument("--method", choices=["fixed", "stat", "both"], default="both",
                   help="Метод определения порога:\n"
                        "  fixed — фиксированный порог (--fixed-cutoff)\n"
                        "  stat  — среднее + N×σ (--sigma)\n"
                        "  both  — показать оба")
    p.add_argument("--fixed-cutoff", type=float, default=40.0,
                   help="Порог B-фактора при методе 'fixed' (Å²). По умолчанию: 40.0")
    p.add_argument("--sigma", type=float, default=1.0,
                   help="Множитель σ при методе 'stat'. По умолчанию: 1.0 (среднее + 1σ)")
    p.add_argument("--output", default=None,
                   help="Файл для записи остатков в формате Meeko. "
                        "Если не задано — только вывод в терминал")
    return p.parse_args()


# ─────────────────────────────────────────────
# 2. Загрузка структуры и фильтрация остатков
# ─────────────────────────────────────────────

def load_structure(pdb_path: str):
    parser = PDB.PDBParser(QUIET=True)
    structure = parser.get_structure("protein", pdb_path)
    return structure


def get_residues_in_site(structure, chain_id=None, center=None, radius=10.0):
    """
    Возвращает список остатков (Bio.PDB.Residue) в сайте связывания.
    Только стандартные аминокислоты (без HETATM, воды и т.д.).
    """
    standard_aa = set(PDB.Polypeptide.standard_aa_names)
    residues = []

    for model in structure:
        for chain in model:
            if chain_id and chain.id != chain_id:
                continue
            for residue in chain:
                # Пропускаем воду, лиганды, HETATM
                if residue.get_resname().strip() not in standard_aa:
                    continue
                if center is not None:
                    center_arr = np.array(center)
                    # Берём Cα как представительный атом остатка
                    if "CA" not in residue:
                        continue
                    ca_coord = residue["CA"].get_vector().get_array()
                    dist = np.linalg.norm(ca_coord - center_arr)
                    if dist > radius:
                        continue
                residues.append(residue)
    return residues


# ─────────────────────────────────────────────
# 3. Вычисление среднего B-фактора остатка
# ─────────────────────────────────────────────

def mean_bfactor_residue(residue):
    """Среднее значение B-фактора по всем атомам боковой цепи (без backbone)."""
    backbone = {"N", "CA", "C", "O"}
    bfactors = [
        atom.get_bfactor()
        for atom in residue.get_atoms()
        if atom.get_name() not in backbone
    ]
    if not bfactors:
        # Если только backbone (Gly) — берём все атомы
        bfactors = [atom.get_bfactor() for atom in residue.get_atoms()]
    return np.mean(bfactors) if bfactors else 0.0


# ─────────────────────────────────────────────
# 4. Отбор остатков по порогу
# ─────────────────────────────────────────────

def select_by_fixed(residues_bfactors, cutoff):
    return [(res, bf) for res, bf in residues_bfactors if bf > cutoff]


def select_by_stat(residues_bfactors, sigma_mult):
    bfs = np.array([bf for _, bf in residues_bfactors])
    threshold = bfs.mean() + sigma_mult * bfs.std()
    return [(res, bf) for res, bf in residues_bfactors if bf > threshold], threshold


# ─────────────────────────────────────────────
# 5. Форматирование вывода
# ─────────────────────────────────────────────

def residue_to_meeko_string(residue):
    """
    Формат для флага --flex в Meeko / mk_prepare_receptor.py:
        ChainID:ResName:ResNum
    Например: A:PHE:456
    """
    chain = residue.get_parent().id
    resname = residue.get_resname().strip()
    resnum = residue.get_id()[1]
    return f"{chain}:{resname}{resnum}"


def print_table(label, selected, all_count):
    print(f"\n{'═'*55}")
    print(f"  Метод: {label}")
    print(f"  Отобрано: {len(selected)} / {all_count} остатков")
    print(f"{'─'*55}")
    print(f"  {'Остаток':<20} {'Цепь':<8} {'B-фактор (Å²)':>14}")
    print(f"{'─'*55}")
    for res, bf in sorted(selected, key=lambda x: -x[1]):
        name = f"{res.get_resname().strip()}{res.get_id()[1]}"
        chain = res.get_parent().id
        print(f"  {name:<20} {chain:<8} {bf:>14.2f}")
    print(f"{'═'*55}")


def write_meeko_file(selected, output_path, label):
    residue_strings = [residue_to_meeko_string(res) for res, _ in selected]
    with open(output_path, "w") as f:
        f.write(",".join(residue_strings) + "\n")
    print(f"\n✓ Список остатков сохранён в: {output_path}")
    print(f"  Строка для Meeko:")
    print(f"  --flex {','.join(residue_strings)}")


# ─────────────────────────────────────────────
# 6. Основная логика
# ─────────────────────────────────────────────

def main():
    args = parse_args()

    print(f"\nЗагружаю структуру: {args.pdb}")
    structure = load_structure(args.pdb)

    site_info = (
        f"центр {args.center}, радиус {args.radius} Å"
        if args.center else "весь белок"
    )
    chain_info = f"цепь {args.chain}" if args.chain else "все цепи"
    print(f"Область анализа: {site_info} | {chain_info}")

    residues = get_residues_in_site(
        structure,
        chain_id=args.chain,
        center=args.center,
        radius=args.radius
    )

    if not residues:
        print("Ошибка: остатки в заданной области не найдены. "
              "Проверьте --center, --radius и --chain.", file=sys.stderr)
        sys.exit(1)

    print(f"Остатков в сайте связывания: {len(residues)}")

    # Считаем B-факторы
    residues_bfactors = [(res, mean_bfactor_residue(res)) for res in residues]
    all_bfs = np.array([bf for _, bf in residues_bfactors])
    print(f"\nСтатистика B-факторов боковых цепей:")
    print(f"  Минимум : {all_bfs.min():.2f} Å²")
    print(f"  Среднее : {all_bfs.mean():.2f} Å²")
    print(f"  Максимум: {all_bfs.max():.2f} Å²")
    print(f"  Ст. откл: {all_bfs.std():.2f} Å²")

    # Отбор
    selected_fixed, selected_stat = None, None

    if args.method in ("fixed", "both"):
        selected_fixed = select_by_fixed(residues_bfactors, args.fixed_cutoff)
        print_table(f"Фиксированный порог (>{args.fixed_cutoff} Å²)",
                    selected_fixed, len(residues))

    if args.method in ("stat", "both"):
        selected_stat, threshold = select_by_stat(residues_bfactors, args.sigma)
        print_table(f"Статистический порог (среднее + {args.sigma}σ = {threshold:.2f} Å²)",
                    selected_stat, len(residues))

    # Выбираем результат для записи в файл
    if args.method == "fixed":
        final_selected = selected_fixed
        label = f"fixed_cutoff_{args.fixed_cutoff}"
    elif args.method == "stat":
        final_selected = selected_stat
        label = f"stat_mean+{args.sigma}sigma"
    else:
        # При 'both' — пересечение обоих методов (консервативно)
        fixed_ids = {id(r) for r, _ in selected_fixed}
        final_selected = [(r, bf) for r, bf in selected_stat if id(r) in fixed_ids]
        label = "intersection_fixed_and_stat"
        print(f"\n{'═'*55}")
        print(f"  Пересечение обоих методов: {len(final_selected)} остатков")
        print(f"{'═'*55}")
        for res, bf in sorted(final_selected, key=lambda x: -x[1]):
            name = f"{res.get_resname().strip()}{res.get_id()[1]}"
            chain = res.get_parent().id
            print(f"  {name} (цепь {chain}): {bf:.2f} Å²")

    # Запись в файл
    if args.output and final_selected:
        write_meeko_file(final_selected, args.output, label)
    elif args.output and not final_selected:
        print("\nПредупреждение: нет остатков для записи — файл не создан.")


if __name__ == "__main__":
    main()
