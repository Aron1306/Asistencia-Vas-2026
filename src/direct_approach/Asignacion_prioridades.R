setwd("C:/Users/User/OneDrive/Escritorio/Mineria texto prioridades")

library(dplyr)
library(tidyr)
library(readxl)

base <- read_excel("EE_EducSup_2024_UCR_VAS_12_para emparejamiento prioridades.xlsx")

data_limpio <- base %>%
  separate_rows(`I.14 (temas)`, sep = ",")

data_limpio <- data_limpio %>%
  separate_rows(`I.15 (Subtemas)`, sep = ",")

table(data_limpio$`I.14 (temas)`)

########Usando variable "I.03 (nombre proyecto)"


data_limpio <- data_limpio %>%
  mutate(
    `A.1.1 Agua` = ifelse(
      grepl("Agua |agua |río| rio| mar| recurso hídrico| cuenca", `I.03 (nombre proyecto)`, ignore.case = TRUE),1,0)
  )

data_limpio <- data_limpio %>%
  mutate(
    `A.1.2 Suelo` = ifelse(
      grepl("Suelo |tierra |Tierra |suelo", `I.03 (nombre proyecto)`, ignore.case = TRUE),1,0)
  )

data_limpio <- data_limpio %>%
  mutate(
    `A.1.3 Ambiente, Descarbonización y Residuos` = ifelse(
      grepl("Ambiente| medio ambiente| Descarbonización|descarbonización| carbono neutralidad| Residuos|residuos| residuos sólidos| basura| manejo de desechos| naturaleza| carbono neutral", `I.03 (nombre proyecto)`, ignore.case = TRUE),1,0)
  )

data_limpio <- data_limpio %>%
  mutate(
    `A.2.1 Salud` = ifelse(
      grepl("Salud| salud humana| enfermedad| nutrición| salud", `I.03 (nombre proyecto)`, ignore.case = TRUE),1,0)
  )

data_limpio <- data_limpio %>%
  mutate(
    `A.2.2 Educación` = ifelse(
      grepl("Educación| educación primaria| educación secundaria| educación terciaria| educación técnica| educación preescolar| educación universitaria| formación profesional| educación de adultos| educación continua", `I.03 (nombre proyecto)`, ignore.case = TRUE),1,0)
  )

data_limpio <- data_limpio %>%
  mutate(
    `A.2.3 Cultura` = ifelse(
      grepl("Cultura| arte| música| danza| artes plásticas| bellas artes| patrimonio cultural| patrimonio arquitectónico| patrimonio arqueológico", `I.03 (nombre proyecto)`, ignore.case = TRUE),1,0)
  )

data_limpio <- data_limpio %>%
  mutate(
    `A.3.1 Ciencia, Tecnología e Innovación` = ifelse(
      grepl("Ciencia| Tecnología| tecnología| innovación| ciencia   | Innovación| investigación y desarrollo| creatividad", `I.03 (nombre proyecto)`, ignore.case = TRUE),1,0)
  )

data_limpio <- data_limpio %>%
  mutate(
    `A.3.2 Transportes` = ifelse(
      grepl("Transporte| transporte terrestre| transporte marítimo| transporte aéreo| infraestructura de transporte|transporte", `I.03 (nombre proyecto)`, ignore.case = TRUE),1,0)
  )

data_limpio <- data_limpio %>%
  mutate(
    `A.3.3 Vivienda y Hábitat` = ifelse(
      grepl("Vivienda| hábitat| ciudad| desarrollo urbano| urbanización| precarios| asentamientos informales| ordenamiento territorial| planes reguladores", `I.03 (nombre proyecto)`, ignore.case = TRUE),1,0)
  )

data_limpio <- data_limpio %>%
  mutate(
    `A.4.1 Empleo` = ifelse(
      grepl("Empleo| desempleo| subempleo| salarios| empleo informal| empleo| salario", `I.03 (nombre proyecto)`, ignore.case = TRUE),1,0)
  )

data_limpio <- data_limpio %>%
  mutate(
    `A.4.2 Pobreza` = ifelse(
      grepl("Pobreza| pobreza urbana| pobreza rural| pobreza", `I.03 (nombre proyecto)`, ignore.case = TRUE),1,0)
  )

data_limpio <- data_limpio %>%
  mutate(
    `A.4.3 Desarrollo Regional` = ifelse(
      grepl("desarrollo regional| desarrollo local| desarrollo territorial", `I.03 (nombre proyecto)`, ignore.case = TRUE),1,0)
  )

data_limpio <- data_limpio %>%
  mutate(
    `A.4.4 Agropecuario` = ifelse(
      grepl("Agropecuario| agricultura| agroalimentario| agropecuario|Agro ", `I.03 (nombre proyecto)`, ignore.case = TRUE),1,0)
  )

