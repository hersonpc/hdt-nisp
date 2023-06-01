###
##
## 13 de Julho de 2017
## Author: Herson P. C. de Melo <hersonpc@gmail.com>
##
## Análise estatística das notificações de eventos adversos
## Hospital de Doenças Tropicais Dr. Anuar Auad
##
###

months <- c("Jan","Fev","Mar","Abr","Mai","Jun",
            "Jul","Ago","Set","Out","Nov","Dez")
months.fullname <- c("Janeiro","Fevereiro","Março","Abril","Maio","Junho",
                     "Julho","Agosto","Setembro","Outubro","Novembro","Dezembro")



###
## Bibliotecas necessárias
###

library(reshape2)
library(dplyr)
library(tidyr)
library(lubridate)

library(ggplot2)
library(RColorBrewer)

library(data.table)


###
## Funções auxiliares
###

trim <- function (x) gsub("^\\s+|\\s+$", "", x)
iso8859 <- function (x) iconv(trim(as.character(x)), "UTF-8", "ISO_8859-2")

###
## Definindo fonte da origem dos dados
###

# Link para visualização dos dados https://docs.google.com/spreadsheets/d/1uP1yIENzwkEJPH7xIMm-eWVV_p40qOI3mvZd3-L4gqw/edit?usp=sharing
url.google.forms.eventos_adversos.csv = "https://docs.google.com/spreadsheets/d/1uP1yIENzwkEJPH7xIMm-eWVV_p40qOI3mvZd3-L4gqw/pub?gid=0&single=true&output=csv"
url.google.forms.farmacovigilancia.csv = "https://docs.google.com/spreadsheets/d/1Kn-G_wO1o1nrSMI5_pOkPHhG46vJsZFoS2PjKMfpHYk/pub?gid=0&single=true&output=csv"
url.google.forms.hemovigilancia.csv = "https://docs.google.com/spreadsheets/d/1SN_6-71PD6Ay94hh2nNAsfcTnF_-al_sqN86eT21Mqs/pub?gid=0&single=true&output=csv"


###
## Obtendo dados
###


# raw.data.nisp <- read.csv(url.google.forms.eventos_adversos.csv)
# raw.data.farmacovigilancia <- read.csv(url.google.forms.farmacovigilancia.csv)
# raw.data.hemovigilancia <- read.csv(url.google.forms.hemovigilancia.csv)
# 
#
# raw1 <- raw.data.nisp %>% filter(nchar(trim(as.character(Data))) >= 10) %>% select(data = Data, turno = Turno, setor = Setor, tipo = Tipo.de.incidente, 'subtipo' = Subtipo.Incidente, grau_dano = Grau.de.Dano, lesao_pele = LesÃ.o.de.Pele.â...Causa, classificacao_up = ClassificaÃ.Ã.o.da.UP, tipo_queda = Tipo.de.Queda, extubacao = ExtubaÃ.Ã.o, perda_sne = Perda.de.SNE, sexo = Sexo, cor = Cor, comunicante = who...quem.comunicou)
# raw2 <- raw.data.farmacovigilancia %>% filter(nchar(trim(as.character(Data))) >= 10) %>% select(data = Data, turno = Turno, setor = Setor, tipo = Tipo.de.incidente, subtipo = Subtipo.Incidente, grau_dano = Grau.de.Dano, medicamento = Incidente.Medicamento, sexo = Sexo, cor = Cor, comunicante = Comunicante)
# raw3 <- raw.data.hemovigilancia %>% filter(nchar(trim(as.character(Data))) >= 10) %>% select(data = Data, turno = Turno, setor = Setor, tipo = Tipo.de.incidente, subtipo = Subtipo, grau_dano = Grau.de.Dano, reacao_trasnfusional = Tipo.de.reaÃ.Ã.o.transfusional, sexo = Sexo, cor = Cor, comunicante = Comunicante)
# raw0 <- rbindlist(list(raw1, raw2, raw3), fill = TRUE)
# 
# 
# raw0$data <- as.character(raw0$data)
# raw0$turno <- iso8859(raw0$turno)
# raw0$setor <- iso8859(raw0$setor)
# raw0$tipo <- iso8859(raw0$tipo)
# raw0$subtipo <- iso8859(raw0$subtipo)
# raw0$grau_dano <- iso8859(raw0$grau_dano)
# raw0$medicamento <- iso8859(raw0$medicamento)
# raw0$cor <- iso8859(raw0$cor)
# raw0$comunicante <- iso8859(raw0$comunicante)
# raw0$lesao_pele <- iso8859(raw0$lesao_pele)
# raw0$classificacao_up <- iso8859(raw0$classificacao_up)
# raw0$tipo_queda <- iso8859(raw0$tipo_queda)
# raw0$extubacao <- iso8859(raw0$extubacao)
# raw0$perda_sne <- iso8859(raw0$perda_sne)
# raw0$reacao_trasnfusional <- iso8859(raw0$reacao_trasnfusional)
# 
# raw0$dt <- dmy(raw0$data, quiet = TRUE, tz = "America/Sao_Paulo")
# raw0$ano <- factor(year(raw0$dt))
# raw0$mes <- factor(month(raw0$dt), levels = 1:12)
# 
# raw0$cor <- factor(raw0$cor)
# raw0$comunicante <- factor(raw0$comunicante)