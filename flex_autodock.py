import os
import sys
import subprocess


# =============================================================================
# Константы — меняйте здесь при необходимости
# =============================================================================

WORK_DIR       = "/home/greanbeen/cyberchem"
DOCK_TYPE      = "flex"    # "flex" или "simple"
EXHAUSTIVENESS = 16
VINA           = "vina"

# =============================================================================
# Использование:
#   python flex_autodock.py <белок> <лиганд>
#
# Пример:
#   python flex_autodock.py 8pjk_ready G78
#
# Белок и лиганд передаются аргументами — списки формирует вызывающий скрипт.
# Результат дописывается в total_nrg.txt (не перезаписывается).
# =============================================================================


def run_vina(prot, lig, dock_type):
    """Запускает Vina, пишет лог-файл, возвращает returncode."""
    log_file = f"{prot}_{lig}_log.txt"
    out_file = f"{prot}_{lig}_out.pdbqt"

    if dock_type == "flex":
        cmd = (
            f"{VINA}"
            f" --receptor {prot}_rigid.pdbqt"
            f" --flex {prot}_flex.pdbqt"
            f" --ligand ligands/{lig}.pdbqt"
            f" --config {prot.replace('_ready', '')}_config.txt"
            f" --exhaustiveness {EXHAUSTIVENESS}"
            f" --out {out_file}"
        )

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        shell=True
    )
    
    if result.returncode != 0:
        print(result.stderr or result.stdout)

    with open(log_file, "w", encoding="utf-8") as f:
        f.write(result.stdout)

    return result.returncode, log_file


def parse_best_affinity(log_file, dock_type):
    """Парсит лучшую аффинность из лога Vina (строка с режимом 1)."""
    lines_to_skip = 39 if dock_type in ("flex") else 25

    try:
        with open(log_file, encoding="utf-8") as log:
            for i in range(lines_to_skip):
                line = log.readline()
                if not line:
                    break
                if "WARNING" in line:
                    log.readline()  # пропускаем строку после WARNING
            return log.readline()
    except FileNotFoundError:
        return "N/A\n"


def auto_autodock(prot, lig, dock_type):
    os.chdir(WORK_DIR)

    print(f"\n>>> {prot} + {lig}  [{dock_type}]")

    returncode, log_file = run_vina(prot, lig, dock_type)

    with open("total_nrg.txt", "a", encoding="utf-8") as res:
        if returncode != 0:
            print(f"    ОШИБКА при докинге {prot} + {lig}")
            res.write(f"{prot} {lig} ERROR\n")
        else:
            best = parse_best_affinity(log_file, dock_type)
            res.write(f"{prot} {lig} {best}")
            print(f"    Лучшая аффинность: {best.strip()}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Использование: python flex_autodock.py <белок> <лиганд>")
        print("Пример:        python flex_autodock.py 8pjk_ready G78")
        sys.exit(1)

    auto_autodock(prot=sys.argv[1], lig=sys.argv[2], dock_type=DOCK_TYPE)