data_limpio <- data_limpio %>%
  mutate(
    `B.1.1 Pobreza` = ifelse(
      grepl("Pobreza| pobreza urbana| pobreza rural| pobreza", `I.03 (nombre proyecto)`, ignore.case = TRUE),1,0)
  )

data_limpio <- data_limpio %>%
  mutate(
    `B.1.2 Alimentación sostenible en zonas costeras` = ifelse(
      grepl("desnutrición| nutrición", `I.03 (nombre proyecto)`, ignore.case = TRUE),1,0)
  )

data_limpio <- data_limpio %>%
  mutate(
    `B.1.3 Planes Reguladores` = ifelse(
      grepl("Planes reguladores| ordenamiento territorial", `I.03 (nombre proyecto)`, ignore.case = TRUE),1,0)
  )

data_limpio <- data_limpio %>%
  mutate(
    `B.2.1 Salud` = ifelse(
      grepl("Salud| salud humana| enfermedad| nutrición| desnutrición", `I.03 (nombre proyecto)`, ignore.case = TRUE),1,0)
  )

data_limpio <- data_limpio %>%
  mutate(
    `B.2.2 Embarazos adolescentes` = ifelse(
      grepl("Embarazos adolescentes|Embarazo adolescente", `I.03 (nombre proyecto)`, ignore.case = TRUE),1,0)
  )

data_limpio <- data_limpio %>%
  mutate(
    `B.2.3 Igualdad de genero` = ifelse(
      grepl("igualdad de género| brechas de género|desigualdad de género", `I.03 (nombre proyecto)`, ignore.case = TRUE),1,0)
  )

data_limpio <- data_limpio %>%
  mutate(
    `B.3.1 Agua` = ifelse(
      grepl("Agua| agua potable| acueductos", `I.03 (nombre proyecto)`, ignore.case = TRUE),1,0)
  )

data_limpio <- data_limpio %>%
  mutate(
    `B.3.2 Energía` = ifelse(
      grepl("Energía|energía eólica| energía hidroeléctrica| energía geotérmina| energía solar| solar| geotérmica| hidroeléctrica| eólica", `I.03 (nombre proyecto)`, ignore.case = TRUE),1,0)
  )

data_limpio <- data_limpio %>%
  mutate(
    `B.4.1 Trabajo digno` = ifelse(
      grepl("trabajo| trabajo digno| trabajo decente| derechos laborales", `I.03 (nombre proyecto)`, ignore.case = TRUE),1,0)
  )

data_limpio <- data_limpio %>%
  mutate(
    `B.4.2 Industrialización inclusiva` = ifelse(
      grepl("Industrialización|Industrialización inclusiva", `I.03 (nombre proyecto)`, ignore.case = TRUE),1,0)
  )

data_limpio <- data_limpio %>%
  mutate(
    `B.4.3 Innovación` = ifelse(
      grepl("Innovación| innovación productiva| creatividad", `I.03 (nombre proyecto)`, ignore.case = TRUE),1,0)
  )

data_limpio <- data_limpio %>%
  mutate(
    `B.4.4 Desigualdad` = ifelse(
      grepl("Desigualdad| equidad| desigualdad de ingresos", `I.03 (nombre proyecto)`, ignore.case = TRUE),1,0)
  )

data_limpio <- data_limpio %>%
  mutate(
    `B.5.1 Comunicación vial` = ifelse(
      grepl("infraestructura vial| Comunicación vial", `I.03 (nombre proyecto)`, ignore.case = TRUE),1,0)
  )

data_limpio <- data_limpio %>%
  mutate(
    `B.5.2 Urbanismo` = ifelse(
      grepl("Urbanismo| desarrollo urbano", `I.03 (nombre proyecto)`, ignore.case = TRUE),1,0)
  )

data_limpio <- data_limpio %>%
  mutate(
    `B.5.3 Contaminación` = ifelse(
      grepl("Contaminaión| descontaminación", `I.03 (nombre proyecto)`, ignore.case = TRUE),1,0)
  )

data_limpio <- data_limpio %>%
  mutate(
    `B.5.4 Ambiente y Mares` = ifelse(
      grepl("Ambiente| medio ambiente| mares| costas| marinos", `I.03 (nombre proyecto)`, ignore.case = TRUE),1,0)
  )

data_limpio <- data_limpio %>%
  mutate(
    `B.5.5 Justicia institucional` = ifelse(
      grepl("Justicia| Justicia institucional", `I.03 (nombre proyecto)`, ignore.case = TRUE),1,0)
  )

