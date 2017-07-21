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


raw.data.nisp <- read.csv(url.google.forms.eventos_adversos.csv)
raw.data.farmacovigilancia <- read.csv(url.google.forms.farmacovigilancia.csv)
raw.data.hemovigilancia <- read.csv(url.google.forms.hemovigilancia.csv)


raw1 <- raw.data.nisp %>% filter(nchar(trim(as.character(Data))) >= 10) %>% select(data = Data, turno = Turno, setor = Setor, tipo = Tipo.de.incidente, subtipo = Subtipo.Incidente, grau_dano = Grau.de.Dano, lesao_pele = LesÃ.o.de.Pele.â...Causa, classificacao_up = ClassificaÃ.Ã.o.da.UP, tipo_queda = Tipo.de.Queda, extubacao = ExtubaÃ.Ã.o, perda_sne = Perda.de.SNE, sexo = Sexo, cor = Cor, comunicante = who...quem.comunicou)
raw2 <- raw.data.farmacovigilancia %>% filter(nchar(trim(as.character(Data))) >= 10) %>% select(data = Data, turno = Turno, setor = Setor, tipo = Tipo.de.incidente, subtipo = Subtipo.Incidente, grau_dano = Grau.de.Dano, medicamento = Incidente.Medicamento, sexo = Sexo, cor = Cor, comunicante = Comunicante)
raw3 <- raw.data.hemovigilancia %>% filter(nchar(trim(as.character(Data))) >= 10) %>% select(data = Data, turno = Turno, setor = Setor, tipo = Tipo.de.incidente, subtipo = Subtipo, grau_dano = Grau.de.Dano, reacao_trasnfusional = Tipo.de.reaÃ.Ã.o.transfusional, sexo = Sexo, cor = Cor, comunicante = Comunicante)
raw0 <- rbindlist(list(raw1, raw2, raw3), fill = TRUE)


raw0$data <- as.character(raw0$data)
raw0$turno <- iso8859(raw0$turno)
raw0$setor <- iso8859(raw0$setor)
raw0$tipo <- iso8859(raw0$tipo)
raw0$subtipo <- iso8859(raw0$subtipo)
raw0$grau_dano <- iso8859(raw0$grau_dano)
raw0$medicamento <- iso8859(raw0$medicamento)
raw0$cor <- iso8859(raw0$cor)
raw0$comunicante <- iso8859(raw0$comunicante)
raw0$lesao_pele <- iso8859(raw0$lesao_pele)
raw0$classificacao_up <- iso8859(raw0$classificacao_up)
raw0$tipo_queda <- iso8859(raw0$tipo_queda)
raw0$extubacao <- iso8859(raw0$extubacao)
raw0$perda_sne <- iso8859(raw0$perda_sne)
raw0$reacao_trasnfusional <- iso8859(raw0$reacao_trasnfusional)

raw0$dt <- dmy(raw0$data, quiet = TRUE, tz = "America/Sao_Paulo")
raw0$ano <- factor(year(raw0$dt))
raw0$mes <- factor(month(raw0$dt), levels = 1:12)

raw0$cor <- factor(raw0$cor)
raw0$comunicante <- factor(raw0$comunicante)

raw0 <- raw0 %>% 
          select(ano, mes, dt, data, comunicante, turno, setor, tipo, subtipo, 
                 grau_dano, lesao_pele, classificacao_up, tipo_queda, extubacao, 
                 perda_sne, medicamento, reacao_trasnfusional, sexo, cor) %>% 
          arrange(ano, mes, turno, setor)

# Ajustando as datas...
data.nisp <- raw.data.nisp
data.nisp$Data <- dmy(data.nisp$Data, quiet = TRUE, tz = "America/Sao_Paulo")
data.nisp$ano <- year(data.nisp$Data)
data.nisp$mes <- factor(month(data.nisp$Data), levels = 1:12)
data.nisp$mes_desc <- factor(months.fullname[month(data.nisp$Data)], levels = months.fullname)
data.nisp$ano_mes <- paste0(year(data.nisp$Data), '-', month(data.nisp$Data))
data.nisp$periodo_mes <- floor_date(data.nisp$Data, "month")

