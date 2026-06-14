import json
import re
from pathlib import Path


# Pesos por campo
# Mayor peso = más confianza en que una palabra ahí es relevante
FIELD_WEIGHTS = {
    'Nombre':               1.5,
    'Descriptores':         3.0,
    'Subtemáticas':         3.0,
    'Temáticas':            3.0,
    'Objetivo general':     2.5,
    'Objetivos específicos':2.5,
    'Descripción':          0.5,
    'Población':            2.0,
    'Modalidad':            1.0,
}


class Scorer:
    def __init__(self, json_path: str):
        with open(json_path, encoding='utf-8') as f:
            self.bibliotecas = json.load(f)

        # Pre-procesar: convertir cada lista a set de tokens normalizados
        self.kw_sets = {}
        for indicador, palabras in self.bibliotecas.items():
            self.kw_sets[indicador] = set(self._normalizar(p) for p in palabras)

    #Normalización
    def _normalizar(self, texto: str) -> str:
        """Minúsculas y sin tildes para comparación robusta."""
        texto = texto.lower().strip()
        replacements = str.maketrans('áéíóúüÁÉÍÓÚÜ', 'aeiouuAEIOUU')
        return texto.translate(replacements)

    def _tokens(self, texto: str) -> list[str]:
        """Extrae tokens de 3+ caracteres del texto."""
        if not texto or (isinstance(texto, float)):
            return []
        texto = self._normalizar(str(texto))
        return re.findall(r'[a-z]{3,}', texto)

    # Scoring
    def score_proyecto(self, row: dict) -> dict[str, float]:
        scores = {ind: 0.0 for ind in self.kw_sets}

        for field, weight in FIELD_WEIGHTS.items():
            valor = row.get(field, None)
            if valor is None or (isinstance(valor, float)):
                continue

            tokens_campo = set(self._tokens(str(valor)))  # cada kw cuenta 1 vez por campo

            for indicador, kw_set in self.kw_sets.items():
                # Buscar keywords completas O como subcadena de un token
                # Ej: "hídrico" matchea con "hidrico", "recursos hidricos" matchea "hidrico"
                matches = 0
                for kw in kw_set:
                    kw_tokens = kw.split()  # keywords pueden ser frases
                    if len(kw_tokens) == 1:
                        # keyword simple: buscar en tokens individuales
                        if kw in tokens_campo:
                            matches += 1
                    else:
                        # keyword frase: buscar en el texto completo del campo
                        texto_norm = self._normalizar(str(valor))
                        if kw in texto_norm:
                            matches += 1

                scores[indicador] += matches * weight

        return scores

    # Retorna {indicador: 0/1} usando el umbral dado.
    def predict(self, row: dict, umbral: float = 3.0) -> dict[str, int]:
        scores = self.score_proyecto(row)
        return {ind: 1 if score >= umbral else 0 for ind, score in scores.items()}

    # Aplica predict a un DataFrame completo.
    # Retorna un DataFrame con las predicciones (mismas columnas que los indicadores).
    def predict_df(self, df, umbral: float = 3.0):
        import pandas as pd
        rows = []
        for _, row in df.iterrows():
            rows.append(self.predict(row.to_dict(), umbral))
        return pd.DataFrame(rows, index=df.index)

    # Retorna un DataFrame con los scores continuos.
    def score_df(self, df):
        import pandas as pd
        rows = []
        for _, row in df.iterrows():
            rows.append(self.score_proyecto(row.to_dict()))
        return pd.DataFrame(rows, index=df.index)