data_limpio <- data_limpio %>%
  mutate(
    `C.1.1 Desarrollo humano integral` = ifelse(
      grepl("Desarrollo humano| desarrollo social", `I.03 (nombre proyecto)`, ignore.case = TRUE),1,0)
  )

data_limpio <- data_limpio %>%
  mutate(
    `C.1.2 Costas y zonas fronterizas` = ifelse(
      grepl("Costas| zonas costeras| fronteras| zonas fronterizas", `I.03 (nombre proyecto)`, ignore.case = TRUE),1,0)
  )


data_limpio <- data_limpio %>%
  mutate(
    `C.2.1 Infraestructura Vial y Educativa` = ifelse(
      grepl("infraestructura vial| infraestructura educativa| educación vial", `I.03 (nombre proyecto)`, ignore.case = TRUE),1,0)
  )

data_limpio <- data_limpio %>%
  mutate(
    `C.2.2 Logística (multimodal)` = ifelse(
      grepl("Logística| corredores logísticos", `I.03 (nombre proyecto)`, ignore.case = TRUE),1,0)
  )

data_limpio <- data_limpio %>%
  mutate(
    `C.1.2 Costas y zonas fronterizas` = ifelse(
      grepl("Costas| zonas costeras| fronteras| zonas fronterizas", `I.03 (nombre proyecto)`, ignore.case = TRUE),1,0)
  )

data_limpio <- data_limpio %>%
  mutate(
    `C.3.1 Educación` = ifelse(
      grepl("Educación| educación primaria| ducación secundaria| educación terciaria| educación técnica| educación preescolar| educación universitaria| formación profesional| educación de adultos| educación continua", `I.03 (nombre proyecto)`, ignore.case = TRUE),1,0)
  )

data_limpio <- data_limpio %>%
  mutate(
    `C.3.2 Innovación` = ifelse(
      grepl("Innovación educativa", `I.03 (nombre proyecto)`, ignore.case = TRUE),1,0)
  )

data_limpio <- data_limpio %>%
  mutate(
    `C.4.1 Género` = ifelse(
      grepl("igualdad de género| desigualdad de género| brechas de género", `I.03 (nombre proyecto)`, ignore.case = TRUE),1,0)
  )

data_limpio <- data_limpio %>%
  mutate(
    `C.4.2 Salud` = ifelse(
      grepl("Salud| salud humana| enfermedad| nutrición", `I.03 (nombre proyecto)`, ignore.case = TRUE),1,0)
  )

data_limpio <- data_limpio %>%
  mutate(
    `C.4.3 Pobreza` = ifelse(
      grepl("Pobreza| pobreza urbana| pobreza rural", `I.03 (nombre proyecto)`, ignore.case = TRUE),1,0)
  )

data_limpio <- data_limpio %>%
  mutate(
    `C.5.1 Economía verde` = ifelse(
      grepl("Economía verde| economía ambiental", `I.03 (nombre proyecto)`, ignore.case = TRUE),1,0)
  )

data_limpio <- data_limpio %>%
  mutate(
    `C.5.2 Producción sofisticada` = ifelse(
      grepl("Producción| productividad", `I.03 (nombre proyecto)`, ignore.case = TRUE),1,0)
  )

data_limpio <- data_limpio %>%
  mutate(
    `C.5.3 Desigualdad` = ifelse(
      grepl("Desigualdad| equidad| desigualdad de ingresos", `I.03 (nombre proyecto)`, ignore.case = TRUE),1,0)
  )

data_limpio <- data_limpio %>%
  mutate(
    `C.6.1 Economía regenerativa` = ifelse(
      grepl("Economía regenerativa", `I.03 (nombre proyecto)`, ignore.case = TRUE),1,0)
  )

data_limpio <- data_limpio %>%
  mutate(
    `D.1.1 Descentralizada` = ifelse(
      grepl("Descentralización", `I.03 (nombre proyecto)`, ignore.case = TRUE),1,0)
  )

data_limpio <- data_limpio %>%
  mutate(
    `D.1.2 Digitalizada` = ifelse(
      grepl("Digitalización| brecha digital| acceso tecnología", `I.03 (nombre proyecto)`, ignore.case = TRUE),1,0)
  )

data_limpio <- data_limpio %>%
  mutate(
    `D.1.3 Descarbonizada` = ifelse(
      grepl("Descarbonizada| carbono neutralidad| cero emisiones", `I.03 (nombre proyecto)`, ignore.case = TRUE),1,0)
  )

data_limpio <- data_limpio %>%
  mutate(
    `D.2.1 Productividad laboral` = ifelse(
      grepl("Productividad laboral", `I.03 (nombre proyecto)`, ignore.case = TRUE),1,0)
  )