data.nisp$Setor <- iconv(as.character(data.nisp$Setor), "UTF-8", "ISO_8859-2")

# Contando registros com datas inválidas
reg.invalidos <- data.nisp %>% filter(is.na(ano))
reg.validos <- data.nisp %>% filter(!is.na(ano))

if(count(reg.invalidos) > 0) {
  warning(paste0('Existem #', count(reg.invalidos), ' registros inválidos nesta amostra'))
  data.nisp <- reg.validos
}
inconformidade.sem.tipo <- data.nisp[data.nisp$Tipo.de.incidente == "", ]
if(count(inconformidade.sem.tipo) > 0) {
  warning(paste0('Existem #', count(inconformidade.sem.tipo), ' registros sem classificação de tipo de evento nesta amostra'))
  data.nisp <- data.nisp %>% filter(Tipo.de.incidente != "")
  data.nisp$Tipo.de.incidente <- factor(data.nisp$Tipo.de.incidente)
}

# Grupos...
nisp.eventos.adversos <- data.nisp %>% filter(Tipo.de.incidente == "Evento Adverso")

###
## Obtendo estatisticas descritivas
###
distribuicao.ano <- table(data.nisp$ano) %>% melt %>% mutate(Var1 = factor(Var1))
grafico.incidentes.ano <- ggplot(distribuicao.ano, aes(x = Var1, y = value, fill = Var1)) +
  geom_bar(stat="identity") +
  geom_text(aes(label = value), vjust = -0.7) +
  coord_cartesian(ylim = c(0, max(distribuicao.ano$value) * 1.1)) +
  scale_fill_brewer(palette = "Set2") +
  theme_bw() +
  theme(legend.position = "none") +
  labs(title = 'Total de incidentes notificados por ano',
       x = "",
       y = "Total de incidentes notificados")
  
  
distribuicao.periodo <- table(data.nisp$periodo_mes) %>% melt %>% mutate(Var1 = ymd(Var1))
timeline.eventos <- ggplot(distribuicao.periodo, aes(x = Var1, y = value, group = 1)) +
  geom_point() +
  geom_line() +
  theme_bw() +
  theme(axis.text.x = element_text(angle = 45, hjust = 1)) +
  scale_x_date(date_breaks = "2 month", date_labels =  "%b %Y") +
  labs(title = "Timeline de notificações de eventos adversos",
       x = "",
       y = "Total de notificações de eventos")


distribuicao.ano.tipo <- table(data.nisp$ano, data.nisp$Tipo.de.incidente) %>% melt
grafico.tipo.ano <- ggplot(distribuicao.ano.tipo, aes(x = Var1, y = value, fill = Var2)) +
  geom_bar(stat="identity") +
  facet_grid(.~Var2) +
  geom_text(aes(label = value), vjust = -0.7) +
  coord_cartesian(ylim = c(0, max(distribuicao.ano.tipo$value) * 1.1)) +
  scale_fill_brewer(palette = "Set3") +
  theme_bw() +
  theme(legend.position = "none") +
  labs(title = 'Tipos de incidentes por ano',
       x = "",
       y = "Total de incidentes notificados")


distribuicao.ano.sexo <- table(data.nisp$ano, data.nisp$Sexo) %>% melt %>% 
  mutate(Var2 = ifelse(as.character(Var2) == "", NA, as.character(Var2)),
         Var2 = ifelse(as.character(Var2) == "F", "Feminino", as.character(Var2)),
         Var2 = ifelse(as.character(Var2) == "M", "Masculino", as.character(Var2))) %>%
  filter(!is.na(Var2))
