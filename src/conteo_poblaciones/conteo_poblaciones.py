import requests
import json
import re
import pandas as pd
import argparse
import time


OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "gemma4:12b"

COLUMNAS_PROYECTO = [
    "Beneficios para la UCR",
    "Beneficios para la población",
    "Beneficiarios según propuesta de proyecto",
    "Población"
]


def construir_proyecto(fila):
    partes = []

    for columna in COLUMNAS_PROYECTO:
        valor = fila[columna]

        if pd.notna(valor) and str(valor).strip():
            partes.append(f"{columna}: {valor}")

    return "\n".join(partes)


def cargar_beneficiados(ruta):
    with open(ruta, "r", encoding="utf-8") as archivo:
        config = json.load(archivo)

    return config["beneficiados"]


def preguntar_ollama(prompt: str) -> str:
    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "think": False,
            "stream": False,
            "options": {
                "temperature": 0,
                "seed": 42
            }
        },
        timeout=600
    )

    response.raise_for_status()

    return response.json()["message"]["content"]


def limpiar_respuesta_json(respuesta: str):
    """
    Extrae el JSON aunque Ollama lo devuelva dentro de ```json ... ```.
    """

    respuesta = respuesta.strip()

    if respuesta.startswith("```"):
        respuesta = re.sub(r"^```(?:json)?\s*", "", respuesta)
        respuesta = re.sub(r"\s*```$", "", respuesta)

    return respuesta.strip()


def cargar_prompt(ruta):
    with open(ruta, "r", encoding="utf-8") as archivo:
        return archivo.read()


def crear_prompt(plantilla, proyecto, etiquetas):
    return (
        plantilla
        .replace("<<<ETIQUETAS>>>", "\n".join(etiquetas))
        .replace("<<<PROYECTO>>>", proyecto)
    )


def procesar_respuesta(respuesta, poblaciones_predefinidas, archivo_log):
    """
    Procesa el JSON devuelto por Ollama.

    Formato esperado:

    {
        "poblacion": [
            "Estudiantes",
            "Docentes"
        ]
    }

    Las poblaciones que no existan en el catálogo son ignoradas
    y registradas en el log.
    """

    respuesta = limpiar_respuesta_json(respuesta)

    datos = json.loads(respuesta)

    if not isinstance(datos, dict):
        raise ValueError(
            "La respuesta de Ollama no contiene un objeto JSON."
        )

    poblaciones = datos.get("poblacion")

    if poblaciones is None:
        raise ValueError(
            'La respuesta JSON no contiene la clave "poblacion".'
        )

    if not isinstance(poblaciones, list):
        raise ValueError(
            'La clave "poblacion" no contiene una lista.'
        )

    poblaciones_proyecto = set()

    for poblacion in poblaciones:

        if not isinstance(poblacion, str):
            archivo_log.write(
                "ADVERTENCIA: Ollama devolvió una población "
                "que no es texto. Se ignora.\n"
            )
            continue

        nombre = poblacion.strip()

        if not nombre:
            continue

        if nombre in poblaciones_proyecto:
            continue

        if nombre not in poblaciones_predefinidas:
            archivo_log.write(
                f"ADVERTENCIA: Ollama devolvió una población "
                f"que no está en el catálogo: {nombre}\n"
            )
            continue

        poblaciones_proyecto.add(nombre)

    return poblaciones_proyecto


def guardar_conteos(df, poblaciones, ruta_salida):
    """
    Calcula los conteos a partir de las columnas binarias
    y los guarda en un archivo de texto.
    """

    with open(ruta_salida, "w", encoding="utf-8") as archivo:
        for poblacion in poblaciones:
            conteo = int(df[poblacion].sum())
            archivo.write(f"{poblacion}: {conteo}\n")


