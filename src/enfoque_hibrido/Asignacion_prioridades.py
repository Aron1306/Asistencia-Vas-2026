import sys
import json
import re
import pandas as pd
import unicodedata
import argparse

def normalizar(texto):
    texto = texto.lower()
    texto = unicodedata.normalize("NFD", texto)
    texto = "".join(c for c in texto if unicodedata.category(c) != "Mn")
    return texto

DEBUG = True


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
    Busca palabras clave exactas en el texto de cada proyecto.
    Marca 1 donde hay coincidencia.
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


def mostrar_conteos(base, descripciones, etiqueta):
    print(f"\nConteos — {etiqueta}:")
    resultados = base[list(descripciones.keys())].sum().astype(int)
    for indicador, total in resultados.items():
        print(f"  {indicador:<70} {total}")


def main():
    parser = argparse.ArgumentParser(
        description="Asignación de prioridades a proyectos (Fase 1: keywords)"
    )
    parser.add_argument("entrada", help="Archivo xlsx de entrada")
    parser.add_argument("salida", help="Archivo xlsx de salida")
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
    fase_keywords(base, textos_proyectos, descripciones)
    mostrar_conteos(base, descripciones, "después de keywords")

    base.to_excel(ruta_salida, index=False)
    print(f"\nAsignación lista en {ruta_salida}")


if __name__ == "__main__":
    main()