grafico.sexo.ano <- ggplot(distribuicao.ano.sexo, aes(x = Var1, y = value, fill = Var2)) +
  geom_bar(stat="identity") +
  facet_grid(.~Var2) +
  geom_text(aes(label = value), vjust = -0.7) +
  coord_cartesian(ylim = c(0, max(distribuicao.ano.sexo$value) * 1.1)) +
  scale_fill_manual(values = c("#9b3333", "#345c9b")) +
  theme_bw() +
  theme(legend.position = "none") +
  labs(title = 'Total de incidentes por sexo',
       x = "",
       y = "Total de incidentes notificados")



distribuicao.ano.cor <- table(data.nisp$ano, data.nisp$Cor) %>% melt %>% 
    mutate(Var2 = ifelse(as.character(Var2) == "", NA, iconv(as.character(Var2), "UTF-8", "ISO_8859-2")),
           Var2 = ifelse(tolower(Var2) == "nao informado", NA, Var2)) %>%
    filter(!is.na(Var2))
grafico.tipo.cor <- ggplot(distribuicao.ano.cor, aes(x = Var1, y = value, fill = Var2)) +
    geom_bar(stat="identity") +
    facet_grid(.~Var2) +
    geom_text(aes(label = value), vjust = -0.7) +
    coord_cartesian(ylim = c(0, max(distribuicao.ano.cor$value) * 1.1)) +
    scale_fill_brewer(palette = "Set2") +
    theme_bw() +
    theme(legend.position = "none") +
    labs(title = 'Total de incidentes por cor',
         x = "",
         y = "Total de incidentes notificados")

distribuicao.ano.cor.2 <- distribuicao.ano.cor %>%
                          group_by(Var1, Var2) %>%
                          summarise(Freq = sum(value)) %>%
                          mutate(Freq.rel = (Freq / sum(Freq))) %>%
                          ungroup()

grafico.tipo.cor.2 <- ggplot(distribuicao.ano.cor.2, aes(x = Var1, y = Freq.rel, fill = Var2)) +
  geom_bar(stat="identity") +
  scale_fill_brewer(palette = "Set2") +
#  coord_flip() +
  scale_y_continuous(labels = scales::percent) +
  theme_bw() +
  labs(title = 'Proporção de incidentes por cor',
       x = "",
       y = "Percentual",
       fill = "Cores")





distribuicao.incidentes.queda <- with(nisp.eventos.adversos, table(Var1 = ano, Var2 = Tipo.de.Queda) ) %>% melt %>% 
  mutate(Var2 = ifelse(as.character(Var2) == "", NA, iconv(as.character(Var2), "UTF-8", "ISO_8859-2"))) %>%
  filter(!is.na(Var2))
grafico.incidentes.queda <- ggplot(distribuicao.incidentes.queda, aes(x = Var1, y = value, fill = Var2)) +
  geom_bar(stat="identity") +
  facet_grid(.~Var2) +
  geom_text(aes(label = value), vjust = -0.7) +
  coord_cartesian(ylim = c(0, max(distribuicao.incidentes.queda$value) * 1.1)) +
  scale_fill_brewer(palette = "Set2") +
  theme_bw() +
  theme(legend.position = "none") +
  labs(title = 'Eventos adversos de queda',
       x = "",
       y = "Eventos adversos notificados")

distribuicao.incidentes.queda.2 <- distribuicao.incidentes.queda %>%
  group_by(Var1, Var2) %>%
  summarise(Freq = sum(value)) %>%
  mutate(Freq.rel = (Freq / sum(Freq))) %>%
  ungroup()

grafico.incidentes.queda.2 <- ggplot(distribuicao.incidentes.queda.2, aes(x = Var1, y = Freq.rel, fill = Var2)) +
  geom_bar(stat="identity") +
  scale_fill_brewer(palette = "Set2") +
  #  coord_flip() +
  scale_y_continuous(labels = scales::percent) +
  theme_bw() +
  labs(title = 'Proporção dos eventos adversos de queda',
       subtitle = "Proporção entre os tipos de queda em relação ao total de notificações de quedas",
       x = "",
       y = "Percentual",
       fill = "Tipos de quedas")



