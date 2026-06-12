library(dplyr)
library(tidyr)
library(readxl)
library(jsonlite)
library(stringi)
library(writexl)

# Archivo JSON con las posibles columnas cualitivas registradas
columnas <- fromJSON("columnas.json")

# Archivo JSON con keywords de los diferentes indicadores
keywords <- fromJSON("keywords_indicadores.json")

args <- commandArgs(trailingOnly = TRUE)
ruta_entrada <- args[1] # Path al archivo xlsx de entrada recibido desde línea de comandos
ruta_salida <- args[2]  # Nombre del archivo xlsx de salida donde se guardarán los resultados
base <- read_excel(ruta_entrada)

# Procesar el texto para quitar tíldes y convertir todo el texto en minúsculas
normalizar <- function(texto) {
  texto <- stri_trans_general(texto, "Latin-ASCII")  # quita tildes
  texto <- tolower(texto)                             # minúsculas
  return(texto)
}

# Inicializar todas las columnas de indicadores.
# Se inicializan de manera previa ya que un indicador puede no contar con keywords
# haciendo que el ciclo principal lo salte y no lo inicialice.
for (indicador in names(keywords)) {
  base[[indicador]] <- 0
}

# Ciclo principal. 
# Recorre los keywords de los diferentes indicadores definidos en "keywords_indicadores.json"
# buscando coincidencias en cualquiera de las columnas registradas en "columnas.json" que 
# puedan aparecer en el archivo de entrada "ruta_entrada" almacenado en "base".
for (indicador in names(keywords)) {
  kws <- keywords[[indicador]]

  # Si un indicador no cuenta con pertinencias asociadas, pasa al siguiente
  if (length(kws) == 0) next

  # Estructura con todas las keywords en formato regex separadas por "|"
  # que causa que solo se haga match si es la palabra exacta
  patron <- paste0("\\b", kws, "\\b", collapse = "|")

  patron <- normalizar(patron)
  
  # Empezar con todos en 0
  match_final <- rep(0, nrow(base))
  
  # Iterar sobre las columnas cualitativas
  for (cualitativa in columnas$columnas_texto) {

    # Si la columna cualitativa no existe, pasa a la siguiente
    if (!cualitativa %in% names(base)) next

    texto_normalizado <- normalizar(base[[cualitativa]])
    
    # Busca coincidencias de las keywords en el texto
    match_col <- ifelse(
      grepl(patron, texto_normalizado, ignore.case = TRUE), 1, 0
    )

    # Si alguna columna da 1, el resultado es 1
    match_final <- pmax(match_final, match_col)
  }
  
  base[[indicador]] <- match_final
}

# Mostrar resultados de conteos en la consola
print(colSums(base[, names(keywords)], na.rm = TRUE))

# Escribir en un excel el resultado
write_xlsx(base, ruta_salida)

# Indicar donde se guardó las pertinencias asignadas
cat("Asignación lista en", ruta_salida, "\n")