def main():
    inicio = time.perf_counter()

    parser = argparse.ArgumentParser(
        description="Procesa proyectos de un Excel utilizando Ollama."
    )

    parser.add_argument(
        "excel",
        help="Ruta al archivo Excel (.xlsx)"
    )

    parser.add_argument(
        "--debug",
        type=int,
        default=0,
        help="Cantidad de proyectos a procesar. 0 = todos."
    )

    parser.add_argument(
        "--salida",
        default="proyectos_clasificados.xlsx",
        help="Archivo Excel donde se guardará el resultado."
    )

    parser.add_argument(
        "--conteos",
        default="conteo_poblaciones.txt",
        help="Archivo de texto donde se guardarán los conteos."
    )

    parser.add_argument(
        "--log",
        default="log.txt",
        help="Archivo de texto donde se guardará el detalle del procesamiento."
    )

    args = parser.parse_args()

    poblaciones_predefinidas = cargar_beneficiados(
        "beneficiados.json"
    )

    plantilla_prompt = cargar_prompt("prompt.txt")

    etiquetas = list(poblaciones_predefinidas)

    with open(args.log, "w", encoding="utf-8") as archivo_log:

        archivo_log.write(
            f"Excel de entrada: {args.excel}\n"
        )
        archivo_log.write(
            f"Modelo: {MODEL}\n"
        )
        archivo_log.write("\n")

        print(f"Leyendo Excel: {args.excel}")

        df = pd.read_excel(
            args.excel,
            skiprows=[1]
        )

        total_proyectos = len(df)

        if args.debug > 0:
            cantidad = min(args.debug, total_proyectos)
            df = df.head(cantidad).copy()
        else:
            cantidad = total_proyectos

        print(f"Proyectos encontrados: {total_proyectos}")
        print(f"Proyectos a procesar: {cantidad}")
        print()

        archivo_log.write(
            f"Proyectos encontrados: {total_proyectos}\n"
        )

        archivo_log.write(
            f"Proyectos a procesar: {cantidad}\n\n"
        )

        for poblacion in poblaciones_predefinidas:
            df[poblacion] = 0

        for posicion, (indice, fila) in enumerate(
            df.iterrows(),
            start=1
        ):
            print(
                f"Procesando proyecto {posicion}/{cantidad}..."
            )

            archivo_log.write("=" * 70 + "\n")
            archivo_log.write(
                f"Procesando proyecto {posicion}/{cantidad}\n"
            )
            archivo_log.write("-" * 70 + "\n")

            proyecto = construir_proyecto(fila)

            if not proyecto.strip():
                print("  Proyecto vacío. Se omite.")

                archivo_log.write(
                    "Proyecto vacío. Se omite.\n\n"
                )
                continue

            archivo_log.write(proyecto)
            archivo_log.write("\n")
            archivo_log.write("-" * 70 + "\n")

            prompt = crear_prompt(
                plantilla_prompt,
                proyecto,
                etiquetas
            )

            try:
                respuesta = preguntar_ollama(prompt)

                archivo_log.write(
                    "RESPUESTA DE OLLAMA:\n"
                )
                archivo_log.write(respuesta)
                archivo_log.write("\n")

                poblaciones_proyecto = procesar_respuesta(
                    respuesta,
                    poblaciones_predefinidas,
                    archivo_log
                )

                for poblacion in poblaciones_proyecto:
                    df.at[indice, poblacion] = 1

                archivo_log.write(
                    "Respuesta procesada correctamente.\n\n"
                )

            except json.JSONDecodeError as error:
                print(
                    "  ERROR: Ollama no devolvió JSON válido."
                )

                archivo_log.write(
                    "ERROR: Ollama no devolvió JSON válido.\n"
                )
                archivo_log.write(
                    f"Detalle: {error}\n"
                )
                archivo_log.write(
                    "Respuesta recibida:\n"
                )
                archivo_log.write(
                    respuesta
                )
                archivo_log.write("\n\n")

            except requests.RequestException as error:
                print(
                    "  ERROR de conexión con Ollama."
                )

                archivo_log.write(
                    "ERROR de conexión con Ollama.\n"
                )
                archivo_log.write(
                    f"{error}\n\n"
                )

            except Exception as error:
                print(
                    "  ERROR procesando el proyecto."
                )

                archivo_log.write(
                    "ERROR procesando el proyecto.\n"
                )
                archivo_log.write(
                    f"{error}\n\n"
                )

        df.to_excel(
            args.salida,
            index=False
        )

        guardar_conteos(
            df,
            poblaciones_predefinidas,
            args.conteos
        )

        archivo_log.write("=" * 70 + "\n")
        archivo_log.write(
            "Procesamiento terminado.\n"
        )

        archivo_log.write(
            f"Excel guardado en: {args.salida}\n"
        )

        archivo_log.write(
            f"Conteos guardados en: {args.conteos}\n"
        )

        archivo_log.write(
            f"Log guardado en: {args.log}\n"
        )

        archivo_log.write("\n")
        archivo_log.write("CONTEOS:\n")

        for poblacion in poblaciones_predefinidas:
            conteo = int(df[poblacion].sum())

            if conteo > 0:
                archivo_log.write(
                    f"{poblacion}: {conteo}\n"
                )

    fin = time.perf_counter()
    duracion = fin - inicio

    horas = int(duracion // 3600)
    minutos = int((duracion % 3600) // 60)
    segundos = duracion % 60

    tiempo_formateado = (
        f"{horas:02d}:{minutos:02d}:{segundos:05.2f}"
    )

    print()
    print("Procesamiento terminado.")
    print(f"Excel guardado en: {args.salida}")
    print(f"Conteos guardados en: {args.conteos}")
    print(f"Log guardado en: {args.log}")
    print(f"Tiempo total: {tiempo_formateado}")


if __name__ == "__main__":
    main()