#nisp.quedas <- nisp.eventos.adversos %>% filter(ano > 2014 & trim(as.character(Tipo.de.Queda)) != "" & trim(as.character(IDADE)) != "")
nisp.quedas <- data.nisp %>% filter(ano > 2014 & trim(as.character(Tipo.de.Queda)) != "" & trim(as.character(IDADE)) != "")
nisp.quedas$IDADE <- as.character(nisp.quedas$IDADE)
if(length(nisp.quedas[nisp.quedas$IDADE == "36 a 45 anos",]$IDADE) > 0) {
  nisp.quedas[nisp.quedas$IDADE == "36 a 45 anos",]$IDADE <- 36
}
if(length(nisp.quedas[nisp.quedas$IDADE == "46 a 55 anos",]$IDADE) > 0) {
  nisp.quedas[nisp.quedas$IDADE == "46 a 55 anos",]$IDADE <- 45
}
if(length(nisp.quedas[nisp.quedas$IDADE == "56 a 65 anos",]$IDADE) > 0) {
  nisp.quedas[nisp.quedas$IDADE == "56 a 65 anos",]$IDADE <- 56
}
if(length(nisp.quedas[nisp.quedas$IDADE == "66 a 75 anos",]$IDADE) > 0) {
  nisp.quedas[nisp.quedas$IDADE == "66 a 75 anos",]$IDADE <- 66
}
nisp.quedas$IDADE <- as.numeric(nisp.quedas$IDADE)

quedas.por.idade <- table(cut(nisp.quedas$IDADE, breaks=c(0, 10, 20, 30, 40, 50, 60, 130), right = FALSE)) %>% melt
quedas.por.idade$Var1 <- gsub("[[]", "", quedas.por.idade$Var1)
quedas.por.idade$Var1 <- gsub("[,]", " -| ", quedas.por.idade$Var1)
quedas.por.idade$Var1 <- gsub(")", " anos", quedas.por.idade$Var1)
quedas.por.idade$Var1 <- factor(quedas.por.idade$Var1, levels = quedas.por.idade$Var1)
#grafico.queda.idade <- 
  ggplot(quedas.por.idade, aes(x = Var1, y = value)) +
  geom_bar(stat="identity") +
  #facet_grid(.~Var2) +
  geom_text(aes(label = value), vjust = -0.7) +
  coord_cartesian(ylim = c(0, max(quedas.por.idade$value) * 1.1)) +
  scale_fill_brewer(palette = "Set2") +
  theme_bw() +
  theme(legend.position = "none") +
  labs(title = 'Histograma de evento de queda por idade',
       x = "",
       y = "Eventos adversos notificados")


ppi <- read.csv("pacientes_atendidos_por_idade.csv")
tab.ppi  <- data.frame(Faixa = c("0 - 10 anos", 
                     "10 - 20 anos", 
                     "20 - 30 anos",
                     "30 - 40 anos",
                     "40 - 50 anos",
                     "50 - 60 anos",
                     "60 - 130 anos"
                    ), 
           Pacientes = c(
             sum(ppi[ppi$IDADE_NA_EPOCA >= 0 & ppi$IDADE_NA_EPOCA < 10,]$COUNT.DISTINCTCD_PACIENTE.),
             sum(ppi[ppi$IDADE_NA_EPOCA >= 10 & ppi$IDADE_NA_EPOCA < 20,]$COUNT.DISTINCTCD_PACIENTE.),
             sum(ppi[ppi$IDADE_NA_EPOCA >= 20 & ppi$IDADE_NA_EPOCA < 30,]$COUNT.DISTINCTCD_PACIENTE.),
             sum(ppi[ppi$IDADE_NA_EPOCA >= 30 & ppi$IDADE_NA_EPOCA < 40,]$COUNT.DISTINCTCD_PACIENTE.),
             sum(ppi[ppi$IDADE_NA_EPOCA >= 40 & ppi$IDADE_NA_EPOCA < 50,]$COUNT.DISTINCTCD_PACIENTE.),
             sum(ppi[ppi$IDADE_NA_EPOCA >= 50 & ppi$IDADE_NA_EPOCA < 60,]$COUNT.DISTINCTCD_PACIENTE.),
             sum(ppi[ppi$IDADE_NA_EPOCA >= 60 & ppi$IDADE_NA_EPOCA < 130,]$COUNT.DISTINCTCD_PACIENTE.)
           ),
           Quedas = quedas.por.idade$value
)

