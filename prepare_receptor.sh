#!/bin/bash
# =============================================================================
# prepare_receptor.sh — подготовка рецепторов и запуск гибкого докинга
# =============================================================================
# Шаги:
#   Для каждого *_clean.pdb в рабочей папке:
#     1. Определить шифр цепи
#     2. Выбрать флексибельные остатки (B-фактор + близость к сайту)
#     3. Добавить полярные водороды (pdb2pqr)
#     4. Исправить гистидины (HIS -> HID/HIE по геометрии)
#     5. Запустить mk_prepare_receptor.py (Meeko)
#   После обработки всех белков:
#     6. Собрать списки готовых белков и лигандов, запустить flex_autodock.py
#
# Использование:
#   bash prepare_receptor.sh [рабочая_папка]
#
# Пример:
#   bash prepare_receptor.sh ./dock
#
# Ожидаемая структура рабочей папки:
#   <name>_clean.pdb       — белок
#   <name>_config.txt      — конфиг бокса (по одному на каждый белок)
#   ligands/               — лиганды .pdbqt
#
# Формат конфиг-файла:
#   center_x = 161.873
#   center_y = 170.483
#   center_z = 142.739
#   size_x = 24
#   size_y = 24
#   size_z = 26
#
# Зависимости:
#   conda activate docking   (pdb2pqr, meeko, biopython)
#   select_flex_residues.py  (должен лежать рядом со скриптом)
#   flex_autodock.py         (должен лежать рядом со скриптом)
# =============================================================================
 
set -e
 
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
WORK_DIR="${1:-.}"
mkdir -p "$WORK_DIR"
 
# ─── Функция парсинга одного параметра из конфига ─────────────────────────────
parse_param() {
    grep -E "^\s*$1\s*=" "$2" | awk -F'=' '{print $2}' | tr -d ' \r'
}
 
