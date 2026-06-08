"""
clasificar.py — Calibración de umbrales y clasificación de pertinencias

Pasos:
  1. Calibrar umbrales por indicador usando el Excel con pertinencias conocidas
  2. Clasificar un Excel nuevo con los umbrales calibrados

Uso:
  # Paso 1 — calibrar
  python clasificar.py calibrar --etiquetado df_final_combinado.xlsx --output umbrales.json

  # Paso 2 — clasificar
  python clasificar.py clasificar --input proyectos_nuevos.xlsx --umbrales umbrales.json --output resultado.xlsx
"""

import argparse
import json
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.metrics import f1_score
from scorer import Scorer

# ── Constantes ───────────────────────────────────────────────────────────────

JSON_BIBLIOTECAS = Path(__file__).parent / 'frequent_words.json'

UMBRALES_CANDIDATOS = [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 4.0, 5.0, 6.0, 7.0,
                       8.0, 10.0, 12.0, 14.0, 16.0, 18.0, 20.0, 25.0, 30.0]

UMBRAL_FALLBACK = 5.0   # para indicadores sin positivos en el set de calibración


# ── Helpers ──────────────────────────────────────────────────────────────────

def detectar_indicadores(df):
    """Detecta columnas de indicadores (valores 0/1 únicamente)."""
    return [
        c for c in df.columns
        if df[c].dropna().isin([0, 1]).all() and df[c].nunique() <= 2
    ]


# ── Paso 1: Calibrar ─────────────────────────────────────────────────────────

def calibrar(ruta_etiquetado: str, ruta_output: str):
    print(f"\n📂 Cargando datos etiquetados: {ruta_etiquetado}")
    df = pd.read_excel(ruta_etiquetado)
    ind_cols = detectar_indicadores(df)
    print(f"   {len(df)} proyectos | {len(ind_cols)} indicadores detectados")

    scorer = Scorer(str(JSON_BIBLIOTECAS))

    print("\n⏳ Calculando scores...")
    scores_df = scorer.score_df(df)

    print("\n🔍 Calibrando umbral óptimo por indicador...\n")
    print(f"  {'Indicador':<50} {'n_pos':>6} {'Umbral':>8} {'F1':>7} {'Prec':>7} {'Rec':>7}")
    print("  " + "-" * 85)

    umbrales = {}

    for ind in ind_cols:
        if ind not in scores_df.columns:
            umbrales[ind] = UMBRAL_FALLBACK
            continue

        y_true = df[ind].fillna(0).astype(int).values
        n_pos = int(y_true.sum())

        if n_pos == 0:
            umbrales[ind] = UMBRAL_FALLBACK
            print(f"  {ind[:50]:<50} {n_pos:>6} {'(sin positivos — fallback)':>17}")
            continue

        mejor_f1 = -1
        mejor_umbral = UMBRAL_FALLBACK
        mejor_prec = 0
        mejor_rec = 0

        for u in UMBRALES_CANDIDATOS:
            y_pred = (scores_df[ind] >= u).astype(int).values
            f1 = f1_score(y_true, y_pred, zero_division=0)
            if f1 > mejor_f1:
                mejor_f1 = f1
                mejor_umbral = u
                mejor_prec = float(np.sum((y_pred == 1) & (y_true == 1)) /
                                   max(y_pred.sum(), 1))
                mejor_rec = float(np.sum((y_pred == 1) & (y_true == 1)) /
                                  max(y_true.sum(), 1))

        umbrales[ind] = mejor_umbral
        flag = "  ⚠️" if mejor_f1 < 0.4 else ""
        print(f"  {ind[:50]:<50} {n_pos:>6} {mejor_umbral:>8.1f} "
              f"{mejor_f1:>7.3f} {mejor_prec:>7.3f} {mejor_rec:>7.3f}{flag}")

    # Guardar umbrales
    with open(ruta_output, 'w', encoding='utf-8') as f:
        json.dump(umbrales, f, ensure_ascii=False, indent=2)

    print(f"\n✅ Umbrales guardados en: {ruta_output}")

    # Resumen global
    f1s = []
    for ind in ind_cols:
        if ind not in scores_df.columns: continue
        y_true = df[ind].fillna(0).astype(int).values
        if y_true.sum() == 0: continue
        y_pred = (scores_df[ind] >= umbrales[ind]).astype(int).values
        f1s.append(f1_score(y_true, y_pred, zero_division=0))

    print(f"\n📊 F1 macro promedio con umbrales individuales: {np.mean(f1s):.4f}")
    print(f"   F1 mediana: {np.median(f1s):.4f}")
    print(f"   Indicadores con F1 >= 0.6: {sum(f >= 0.6 for f in f1s)}/{len(f1s)}")
    print(f"   Indicadores con F1 <  0.4: {sum(f < 0.4 for f in f1s)}/{len(f1s)}")


# ── Paso 2: Clasificar ───────────────────────────────────────────────────────

def clasificar(ruta_input: str, ruta_umbrales: str, ruta_output: str):
    print(f"\n📂 Cargando proyectos a clasificar: {ruta_input}")
    df = pd.read_excel(ruta_input)
    print(f"   {len(df)} proyectos")

    print(f"\n📂 Cargando umbrales: {ruta_umbrales}")
    with open(ruta_umbrales, encoding='utf-8') as f:
        umbrales = json.load(f)
    print(f"   {len(umbrales)} indicadores con umbral definido")

    scorer = Scorer(str(JSON_BIBLIOTECAS))

    print("\n⏳ Calculando scores y clasificando...")
    scores_df = scorer.score_df(df)

    # Aplicar umbrales individuales
    for ind, umbral in umbrales.items():
        if ind in scores_df.columns:
            df[ind] = (scores_df[ind] >= umbral).astype(int)
        else:
            df[ind] = 0

    df.to_excel(ruta_output, index=False)
    print(f"\n✅ Resultado guardado en: {ruta_output}")

    # Resumen de clasificación
    ind_cols = list(umbrales.keys())
    ind_presentes = [c for c in ind_cols if c in df.columns]
    print(f"\n📊 Resumen de pertinencias asignadas:")
    print(f"  {'Indicador':<52} {'# proyectos con 1':>18} {'%':>6}")
    print("  " + "-" * 80)
    for ind in ind_presentes:
        n = int(df[ind].sum())
        pct = n / len(df) * 100
        print(f"  {ind[:52]:<52} {n:>18} {pct:>5.1f}%")


# ── CLI ──────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Clasificador de pertinencias UCR')
    subparsers = parser.add_subparsers(dest='comando')

    # Subcomando: calibrar
    p_cal = subparsers.add_parser('calibrar', help='Calibrar umbrales con datos etiquetados')
    p_cal.add_argument('--etiquetado', required=True, help='Excel con pertinencias ya asignadas')
    p_cal.add_argument('--output', default='umbrales.json', help='Archivo JSON de salida')

    # Subcomando: clasificar
    p_cls = subparsers.add_parser('clasificar', help='Clasificar proyectos nuevos')
    p_cls.add_argument('--input',    required=True, help='Excel con proyectos a clasificar')
    p_cls.add_argument('--umbrales', required=True, help='JSON de umbrales calibrados')
    p_cls.add_argument('--output',   required=True, help='Excel de salida con pertinencias')

    args = parser.parse_args()

    if args.comando == 'calibrar':
        calibrar(args.etiquetado, args.output)
    elif args.comando == 'clasificar':
        clasificar(args.input, args.umbrales, args.output)
    else:
        parser.print_help()