appx <- tab.ppi %>% mutate(percentual = round(Quedas * 100 / Pacientes, 2) )
appi <- tab.ppi %>% mutate(freq.relativa = paste(round(Quedas * 100 / Pacientes,2), '%'))



def_par <- par() 
par(mar=c(5,5,4,5)) 
d <- arrange(appx, Faixa) %>%
  mutate(
    cumsum = cumsum(percentual),
    freq = round(percentual / sum(percentual), 3),
    cum_freq = cumsum(freq)
  )
pc <- barplot(d$percentual,  
        width = 1, space = 0.2, border = NA, axes = F,
        ylim = c(0, 1.05 * max(d$cumsum, na.rm = T)), 
        ylab = "Frequencia acumulada" , cex.names = 0.7, 
        names.arg = d$Faixa,
        main = "Diagrama de pareto - Notificações de evento de queda por idade"
        )
lines(pc, d$cumsum, type = "b", cex = 0.7, pch = 19, col="cyan4")
box(col = "grey62")
axis(side = 2, at = c(0, d$cumsum), las = 1, col.axis = "grey62", col = "grey62", cex.axis = 0.8)
axis(side = 4, at = c(0, d$cumsum), labels = paste(c(0, round(d$cum_freq * 100)) ,"%",sep=""), 
     las = 1, col.axis = "cyan4", col = "cyan4", cex.axis = 0.8)
par(def_par) 

library(gridExtra)
pdf("distribuicao.quedas.pdf", height=5, width=8)
grid.table(appi)
dev.off()


distribuicao.incidentes.lesao_pele <- with(nisp.eventos.adversos, table(Var1 = ano, Var2 = LesÃ.o.de.Pele.â...Causa) ) %>% melt %>% 
  mutate(Var2 = ifelse(as.character(Var2) == "", NA, iconv(as.character(Var2), "UTF-8", "ISO_8859-2"))) %>%
  filter(!is.na(Var2))
grafico.incidentes.lesao_pele <- 
  ggplot(distribuicao.incidentes.lesao_pele, aes(x = Var1, y = value, fill = Var2)) +
  geom_bar(stat="identity") +
  facet_wrap(~Var2, scales = "free_x") +
  geom_text(aes(label = value), vjust = -0.7) +
  coord_cartesian(ylim = c(0, max(distribuicao.incidentes.lesao_pele$value) * 1.4)) +
  scale_fill_brewer(palette = "Set2") +
  theme_bw() +
  theme(legend.position = "none") +
  labs(title = 'Eventos adversos de lesão de pele',
       x = "",
       y = "Eventos adversos notificados")





distribuicao.incidentes.extubacao <- with(nisp.eventos.adversos, table(Var1 = ano, Var2 = ExtubaÃ.Ã.o) ) %>% melt %>% 
  mutate(Var2 = ifelse(trim(as.character(Var2)) == "", NA, iconv(as.character(Var2), "UTF-8", "ISO_8859-2"))) %>%
  filter(!is.na(Var2))
