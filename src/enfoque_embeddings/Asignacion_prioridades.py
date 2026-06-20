import sys
import json
import pandas as pd
from sentence_transformers import SentenceTransformer, util

# Umbral de similitud para marcar un indicador como 1
# Valor entre 0 y 1, entre más alto más estricto
UMBRAL = 0.48

# Modelo preentrenado
modelo = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

def main():
    # Manejar argumentos inválidos
    if len(sys.argv) != 3:
        print("Argumentos inválidos")
        print("Uso: python3 Asignacion_prioridades.py <archivo xlsx de entrada> <archivo xlsx de salida>")
        sys.exit(1)

    ruta_entrada = sys.argv[1]
    ruta_salida  = sys.argv[2]

    # Manejar caso donde el archivo de entrada no existe
    try:
        base = pd.read_excel(ruta_entrada)
    except FileNotFoundError:
        print(f"No se puede encontrar el archivo {ruta_entrada}")
        sys.exit(1)

    # Cargar JSONs de configuración
    with open("columnas.json", encoding="utf-8") as f:
        columnas = json.load(f)

    with open("descripciones_indicadores.json", encoding="utf-8") as f:
        descripciones = json.load(f)

    # Inicializar todas las columnas de indicadores en 0
    for indicador in descripciones:
        base[indicador] = 0

    # Concatenar columnas cualitativas en un solo texto por proyecto
    # Se usa " | " como separador para que el modelo distinga los campos
    def construir_texto(row):
        partes = []
        for col in columnas["columnas_texto"]:
            if col in base.columns:
                valor = row.get(col, "")
                if isinstance(valor, str) and valor.strip():
                    # Convertir nombre columna + valor
                    partes.append(
                        f"{col}: {valor.strip()}"
                    )
        return "\n".join(partes)
    
    textos_proyectos = base.apply(construir_texto, axis=1).tolist()

    # Calcular embeddings de todos los proyectos de una sola vez
    # Esto es más eficiente que calcularlos uno por uno
    print(f"Calculando embeddings de {len(textos_proyectos)} proyectos...")
    embeddings_proyectos = modelo.encode(textos_proyectos, show_progress_bar=True, batch_size=64)

    print("Asignando pertinencias...")

    # Ciclo principal.
    # Para cada indicador calcula la similitud entre su descripción
    # y el texto de cada proyecto, y marca 1 si supera el umbral.
    for indicador, descripcion in descripciones.items():

        # Calcular embedding de la descripción del indicador
        embedding_indicador = modelo.encode(descripcion)

        # Calcular similitud coseno entre el indicador y todos los proyectos
        similitudes = util.cos_sim(embedding_indicador, embeddings_proyectos)[0]

        # Marcar 1 si la similitud supera el umbral
        base[indicador] = (similitudes >= UMBRAL).int().numpy().tolist()

    # Mostrar resultados de conteos en la consola
    resultados = base[list(descripciones.keys())].sum().astype(int)
    for indicador, total in resultados.items():
        print(f"{indicador:<70} {total}")

    # Escribir en un excel el resultado
    base.to_excel(ruta_salida, index=False)

    print(f"\nAsignación lista en {ruta_salida}")


if __name__ == "__main__":
    main()