# =============================================================================
# Функция подготовки одного белка
# =============================================================================
prepare_one_receptor() {
    local PDB_IN="$1"
    local CONFIG_IN="$2"
 
    # ── Проверка конфига ──────────────────────────────────────────────────────
    if [[ ! -f "$CONFIG_IN" ]]; then
        echo "  ПРОПУСК: конфиг-файл не найден: $CONFIG_IN"
        return 1
    fi
 
    local CX CY CZ SX SY SZ
    CX=$(parse_param "center_x" "$CONFIG_IN")
    CY=$(parse_param "center_y" "$CONFIG_IN")
    CZ=$(parse_param "center_z" "$CONFIG_IN")
    SX=$(parse_param "size_x"   "$CONFIG_IN")
    SY=$(parse_param "size_y"   "$CONFIG_IN")
    SZ=$(parse_param "size_z"   "$CONFIG_IN")
 
    for VAR in CX CY CZ SX SY SZ; do
        if [[ -z "${!VAR}" ]]; then
            echo "  ПРОПУСК: параметр $VAR не найден в $CONFIG_IN"
            return 1
        fi
    done
 
    # ── Пути ─────────────────────────────────────────────────────────────────
    local BASENAME
    BASENAME=$(basename "$PDB_IN" _clean.pdb)
    local PDB_H="$WORK_DIR/${BASENAME}_H.pdb"
    local PDB_FIXED="$WORK_DIR/${BASENAME}_H_fixed.pdb"
    local FLEX_FILE="$WORK_DIR/${BASENAME}_flex_residues.txt"
    local OUT_BASE="$WORK_DIR/${BASENAME}_ready"
 
    echo ""
    echo "======================================================"
    echo "  Белок: $PDB_IN"
    echo "  Конфиг: $CONFIG_IN"
    echo "  Центр бокса:  $CX $CY $CZ"
    echo "  Размер бокса: $SX $SY $SZ"
    echo "======================================================"
 
    # ── Шаг 1: Определить шифр цепи ──────────────────────────────────────────
    echo ""
    echo ">>> Шаг 1: Определение цепей в файле"
    local CHAIN
    CHAIN=$(grep "^ATOM" "$PDB_IN" | cut -c22 | sort -u | tr -d ' \r\n' | head -c1)
    echo "    Используется цепь: $CHAIN"
 
    # ── Шаг 2: Выбрать флексибельные остатки ─────────────────────────────────
    echo ""
    echo ">>> Шаг 2: Выбор флексибельных остатков"
 
    python "$SCRIPT_DIR/select_flex_residues.py" \
        --pdb "$PDB_IN" \
        --chain "$CHAIN" \
        --center "$CX" "$CY" "$CZ" \
        --radius 10.0 \
        --method stat \
        --sigma 1.0 \
        --output "$FLEX_FILE"
 
    local FLEX_ARG=""
    if [[ ! -f "$FLEX_FILE" ]]; then
        echo "    Flex остатки не найдены. Продолжить без флекс? (y/n)"
        read -r ANSWER
        if [[ "$ANSWER" != "y" ]]; then
            return 1
        fi
    else
        local FLEX_RAW FLEX_MEEKO
        FLEX_RAW=$(cat "$FLEX_FILE")
        FLEX_MEEKO=$(echo "$FLEX_RAW" | tr ',' '\n' | \
            sed 's/\([A-Z]\):\([A-Z]*\)\([0-9]*\)/\1:\3/' | \
            tr '\n' ',' | sed 's/,$//')
        echo "    Flex остатки для Meeko: $FLEX_MEEKO"
        FLEX_ARG="-f \"$FLEX_MEEKO\""
    fi
 
    # ── Шаг 3: Добавить полярные водороды ────────────────────────────────────
    echo ""
    echo ">>> Шаг 3: Добавление полярных водородов (pdb2pqr)"
    pdb2pqr30 \
        --ff=AMBER \
        --with-ph=7.4 \
        --pH=7.4 \
        --pdb-output "$PDB_H" \
        "$PDB_IN" \
        "$WORK_DIR/${BASENAME}.pqr" 2>&1 | grep -E "INFO|WARNING|ERROR" || true
 
    if [[ ! -f "$PDB_H" ]]; then
        echo "    ОШИБКА: pdb2pqr не создал файл $PDB_H"
        return 1
    fi
    echo "    Создан: $PDB_H"
 
    # ── Шаг 4: Исправить гистидины ───────────────────────────────────────────
    echo ""
    echo ">>> Шаг 4: Исправление гистидинов"
 
    local HIS_LIST
    HIS_LIST=$(grep "^ATOM" "$PDB_H" | awk '{print $4, $5, $6}' | grep "^HIS" | awk '{print $3}' | sort -u)
 
    if [[ -z "$HIS_LIST" ]]; then
        echo "    Гистидинов не найдено — пропускаем"
        cp "$PDB_H" "$PDB_FIXED"
    else
        cp "$PDB_H" "$PDB_FIXED"
        local RESNUM HAS_HD1 HAS_HE2 STATE
        for RESNUM in $HIS_LIST; do
            HAS_HD1=$(grep "^ATOM" "$PDB_H" | awk -v r="$RESNUM" '$6==r && $3=="HD1"' | wc -l)
            HAS_HE2=$(grep "^ATOM" "$PDB_H" | awk -v r="$RESNUM" '$6==r && $3=="HE2"' | wc -l)
 
            if [[ "$HAS_HD1" -gt 0 && "$HAS_HE2" -gt 0 ]]; then
                STATE="HIP"
            elif [[ "$HAS_HD1" -gt 0 ]]; then
                STATE="HID"
            else
                STATE="HIE"
            fi
 
            echo "    HIS $RESNUM -> $STATE (HD1=$HAS_HD1, HE2=$HAS_HE2)"
            sed -i "s/HIS \($CHAIN \+$RESNUM\)/$STATE \1/g" "$PDB_FIXED"
        done
        echo "    Создан: $PDB_FIXED"
    fi
 
    # ── Шаг 5: Запустить Meeko ───────────────────────────────────────────────
    echo ""
    echo ">>> Шаг 5: Подготовка PDBQT файлов (Meeko)"
 
    eval mk_prepare_receptor.py \
        -i "$PDB_FIXED" \
        -o "$OUT_BASE" \
        -p -v -g \
        --box_size "$SX" "$SY" "$SZ" \
        --box_center "$CX" "$CY" "$CZ" \
        $FLEX_ARG \
        -a
 
    echo ""
    echo "  Созданные файлы:"
    ls "${OUT_BASE}"* 2>/dev/null | sed 's/^/    /'
}
 
