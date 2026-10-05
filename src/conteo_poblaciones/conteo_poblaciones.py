import requests
import json
import re
import pandas as pd
import argparse


OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "qwen3.5:9b"

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
                "temperature": 0
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

def procesar_respuesta(respuesta, conteos):
    """
    Procesa el JSON devuelto por Ollama y actualiza los conteos.
    """

    respuesta = limpiar_respuesta_json(respuesta)

    datos = json.loads(respuesta)

    if not isinstance(datos, list):
        raise ValueError("La respuesta de Ollama no contiene una lista JSON.")

    poblaciones_proyecto = set()

    for poblacion in datos:
        nombre = poblacion.get("poblacion")

        if not nombre:
            continue

        nombre = nombre.strip()

        # Evitar contar dos veces la misma población
        # dentro del mismo proyecto.
        if nombre in poblaciones_proyecto:
            continue

        poblaciones_proyecto.add(nombre)

        # Solo se aceptan categorías del catálogo.
        if nombre in conteos:
            conteos[nombre]["conteo"] += 1
            continue

        print(
            f"ADVERTENCIA: Ollama devolvió una población "
            f"que no está en el catálogo: {nombre}"
        )


def guardar_resultado(conteos, ruta_salida):
    """
    Guarda el conteo de las poblaciones del catálogo.
    """

    resultado = {
        "beneficiados": []
    }

    for nombre, datos in conteos.items():
        resultado["beneficiados"].append({
            "poblacion": nombre,
            "conteo": datos["conteo"]
        })

    with open(ruta_salida, "w", encoding="utf-8") as archivo:
        json.dump(
            resultado,
            archivo,
            ensure_ascii=False,
            indent=4
        )


def main():
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
        default="conteo_poblaciones.json",
        help="Archivo JSON donde se guardará el resultado."
    )

    args = parser.parse_args()

    # Cargar catálogo de poblaciones
    poblaciones_predefinidas = cargar_beneficiados("beneficiados.json")

    plantilla_prompt = cargar_prompt("prompt.txt")

    etiquetas = list(poblaciones_predefinidas)

    # Crear estructura de conteos
    conteos = {
        poblacion: {
            "conteo": 0
        }
        for poblacion in poblaciones_predefinidas
    }

    # Leer Excel
    print(f"Leyendo Excel: {args.excel}")

    df = pd.read_excel(args.excel, skiprows=[1])

    total_proyectos = len(df)

    if args.debug > 0:
        cantidad = min(args.debug, total_proyectos)
        df = df.head(cantidad)
    else:
        cantidad = total_proyectos

    print(f"Proyectos encontrados: {total_proyectos}")
    print(f"Proyectos a procesar: {cantidad}")
    print()

    # Procesar proyectos uno por uno
    for indice, (_, fila) in enumerate(df.iterrows(), start=1):

        print("=" * 70)
        print(f"Procesando proyecto {indice}/{cantidad}")

        proyecto = construir_proyecto(fila)

        if not proyecto.strip():
            print("Proyecto vacío. Se omite.")
            continue

        print("-" * 70)
        print(proyecto)
        print("-" * 70)

        prompt = crear_prompt(
            plantilla_prompt,
            proyecto,
            etiquetas
        )

        try:
            respuesta = preguntar_ollama(prompt)

            print(respuesta)

            procesar_respuesta(
                respuesta,
                conteos
            )

            print("Respuesta procesada correctamente.")

        except json.JSONDecodeError as error:
            print("ERROR: Ollama no devolvió JSON válido.")
            print(f"Detalle: {error}")
            print("Respuesta recibida:")
            print(respuesta)

        except requests.RequestException as error:
            print("ERROR de conexión con Ollama.")
            print(error)

        except Exception as error:
            print("ERROR procesando el proyecto.")
            print(error)

    # Guardar resultados
    guardar_resultado(
        conteos,
        args.salida
    )

    print()
    print("=" * 70)
    print("Procesamiento terminado.")
    print(f"Resultado guardado en: {args.salida}")
    print()

    print("CONTEOS:")
    for nombre, datos in conteos.items():
        if datos["conteo"] > 0:
            print(f"{nombre}: {datos['conteo']}")


if __name__ == "__main__":
    main()