import sys
import json
import re
import numpy as np
import pandas as pd
import unicodedata
import argparse

def normalizar(texto):
    texto = texto.lower()
    texto = unicodedata.normalize("NFD", texto)
    texto = "".join(c for c in texto if unicodedata.category(c) != "Mn")
    return texto

DEBUG = True


_modelo = None

# Cargar modelo solo si se indica como argumento
def cargar_modelo():
    global _modelo, util
    if _modelo is None:
        print("Cargando modelo de embeddings...")
        from sentence_transformers import SentenceTransformer, util
        # Modelo preentrenado
        _modelo = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
    return _modelo

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
            texto_lower = normalizar(texto)
            coincidencias = []

            for palabra in keywords:
                patron = r"\b" + re.escape(normalizar(palabra)) + r"\b"
                if re.search(patron, texto_lower):
                    coincidencias.append(palabra)

            if coincidencias:
                matches_por_indicador[indicador].add(idx)
                base.loc[idx, indicador] = 1

                if DEBUG:
                    print(f"  [KW] Proyecto {idx + 2}: {coincidencias}")

    return matches_por_indicador


"""
    Segunda fase: sugiere proyectos candidatos para enriquecer el diccionario
    de keywords. NO asigna valores — solo imprime en consola para revisión.

    El objetivo de esta fase es dar opciones al usuario/desarrollador de posibles
    keywords o frases similares utilizando el JSON de descripciones_indicadores,
    esto con el objetivo del enriquecimiento del diccionario a la vez de evitar
    asignaciones abstractas de parte del modelo
"""
def fase_embeddings(textos_proyectos, descripciones, matches_keywords):
    modelo = cargar_modelo()
    total_proyectos = len(textos_proyectos)
    indices_todos = set(range(total_proyectos))

    print("\n--- Fase 2: Embeddings ---")
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

        keywords = info.get("palabras_clave", [])
        texto_indicador = " | ".join(keywords) if keywords else info["descripcion"]
        embedding_indicador = modelo.encode(texto_indicador, convert_to_numpy=True)

        umbral_indicador = info.get("umbral", 0.48)

        # Embeddings solo del subconjunto sin match
        embeddings_sub = embeddings_proyectos[sin_match]

        similitudes = util.cos_sim(embedding_indicador, embeddings_sub)[0]

        if DEBUG:
            print(f"\n=== EMBEDDING {indicador} (evaluando {len(sin_match)} proyectos) ===")

        for i, idx_proyecto in enumerate(sin_match):
            score = float(similitudes[i])
            if score >= umbral_indicador:
                if DEBUG:
                    # Fragmento más similar
                    oraciones = [s.strip() for s in re.split(r'[.\n|]', textos_proyectos[idx_proyecto]) if s.strip()]
                    if oraciones:
                        emb_oraciones = modelo.encode(oraciones, convert_to_numpy=True)
                        sims_oraciones = util.cos_sim(embedding_indicador, emb_oraciones)[0]
                        mejor_idx = int(sims_oraciones.argmax())
                        mejor_frag = oraciones[mejor_idx][:120]
                    else:
                        mejor_frag = "(sin fragmento)"

                    # Keyword más cercana 
                    keywords = info.get("palabras_clave", [])
                    if keywords:
                        emb_kws = modelo.encode(keywords, convert_to_numpy=True)
                        # similitud entre cada keyword del indicador y el texto del proyecto
                        emb_proyecto = embeddings_proyectos[idx_proyecto]
                        sims_kws = util.cos_sim(emb_proyecto, emb_kws)[0]
                        mejor_kw_idx = int(sims_kws.argmax())
                        mejor_kw = keywords[mejor_kw_idx]
                        mejor_kw_score = float(sims_kws[mejor_kw_idx])
                    else:
                        mejor_kw, mejor_kw_score = "(sin keywords)", 0.0

                    print(
                        f"  [EMB] Proyecto {idx_proyecto + 2}: score={score:.3f}\n"
                        f"        Fragmento : {mejor_frag}\n"
                        f"        Similar a : '{mejor_kw}' ({mejor_kw_score:.3f})\n"
                    )


def mostrar_conteos(base, descripciones, etiqueta):
    print(f"\nConteos — {etiqueta}:")
    resultados = base[list(descripciones.keys())].sum().astype(int)
    for indicador, total in resultados.items():
        print(f"  {indicador:<70} {total}")


def main():
    parser = argparse.ArgumentParser(description="Asignación de prioridades a proyectos")
    parser.add_argument("entrada", help="Archivo xlsx de entrada")
    parser.add_argument("salida", help="Archivo xlsx de salida")
    parser.add_argument(
        "--embeddings", "-e",
        metavar="INDICADOR",
        help="Activa la fase 2 (embeddings) solo para el indicador dado, ej: --embeddings 'A.1.1 Agua'"
    )
    args = parser.parse_args()

    ruta_entrada = args.entrada
    ruta_salida  = args.salida

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

    if args.embeddings and args.embeddings not in descripciones:
        print(f"El indicador '{args.embeddings}' no existe en descripciones_indicadores.json")
        sys.exit(1)

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

    # Fase 2: embeddings, solo si se pidió y solo para ese indicador
    if args.embeddings:
        descripciones_emb = {args.embeddings: descripciones[args.embeddings]}
        fase_embeddings(textos_proyectos, descripciones_emb, matches_keywords)

    base.to_excel(ruta_salida, index=False)
    print(f"\nAsignación lista en {ruta_salida}")


if __name__ == "__main__":
    main()