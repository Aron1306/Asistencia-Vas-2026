library(dplyr)
library(tidyr)
library(readxl)
library(jsonlite)
library(stringi)
library(writexl)

columnas <- fromJSON("columnas.json")
keywords <- fromJSON("keywords_indicadores.json")

args <- commandArgs(trailingOnly = TRUE)
ruta_excel <- args[1]
base <- read_excel(ruta_excel)

normalizar <- function(texto) {
  texto <- stri_trans_general(texto, "Latin-ASCII")  # quita tildes
  texto <- tolower(texto)                             # minúsculas
  return(texto)
}

for (indicador in names(keywords)) {
  kws <- keywords[[indicador]]
  patron <- paste0("(^|\\s)", kws, "(\\s|$|[^a-z])", collapse = "|")
  patron <- normalizar(patron)
  
  # Empezar con todos en 0
  match_final <- rep(0, nrow(base))
  
  for (cualitativa in columnas$columnas_texto) {
    if (!cualitativa %in% names(base)) next

    texto_normalizado <- normalizar(base[[cualitativa]])
    
    match_col <- ifelse(
      grepl(patron, texto_normalizado, ignore.case = TRUE), 1, 0
    )
    # Si alguna columna da 1, el resultado es 1
    match_final <- pmax(match_final, match_col)
  }
  
  base[[indicador]] <- match_final
}

print(colSums(base[, names(keywords)], na.rm = TRUE))