data_limpio <- data_limpio %>%
  mutate(
    `D.2.2 Sofisticación` = ifelse(
      grepl("Sofisticación", `I.03 (nombre proyecto)`, ignore.case = TRUE),1,0)
  )

data_limpio <- data_limpio %>%
  mutate(
    `D.2.3 Desconcentración e innovación productiva` = ifelse(
      grepl("Desconcentración productiva| innovación productiva", `I.03 (nombre proyecto)`, ignore.case = TRUE),1,0)
  )

data_limpio <- data_limpio %>%
  mutate(
    `E.1.1 Regulación Urbana` = ifelse(
      grepl("regulación urbana| planes reguladores| ordenamiento territorial", `I.03 (nombre proyecto)`, ignore.case = TRUE),1,0)
  )

data_limpio <- data_limpio %>%
  mutate(
    `E.1.2 Gestión municipal` = ifelse(
      grepl("gestión municipal| municipalidades| municipal| gobiernos locales", `I.03 (nombre proyecto)`, ignore.case = TRUE),1,0)
  )

data_limpio <- data_limpio %>%
  mutate(
    `E.2.1 Pobreza` = ifelse(
      grepl("Pobreza| pobreza urbana| pobreza rural", `I.03 (nombre proyecto)`, ignore.case = TRUE),1,0)
  )

data_limpio <- data_limpio %>%
  mutate(
    `E.2.2 Desempleo` = ifelse(
      grepl("Desempleo", `I.03 (nombre proyecto)`, ignore.case = TRUE),1,0)
  )

data_limpio <- data_limpio %>%
  mutate(
    `E.2.3 Inseguridad Ciudadana` = ifelse(
      grepl("Inseguridad| violencia| delitos| crímenes", `I.03 (nombre proyecto)`, ignore.case = TRUE),1,0)
  )

data_limpio <- data_limpio %>%
  mutate(
    `E.3.1 Protección Recurso Hídrico` = ifelse(
      grepl("Agua| río| mar| recurso hídrico| cuenca", `I.03 (nombre proyecto)`, ignore.case = TRUE),1,0)
  )

data_limpio <- data_limpio %>%
  mutate(
    `E.3.2 Suelo` = ifelse(
      grepl("Suelo| tierra", `I.03 (nombre proyecto)`, ignore.case = TRUE),1,0)
  )

data_limpio <- data_limpio %>%
  mutate(
    `E.4.1 Inversión en capital` = ifelse(
      grepl("Inversión de capital| inversión en infraestructura| formación de capital", `I.03 (nombre proyecto)`, ignore.case = TRUE),1,0)
  )
data_limpio <- data_limpio %>%
  mutate(
    `E.4.2 Gestión regional de recursos` = ifelse(
      grepl("Gestión regional de recursos", `I.03 (nombre proyecto)`, ignore.case = TRUE),1,0)
  )
data_limpio <- data_limpio %>%
  mutate(
    `E.5.1 Accesibilidad` = ifelse(
      grepl("Accesibilidad", `I.03 (nombre proyecto)`, ignore.case = TRUE),1,0)
  )
data_limpio <- data_limpio %>%
  mutate(
    `E.5.2 Conectividad` = ifelse(
      grepl("Conectividad", `I.03 (nombre proyecto)`, ignore.case = TRUE),1,0)
  )
data_limpio <- data_limpio %>%
  mutate(
    `E.6.1 Brecha Servicios de Salud` = ifelse(
      grepl("Brecha de servicios de Salud| brechas de salud|Servicios de Salud ", `I.03 (nombre proyecto)`, ignore.case = TRUE),1,0)
  )
data_limpio <- data_limpio %>%
  mutate(
    `E.6.2 Brecha Servicios de Educación` = ifelse(
      grepl("Brecha de servicios de Educación| brechas de educación|servicios de Educación ", `I.03 (nombre proyecto)`, ignore.case = TRUE),1,0)
  )

########Usando variable "I.14 (temas)"
data_limpio <- data_limpio %>%
  mutate(
    `F.1.1 Bienestar nacional global` = ifelse(
      grepl("5/Socioproductividad |6/Derechos humanos", `I.14 (temas)`, ignore.case = TRUE),1,0)
  )


colSums(data_limpio[,7:69])


########Usando variable "I.15 (Subtemas)"
data_limpio <- data_limpio %>%
  mutate(
    `B.1.2 Alimentación sostenible en zonas costeras` = case_when(
      grepl("5/Nutrici on saludable", `I.15 (Subtemas)`, ignore.case = TRUE) ~ 1,
      TRUE ~ `B.1.2 Alimentación sostenible en zonas costeras`)
  )