grafico.incidentes.extubacao <- 
  ggplot(distribuicao.incidentes.extubacao, aes(x = Var1, y = value, fill = Var2)) +
  geom_bar(stat="identity") +
  facet_wrap(~Var2) +
  geom_text(aes(label = value), vjust = -0.7) +
  coord_cartesian(ylim = c(0, max(distribuicao.incidentes.extubacao$value) * 1.1)) +
  scale_fill_brewer(palette = "Set2") +
  theme_bw() +
  theme(legend.position = "none") +
  labs(title = 'Eventos adversos de extubação',
       x = "",
       y = "Eventos adversos notificados")




distribuicao.incidentes.grau_dano <- with(nisp.eventos.adversos, table(Var1 = ano, Var2 = Grau.de.Dano) ) %>% melt %>% 
  mutate(Var2 = ifelse(trim(as.character(Var2)) == "", NA, iconv(as.character(Var2), "UTF-8", "ISO_8859-2"))) %>%
  filter(!is.na(Var2))
grafico.incidentes.grau_dano <- 
  ggplot(distribuicao.incidentes.grau_dano, aes(x = Var1, y = value, fill = Var2)) +
  geom_bar(stat="identity") +
  facet_wrap(~Var2, scales = "free_x") +
  geom_text(aes(label = value), vjust = -0.7) +
  coord_cartesian(ylim = c(0, max(distribuicao.incidentes.grau_dano$value) * 1.3)) +
  scale_fill_brewer(palette = "Set2") +
  theme_bw() +
  theme(legend.position = "none") +
  labs(title = 'Eventos adversos - Grau de dano',
       x = "",
       y = "Eventos adversos notificados")






for (setor in unique(data.nisp$Setor)) {
  data.setor <- data.nisp %>% filter(Setor == setor)
  
  distribuicao.setor.ano.tipo <- table(data.setor$ano, data.setor$Tipo.de.incidente) %>% melt
  #grafico.setor.tipo.ano <- 
    ggplot(distribuicao.setor.ano.tipo, aes(x = Var1, y = value, fill = Var2)) +
    geom_bar(stat="identity") +
    facet_grid(.~Var2) +
    geom_text(aes(label = value), vjust = -0.7) +
    coord_cartesian(ylim = c(0, max(distribuicao.ano.tipo$value) * 1.1)) +
    scale_fill_brewer(palette = "Set3") +
    theme_bw() +
    theme(legend.position = "none") +
    labs(title = paste(setor, ' - Tipos de incidentes por ano'),
         x = "",
         y = "Total de incidentes notificados")
  
  
}







## Analise das ulceras por pressão - Junho/2016 ~ Junho/2017
raw0 %>% 
  filter(dt >= ymd('2016-06-01') & dt <= ymd('2017-06-30')) %>% 
  filter(lesao_pele == "Lesao por pressao" & classificacao_up != "") %>% 
  select(lesao_pele, classificacao_up) %>% 
  group_by(lesao_pele, classificacao_up) %>% 
  summarise(n = n()) %>% 
  ggplot(aes(classificacao_up, n, fill=classificacao_up)) + 
  geom_bar(stat="identity") + 
  #facet_grid(.~ano) + 
  labs(title = "Distribuição das lesões por pressão por grau de classificação", 
       subtitle="Periodo Junho/2016 ~ Junho/2017", 
       x = "", 
       y = "Total de notificações") + 
  geom_text(aes(label = n), vjust = -0.7) + coord_cartesian(ylim = c(0, 35)) + 
  theme_bw() + 
  theme(legend.position = "none")


## Analise das ulceras por pressão - Janeiro/2015 ~ Junho/2017
dados_lesao.0 <- raw0 %>% 
  filter(dt >= ymd('2015-01-01') & dt <= ymd('2017-06-30')) %>%
  filter(lesao_pele == "Lesao por pressao")
  
  
dados_lesao.1 <- dados_lesao.0 %>% 
  select(lesao_pele, classificacao_up) %>% 
  group_by(lesao_pele, classificacao_up) %>% 
  summarise(n = n())