# =============================================================================
# Основной цикл — перебираем все *_clean.pdb в рабочей папке
# =============================================================================
echo ""
echo "======================================================"
echo "  Рабочая папка: $WORK_DIR"
echo "======================================================"
 
PDB_FILES=()
while IFS= read -r -d '' f; do
    PDB_FILES+=("$f")
done < <(find "$WORK_DIR" -maxdepth 1 -name "*_clean.pdb" -print0 | sort -z)
 
if [[ ${#PDB_FILES[@]} -eq 0 ]]; then
    echo "ОШИБКА: не найдено ни одного *_clean.pdb в $WORK_DIR"
    exit 1
fi
 
echo "  Найдено белков: ${#PDB_FILES[@]}"
for f in "${PDB_FILES[@]}"; do echo "    $f"; done
 
for PDB_IN in "${PDB_FILES[@]}"; do
    BASENAME=$(basename "$PDB_IN" _clean.pdb)
    CONFIG_IN="$WORK_DIR/${BASENAME}_config.txt"
    prepare_one_receptor "$PDB_IN" "$CONFIG_IN" || echo "  ОШИБКА при обработке $PDB_IN — пропускаем"
done
 
# =============================================================================
# Шаг 6 — собрать списки и запустить докинг
# =============================================================================
echo ""
echo ">>> Шаг 6: Сбор белков и лигандов, запуск докинга"
 
PROTEINS=()
while IFS= read -r -d '' f; do
    name=$(basename "$f" _rigid.pdbqt)
    PROTEINS+=("$name")
done < <(find "$WORK_DIR" -maxdepth 1 -name "*_rigid.pdbqt" -print0 | sort -z)
 
LIGANDS_DIR="$WORK_DIR/ligands"
LIGANDS=()
if [[ -d "$LIGANDS_DIR" ]]; then
    while IFS= read -r -d '' f; do
        name=$(basename "$f" .pdbqt)
        LIGANDS+=("$name")
    done < <(find "$LIGANDS_DIR" -maxdepth 1 -name "*.pdbqt" -print0 | sort -z)
else
    echo "    ПРЕДУПРЕЖДЕНИЕ: папка $LIGANDS_DIR не найдена — докинг пропущен"
    exit 0
fi
 
if [[ ${#PROTEINS[@]} -eq 0 ]]; then
    echo "    ОШИБКА: не найдено ни одного *_rigid.pdbqt в $WORK_DIR"
    exit 1
fi
if [[ ${#LIGANDS[@]} -eq 0 ]]; then
    echo "    ОШИБКА: не найдено ни одного .pdbqt в $LIGANDS_DIR"
    exit 1
fi
 
echo "    Белки:   ${PROTEINS[*]}"
echo "    Лиганды: ${LIGANDS[*]}"
echo ""
 
for PROT in "${PROTEINS[@]}"; do
    for LIG in "${LIGANDS[@]}"; do
        echo "    Запуск: $PROT + $LIG"
        python "$SCRIPT_DIR/flex_autodock.py" "$PROT" "$LIG"
    done
done
 
echo ""
echo "======================================================"
echo "  Докинг завершён. Результаты: $WORK_DIR/total_nrg.txt"
echo "======================================================"
 
