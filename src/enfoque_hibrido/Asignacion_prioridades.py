import sys
import json
import re
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer, util

DEBUG = True

# Modelo preentrenado
modelo = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

"""Concatena las columnas cualitativas de un proyecto en un solo texto."""
def construir_texto(row, columnas_texto, columnas_disponibles):
    partes = []
    for col in columnas_texto:
        if col in columnas_disponibles:
            valor = row.get(col, "")
            if isinstance(valor, str) and valor.strip():
                partes.append(f"{col}: {valor.strip()}")
    return "\n".join(partes)

"""
    Primera fase: busca palabras clave exactas en el texto
    de cada proyecto. Marca 1 donde hay coincidencia.
"""
def fase_keywords(base, textos_proyectos, descripciones):
    matches_por_indicador = {ind: set() for ind in descripciones}

    print("\n--- Fase 1: Keywords ---")

    for indicador, info in descripciones.items():
        keywords = info.get("palabras_clave", [])
        if not keywords:
            continue

        if DEBUG:
            print(f"\n=== KEYWORDS {indicador} ===")

        for idx, texto in enumerate(textos_proyectos):
            texto_lower = texto.lower()
            coincidencias = []

            for palabra in keywords:
                patron = r"\b" + re.escape(palabra.lower()) + r"\b"
                if re.search(patron, texto_lower):
                    coincidencias.append(palabra)

            if coincidencias:
                matches_por_indicador[indicador].add(idx)
                base.loc[idx, indicador] = 1

                if DEBUG:
                    print(f"  [KW] Proyecto {idx}: {coincidencias}")

    return matches_por_indicador


"""
    Segunda fase: calcula similitud semántica solo para los proyectos que
    NO tuvieron match de keywords en cada indicador.
"""
def fase_embeddings(base, textos_proyectos, descripciones, matches_keywords):
    total_proyectos = len(textos_proyectos)
    indices_todos = set(range(total_proyectos))

    print("\n--- Fase 2: Embeddings (refuerzo) ---")
    print(f"Calculando embeddings de {total_proyectos} proyectos...")

    embeddings_proyectos = modelo.encode(
        textos_proyectos,
        show_progress_bar=True,
        batch_size=64,
        convert_to_numpy=True,
    )

    print("Asignando pertinencias por embedding...")

    for indicador, info in descripciones.items():
        # Solo evaluar proyectos sin match de keywords
        sin_match = sorted(indices_todos - matches_keywords[indicador])

        if not sin_match:
            if DEBUG:
                print(f"\n=== {indicador}: todos cubiertos por keywords, skip ===")
            continue

        descripcion = info["descripcion"]
        umbral_indicador = info.get("umbral", 0.48)

        embedding_indicador = modelo.encode(descripcion, convert_to_numpy=True)

        # Embeddings solo del subconjunto sin match
        embeddings_sub = embeddings_proyectos[sin_match]

        similitudes = util.cos_sim(embedding_indicador, embeddings_sub)[0]

        if DEBUG:
            print(f"\n=== EMBEDDING {indicador} (evaluando {len(sin_match)} proyectos) ===")

        for i, idx_proyecto in enumerate(sin_match):
            score = float(similitudes[i])
            if score >= umbral_indicador:
                base.loc[idx_proyecto, indicador] = 1
                if DEBUG:
                    print(f"  [EMB] Proyecto {idx_proyecto} + 2: score={score:.3f}")


def mostrar_conteos(base, descripciones, etiqueta):
    print(f"\nConteos — {etiqueta}:")
    resultados = base[list(descripciones.keys())].sum().astype(int)
    for indicador, total in resultados.items():
        print(f"  {indicador:<70} {total}")


def main():
    if len(sys.argv) != 3:
        print("Uso: python3 Asignacion_prioridades.py <archivo xlsx de entrada> <archivo xlsx de salida>")
        sys.exit(1)

    ruta_entrada = sys.argv[1]
    ruta_salida  = sys.argv[2]

    try:
        base = pd.read_excel(ruta_entrada)
    except FileNotFoundError:
        print(f"No se puede encontrar el archivo {ruta_entrada}")
        sys.exit(1)

    with open("columnas.json", encoding="utf-8") as f:
        columnas = json.load(f)

    with open("descripciones_indicadores.json", encoding="utf-8") as f:
        descripciones = json.load(f)

    descripciones.pop("inactivos", None)

    # Inicializar todas las columnas de indicadores en 0
    for indicador in descripciones:
        base[indicador] = 0

    # Construir texto por proyecto
    columnas_disponibles = set(base.columns)
    textos_proyectos = base.apply(
        construir_texto,
        axis=1,
        columnas_texto=columnas["columnas_texto"],
        columnas_disponibles=columnas_disponibles,
    ).tolist()

    # Fase 1: keywords
    matches_keywords = fase_keywords(base, textos_proyectos, descripciones)
    mostrar_conteos(base, descripciones, "después de keywords")

    # Fase 2: embeddings solo donde no hubo match
    fase_embeddings(base, textos_proyectos, descripciones, matches_keywords)
    mostrar_conteos(base, descripciones, "después de embeddings")

    base.to_excel(ruta_salida, index=False)
    print(f"\nAsignación lista en {ruta_salida}")


if __name__ == "__main__":
    main()