dados_lesao.1 %>%
  ggplot(aes(classificacao_up, n, fill=classificacao_up)) + 
  geom_bar(stat="identity") + 
  #facet_grid(.~ano) + 
  labs(title = "Distribuição das lesões por pressão por grau de classificação", 
       subtitle="Periodo Janeiro/2015 ~ Junho/2017", 
       x = "", 
       y = "Total de notificações") + 
  geom_text(aes(label = paste0(n, ' - p.', round(n*100/5717,2), '%')), vjust = -0.7) + coord_cartesian(ylim = c(0, 60)) + 
  theme_bw() + 
  theme(legend.position = "none")

est.lesao.internados <- 5717
est.lesao.qtde_lesoes <- sum(dados_lesao.1$n)
est.lesao.indice <- round(est.lesao.qtde_lesoes * 100 / est.lesao.internados,2)

dados_lesao.1 %>% mutate(indice = round(n * 100 / est.lesao.internados,2))

#estatistica_lesao <- 
  data.frame(indicador = c("Periodo:", 
                           "População internada no período:",
                           "Lesão por pressão notificada no período:",
                           "Percentual de incidência de lesão por pressão:",
                           "Percentual de incidência de lesão por pressão - Estágio I:",
                           "Percentual de incidência de lesão por pressão - Estágio II:",
                           "Percentual de incidência de lesão por pressão - Estágio III:",
                           "Percentual de incidência de lesão por pressão - Estágio IV:"
                           ),
             valor = c("Janeiro/2015 ~ Junho/2017",
                       as.character(est.lesao.internados),
                       as.character(est.lesao.qtde_lesoes),
                       as.character(est.lesao.indice)
                       )
             )

## lesao por pressao por setor
dados_lesao.por.setor <- dados_lesao.0 %>% 
  select(setor) %>% 
  group_by(setor) %>% 
  summarise(n = n()) %>%
  ungroup()


dados_internacoes <- read.csv("internacoes.csv")
merge(dados_lesao.por.setor, dados_internacoes) %>% mutate(indice = round(n * 100 / internacoes,2))


dados_lesao.por.setor %>%
  ggplot(aes(setor, n, fill=classificacao_up)) + 
  geom_bar(stat="identity") + 
  #facet_grid(.~ano) + 
  labs(title = "Distribuição das lesões por pressão por grau de classificação", 
       subtitle="Periodo Janeiro/2015 ~ Junho/2017", 
       x = "", 
       y = "Total de notificações",
       fill="Classificação da lesão") + 
  #geom_text(aes(label = paste0(n, ' - p.', round(n*100/5717,2), '%')), vjust = -0.7) + coord_cartesian(ylim = c(0, 60)) + 
  theme_bw() 
  theme(legend.position = "none")
  
dados_lesao.por.setor %>%
  ggplot(aes(setor, n, fill=setor)) + 
  geom_bar(stat="identity") + 
  labs(title = "Incidência de lesão de pele por setor", 
       subtitle="Periodo Janeiro/2015 ~ Junho/2017", 
       x = "", 
       y = "Total de notificações",
       fill="Classificação da lesão") + 
  geom_text(aes(label = paste0(n, ' | ', round(n*100/5717,2), '%')), vjust = -0.7) + 
  coord_cartesian(ylim = c(0, max(dados_lesao.por.setor$n) * 1.1)) + 
  #geom_text(aes(label = n), vjust = -0.7) + coord_cartesian(ylim = c(0, 60)) + 
  theme_bw() +
  theme(legend.position = "none")
  
  
  
  
  
  
  
  
  
  

x <- raw0 %>% 
  filter(dt >= ymd('2015-01-01') & dt <= ymd('2017-06-30')) %>% 
  filter(tipo_queda != "") %>% 
  select(tipo, tipo_queda) %>% 
  group_by(tipo, tipo_queda) %>% 
  summarise(n = n())
  # %>% table(Var1 = ano, Var2 = tipo_queda)

sum(x$n)
