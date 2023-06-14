# Planilha Google Sheets: <https://docs.google.com/spreadsheets/d/1vTveXilqlAjwoWmofIqUo5t3WW53mJG-0pxLwzEhAtE/edit?resourcekey#gid=1424416413>
# Formulario: <https://docs.google.com/forms/d/e/1FAIpQLSfYZ6X_XMvIplltZOEcMyxaZpWjfRLpByN5kUvg4ePyTYTVlA/viewform>

import os
import re
import time
import requests
import pandas as pd
import numpy as np
import streamlit as st
from datetime import datetime
from unidecode import unidecode
from rich.console import Console
from io import StringIO, BytesIO
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go

url_formulario = 'https://docs.google.com/forms/d/e/1FAIpQLSfYZ6X_XMvIplltZOEcMyxaZpWjfRLpByN5kUvg4ePyTYTVlA/viewform'
analise_institucional = 'Institucional'
analise_setorial = 'Setorial'
console = Console()

st.set_page_config(page_title="HDT Segurança do Paciente",
					page_icon=':hospital:', 
					layout="wide",
					# layout="centered",
					initial_sidebar_state="auto", 
					menu_items=None)

st.markdown("""<style>
            #MainMenu {visibility: hidden; }
            footer {visibility: hidden; }
            header {visibility: hidden; }
            </style>""", unsafe_allow_html=True)

def ajustar_placa(texto: str, posicao: int = 3, caractere: str = '-'):
	resultado = texto
	return resultado.replace('-', '').upper()
	if len(texto) > posicao:
		if texto[posicao] == caractere:
			resultado = texto
		else:
			resultado = texto[:posicao] + caractere + texto[posicao:]
	return resultado.upper()

@st.cache_data(ttl=120)
def get_data():
    # url = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vThoql39RlevhMu3lmsMpjngoo6UsVgAQZjNGxFVdEcuqfIp3Tu01msa3ALUfHQV8FX3GwkMNW5nuJJ/pub?gid=1424416413&single=true&output=csv'
    url = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vThoql39RlevhMu3lmsMpjngoo6UsVgAQZjNGxFVdEcuqfIp3Tu01msa3ALUfHQV8FX3GwkMNW5nuJJ/pub?gid=1424416413&single=true&output=tsv'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; rv:91.0) Gecko/20100101 Firefox/91.0',
        'Accept-Charset': 'utf-8'
    }

    # Função para gerar nomes únicos
    def gerar_nome_unico(nome, contador):
        return f"{nome}_{contador}"

    # Função para renomear as colunas
    def renomear_colunas(df):
        novos_nomes = []
        contador = {}
        for nome in df.columns:
            # remover acentos
            nome = unidecode(nome.lower()).replace(' ', '_')
            # Remover caracteres especiais e substituir espaços por underscores
            novo_nome = re.sub(r'\W+', '', nome)
            # novo_nome = nome
            # Limitar a quantidade de caracteres em 15
            novo_nome = novo_nome[:60]
            # Verificar se o nome já existe
            if novo_nome in novos_nomes:
                # Gerar um nome único adicionando um sufixo numérico
                if novo_nome not in contador:
                    contador[novo_nome] = 1
                else:
                    contador[novo_nome] += 1
                novo_nome = gerar_nome_unico(novo_nome, contador[novo_nome])
            novos_nomes.append(novo_nome)
        df.columns = novos_nomes
        return df

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        df = pd.read_csv(BytesIO(response.content), sep='\t')
        df = renomear_colunas(df)
        return df
    else:
        raise Exception('Falhou ao obter dados')
# df = pd.read_csv(url)
    return df

with st.spinner('Atualizando base de dados...'):
	df_raw = get_data()

df_invalidos = df_raw[~df_raw['qual_a_data_do_incidente'].str.contains('/202')]
df_validos = df_raw[df_raw['qual_a_data_do_incidente'].str.contains('/202')]

# Corrigindo os tipo de dados
df = df_validos.copy()
df.to_csv('dados.tsv', sep='\t', index=False)
df['qual_a_data_do_incidente'] = pd.to_datetime(df['qual_a_data_do_incidente'], format='%d/%m/%Y')
df['mes'] = df['qual_a_data_do_incidente'].dt.to_period('M').dt.to_timestamp(freq='M')
df['semana'] = df['qual_a_data_do_incidente'].dt.to_period('W').dt.to_timestamp(freq='W')


st.title('Dashboard - Segurança do Paciente')
st.subheader('Monitoramento das Notificações de Incidentes ou Eventos Adversos')
st.markdown('<h5 style="color: #6880c7;">Hospital Estadual de Doenças Tropicais</h5>', unsafe_allow_html=True)
# st.markdown(f'<h2 style="color: firebrick;text-align:center;border-bottom: 4px solid firebrick;margin-bottom: 1rem;padding: .5rem;">{sel_setor.upper()}</h2>', unsafe_allow_html=True)


## SIDEBAR
with st.sidebar:
    if len(df_invalidos) > 0:
        with st.container():
            st.error(f'**ALERTA:** Identificados {len(df_invalidos)} registros com períodos inválidos na base de dados. Reportar ao setor de Qualidade, para realizar as correções necessárias.', icon="🚨")
            st.write('<hr>', unsafe_allow_html=True)
    
    # fazer uma lista com os meses selecionaveis a partir do df.qual_o_tipo_do_incidente.unique() formatado com %m/%Y
    sel_mes = st.selectbox('Qual período você deseja consultar?', df.sort_values(by='mes', ascending=False).mes.dt.strftime('%Y/%m').unique())
    sel_visao = st.radio('Qual tipo de análise?', [analise_institucional, analise_setorial])
    
    if sel_visao == analise_setorial:
        # sel_setores = st.multiselect('Selecione os setores que deseja analisar', df.sort_values(by='qual_local_onde_ocorreu_o_incidente', ascending=True).qual_local_onde_ocorreu_o_incidente.unique())
        sel_setor = st.radio('Qual a setor?', df[df.mes.dt.strftime('%Y/%m') == sel_mes].sort_values(by='qual_local_onde_ocorreu_o_incidente', ascending=True).qual_local_onde_ocorreu_o_incidente.unique())

    st.markdown(f'<hr><div style="text-align:center;"><a href="{url_formulario}" style="text-decoration:none;">Abrir formulário</a></div>', unsafe_allow_html=True)

    st.markdown(f"<br><br><div style='font-size: 1em;text-align: center;color: gray;font-style: italic;'>Desenvolvido por Herson Melo</div>", unsafe_allow_html=True)


df_mes = df[df.mes.dt.strftime('%Y/%m') == sel_mes]
if sel_visao == analise_setorial:
    if sel_setor:
        df_mes_setor = df_mes.query(f'qual_local_onde_ocorreu_o_incidente=="{sel_setor}"')
        df_ano_setor = df.query(f'qual_local_onde_ocorreu_o_incidente=="{sel_setor}"')
    else:
        df_mes_setor = df_mes
        df_ano_setor = df


placeholder = st.empty()


if sel_visao == analise_institucional:
    with placeholder.container():
    # with st.spinner('Processando...'):
        with st.container():
            col = st.columns(4)
            col[0].metric("Período", sel_mes)
            col[1].metric("Total de registros no periodo", len(df_mes))
            reg_periodo = len(df_mes)
            reg_classificados = len(df_mes[~df_mes.classificacao_de_incidentes.isna()])
            reg_pendentes = len(df_mes[df_mes.classificacao_de_incidentes.isna()])
            p_reg_classificados = round(reg_classificados * 100 / reg_periodo, 0)
            p_reg_pendentes = round(reg_pendentes * 100 / reg_periodo, 0)
            col[2].metric("Notificações já classificadas", f"{reg_classificados}  ({p_reg_classificados}%)")
            col[3].metric("Pendentes de classificação", f"{reg_pendentes}  ({p_reg_pendentes}%)")


        cols = st.columns([2, 1])
        with cols[0].container():
            # with st.container():
            with st.expander('♦︎ SERIE HISTÓRICA', expanded=True):
                st.subheader('TOTAL DE NOTIFICAÇÕES REGISTRADAS', anchor='historico')
                tabSH = st.tabs(['⦿ Por mês', '⦿ Por semana'])
                with tabSH[0].container():
                    df_agg_mes = (
                        df
                        .groupby(['mes'])
                        .size()
                        .reset_index(name='Quantidade')
                        .rename(columns={'mes': 'Periodo'})
                    )
                    # st.dataframe(df_agg_mes)

                    fig = px.line(
                        df_agg_mes,
                        x="Periodo",
                        y="Quantidade",
                        markers=True,
                        title='Série Histórica das Notificações - Institucional',
                        labels={
                            "Periodo": "\nPeríodo (mensal)",
                            "Quantidade": "Total Notificações",
                        },
                    )
                    fig.update_layout(height=300)
                    st.plotly_chart(fig, theme="streamlit", use_container_width=True)

                with tabSH[1].container():
                    df_agg_semana = (
                        df
                        .groupby(['semana'])
                        .size()
                        .reset_index(name='Quantidade')
                        .rename(columns={'semana': 'Periodo'})
                    )
                    # st.write(df_agg_semana)
                    
                    fig = px.line(
                        df_agg_semana,
                        x="Periodo",
                        y="Quantidade",
                        markers=True,
                        title='Série Histórica das Notificações - Institucional',
                        labels={
                            "Periodo": "\nPeríodo (semanal)",
                            "Quantidade": "Total Notificações",
                        },
                    )
                    fig.update_layout(height=300)
                    st.plotly_chart(fig, theme="streamlit", use_container_width=True)


        with cols[1].container():
            with st.expander('♦︎ RELACIONADO AO PACIENTE', expanded=True):
                st.subheader('RELACIONADO AO PACIENTE', anchor='historico2')
                with st.container():
                    df_agg_temp = (
                        df_mes
                        .groupby(['o_incidente_que_voce_quer_notificar_esta_relacionado_a_algum'])
                        .size()
                        .reset_index(name='Quantidade')
                        .rename(columns={'o_incidente_que_voce_quer_notificar_esta_relacionado_a_algum': 'Relacionado'})
                    )
                    
                    fig = px.pie(
                        df_agg_temp,
                        names="Relacionado",
                        color="Relacionado",
                        values="Quantidade",
                        title='Eventos relacionados a pacientes',
                        labels={
                            "Relacionado": "Relacionado a um paciente",
                            "Quantidade": "Total Notificações",
                        },
                        color_discrete_map={
                            'SIM': '#0068c9',
                            'NÃO': '#b3b3b3',
                        }
                    )
                    fig.update_layout(height=358)
                    fig.update_layout(margin = dict(t=70, l=0, r=0, b=0))
                    st.plotly_chart(fig, theme="streamlit", use_container_width=True)

        reg_classificados = len(df_mes[~df_mes.classificacao_de_incidentes.isna()])
        if reg_classificados <= 0:
            st.error(f'Os registros deste período selecionado, ainda estão pendentes de serem classificados. Após a classificação os dados serão exibidos aqui.')
        else:
            
            with st.expander(f'♦︎ DIAGRAMA DE COMPOSIÇÃO EM {sel_mes}', expanded=True):
                
                st.subheader(f'DIAGRAMAS DE COMPOSIÇÃO INSTITUCIONAL EM {sel_mes}', anchor='composicao_institucional')
                tabs = st.tabs(["⦿ Grau de dano vs Setor", "⦿ Tipo de incidente vs Setor", "⦿ Horário do incidente vs Setor"])
                
                with tabs[0].container():
                    df_agg_temp = (
                        df_mes
                        .groupby(['classificacao_de_incidentes', 'qual_o_tipo_do_incidente', 'qual_local_onde_ocorreu_o_incidente'])
                        .size()
                        .reset_index(name='Quantidade')
                        .rename(columns={'qual_o_tipo_do_incidente': 'tipo', 'qual_local_onde_ocorreu_o_incidente': 'unidade'})        
                    ).sort_values(by=['classificacao_de_incidentes', 'tipo', 'unidade'], ascending=False)
                    # st.dataframe(df_agg_temp)
                    
                    fig = px.sunburst(
                        df_agg_temp, 
                        path=['classificacao_de_incidentes', 'tipo', 'unidade'], 
                        values='Quantidade',
                    )
                    fig.update_traces(hovertemplate='<b>%{label}</b><br>Quantidade: <b>%{value}</b>')
                    fig.update_layout(margin = dict(t=0, l=0, r=0, b=0))

                    fig.update_layout(height=700)
                    st.plotly_chart(fig, theme="streamlit", use_container_width=True)
                    st.markdown("- *Clique sobre o gráfico para interagir com ele.*")
                    
                with tabs[1].container():
                    df_agg_grau_dano_por_localidade = (
                        df_mes
                        .groupby(['mes', 'classificacao_de_incidentes', 'grau_do_dano', 'qual_local_onde_ocorreu_o_incidente'])
                        .size()
                        .reset_index(name='Quantidade')
                        .rename(columns={'grau_do_dano': 'grau', 'qual_local_onde_ocorreu_o_incidente': 'unidade'})        
                    ).sort_values(by=['classificacao_de_incidentes', 'grau', 'unidade'], ascending=False)
                    # st.dataframe(df_agg_grau_dano_por_localidade)
                    
                    fig = px.sunburst(
                        df_agg_grau_dano_por_localidade, 
                        path=['classificacao_de_incidentes', 'grau', 'unidade'], 
                        values='Quantidade',
                        # color='classificacao_de_incidentes',
                        # color_continuous_scale=[(0, "red"), (0.5, "green"), (1, "blue")],
                    )
                    fig.update_traces(hovertemplate='<b>%{label}</b><br>Quantidade: <b>%{value}</b>')
                    fig.update_layout(margin = dict(t=0, l=0, r=0, b=0))

                    fig.update_layout(height=700)
                    st.plotly_chart(fig, theme="streamlit", use_container_width=True)
                    st.markdown("- *Clique sobre o gráfico para interagir com ele.*")

                with tabs[2].container():
                    df_agg_temp = (
                        df_mes
                        .groupby(['mes', 'classificacao_de_incidentes', 'qual_horario_do_incidente', 'qual_local_onde_ocorreu_o_incidente'])
                        .size()
                        .reset_index(name='Quantidade')
                        .rename(columns={'qual_horario_do_incidente': 'tipo', 'qual_local_onde_ocorreu_o_incidente': 'unidade'})
                    ).sort_values(by=['classificacao_de_incidentes', 'tipo', 'unidade'], ascending=False)

                    fig = px.sunburst(
                        df_agg_temp, 
                        path=['classificacao_de_incidentes', 'tipo', 'unidade'], 
                        values='Quantidade',
                    )
                    fig.update_traces(hovertemplate='<b>%{label}</b><br>Quantidade: <b>%{value}</b>')
                    fig.update_layout(margin = dict(t=0, l=0, r=0, b=0))

                    fig.update_layout(height=700)
                    st.plotly_chart(fig, theme="streamlit", use_container_width=True)
                    st.markdown("- *Clique sobre o gráfico para interagir com ele.*")

if sel_visao == analise_setorial:
    # with st.spinner('Processando...'):
    with placeholder.container():

        st.markdown(f'<h2 style="color: firebrick;text-align:center;border-bottom: 4px solid firebrick;margin-bottom: 1rem;padding: .5rem;">{sel_setor.upper()}</h2>', unsafe_allow_html=True)
        with st.container():
            col = st.columns(4)
            reg_periodo = len(df_mes_setor)
            reg_classificados = len(df_mes_setor[~df_mes_setor.classificacao_de_incidentes.isna()])
            reg_pendentes = len(df_mes_setor[df_mes_setor.classificacao_de_incidentes.isna()])
            p_reg_classificados = round(reg_classificados * 100 / reg_periodo, 0)
            p_reg_pendentes = round(reg_pendentes * 100 / reg_periodo, 0)
            col[0].metric("Período", sel_mes)
            col[1].metric("Total de registros", reg_periodo)
            col[2].metric("Notificações já classificadas", f"{reg_classificados}  ({p_reg_classificados}%)")
            col[3].metric("Pendentes de classificação", f"{reg_pendentes}  ({p_reg_pendentes}%)")

        reg_classificados = len(df_mes_setor[~df_mes_setor.classificacao_de_incidentes.isna()])
        if reg_classificados <= 0:
            st.error(f'Os registros deste período selecionado, ainda estão pendentes de serem classificados. Após a classificação os dados serão exibidos aqui.')
        else:
            with st.expander('♦︎ SERIE HISTÓRICA SETORIAL', expanded=True):
                st.subheader('TOTAL DE NOTIFICAÇÕES REGISTRADAS DO SETOR', anchor='historico')
            
                classes = df_ano_setor.sort_values(by=['classificacao_de_incidentes'], ascending=True) .classificacao_de_incidentes.unique().tolist()
                classes = [str(x) for x in classes if str(x) != 'nan']

                tabsSHS = st.tabs(['◉ Todos os tipos'] + [f'⦿ {x}' for x in classes])
                with tabsSHS[0].container():
                    df_agg_mes = (
                        df_ano_setor
                        .groupby(['mes'])
                        .size()
                        .reset_index(name='Quantidade')
                        .rename(columns={'mes': 'Periodo'})
                    ).tail(12)
                    df_agg_mes['Periodo_formatado'] = df_agg_mes['Periodo'].dt.strftime('%b %Y')

                    # st.dataframe(df_agg_mes)

                    fig = px.line(
                        df_agg_mes,
                        x="Periodo_formatado",
                        y="Quantidade",
                        markers=True,
                        title=f'Total de notificações | Todos os tipos<br>{sel_setor}',
                        labels={
                            "Periodo_formatado": "Período (mensal)",
                            "Quantidade": "Total Notificações",
                        },
                    )
                    fig.update_layout(height=300)
                    st.plotly_chart(fig, theme="streamlit", use_container_width=True)
                    
                    # ------------------------------------------------------------
                    # TODO: A idéia é montar uma tabela com os dados 
                    # tendo os meses como colunas e as classificações como linhas
                    # ------------------------------------------------------------
                    # df_agg_mes = (
                    #     df_ano_setor
                    #     .groupby(['mes']) #, 'classificacao_de_incidentes'
                    #     .size()
                    #     .reset_index(name='Quantidade')
                    #     .rename(columns={'mes': 'Periodo', 'classificacao_de_incidentes': 'Classificação'})
                    # ).tail(12)
                    # st.table(df_agg_mes)
                    # df_agg_mes['Periodo'] = df_agg_mes['Periodo'].dt.strftime('%b %Y')
                    # df_agg_mes.set_index(['Periodo'], inplace=True)
                    # # df_agg_mes.set_index(['Periodo', 'Classificação'], inplace=True)
                    # st.table(df_agg_mes)
                    # st.dataframe(df_agg_mes[['Classificação']].T)
                    # st.table(df_agg_mes.drop(['Periodo'], axis=1).set_index('Periodo_formatado').T)

                for i, classe in enumerate(classes): 
                    with tabsSHS[i+1].container():
                        df_agg_mes2 = (
                                df_ano_setor.query('classificacao_de_incidentes == @classe')
                                .groupby(['mes'])
                                .size()
                                .reset_index(name='Quantidade')
                                .rename(columns={'mes': 'Perído',})
                            ).sort_values(by=['Perído',], ascending=True)
                        df_agg_mes2['Perído'] = df_agg_mes2['Perído'].dt.strftime('%b %Y')

                        reg_tmp = len(df_agg_mes2)
                        if reg_tmp <= 0:
                            st.warning(f'**Não existem dados neste período para classificação.**')
                        else:
                            # st.dataframe(df_agg_mes2)

                            fig = px.line(
                                df_agg_mes2,
                                x="Perído",
                                y="Quantidade",
                                markers=True,
                                # title=f'[{classe}] - Total de notificações por mês no setor: ({sel_setor}):',
                                title=f'Total de notificações | {classe}<br>{sel_setor}',
                                labels={
                                    "Perído": "Período (mensal)",
                                    "Quantidade": "Total Notificações",
                                },
                            )
                            fig.update_layout(height=300)
                            st.plotly_chart(fig, theme="streamlit", use_container_width=True)
                    
            with st.expander('♦︎ ANALISE CRÍTICA', expanded=False):
                st.subheader('ANÁLISE CRÍTICA DOS INCIDENTES COMUNICADOS', anchor='analise_critica')
                st.error('**ATENÇÃO: O texto abaixo é apenas um modelo como exemplo.**')
                st.text('A análise abaixo é realizada pelo responsável pelo setor em questão')
                st.code(f'''
    # Análise Crítica de Incidentes Comunicados
    # 
    # Setor...: {sel_setor}
    # Período.: {sel_mes[:4]}

    # 2023/Janeiro
    - loren ipsum dolor sit amet
    - loren ipsum dolor sit amet
        - loren ipsum dolor sit amet
        - loren ipsum dolor sit amet

    # 2023/Fevereiro
    - loren ipsum dolor sit amet
    - loren ipsum dolor sit amet
    - loren ipsum dolor sit amet

    # 2023/Março
    - Nenhuma ocorrência

    # 2023/Abril
    - Nenhuma ocorrência

    # 2023/Maio
    - loren ipsum dolor sit amet
    - loren ipsum dolor sit amet

    # 2023/Junho
    - loren ipsum dolor sit amet
        - loren ipsum dolor sit amet
        - loren ipsum dolor sit amet
    - loren ipsum dolor sit amet
        - loren ipsum dolor sit amet
    - loren ipsum dolor sit amet

    # 2023/Julho
    - loren ipsum dolor sit amet
        ''', 
        language="markdown", 
        line_numbers=True)

            
            with st.expander(f'♦︎ DIAGRAMA DE COMPOSIÇÃO SETORIAL EM {sel_mes}', expanded=True):
                st.subheader(f'DIAGRAMA DE COMPOSIÇÃO SETORIAL EM {sel_mes}', anchor='composicao')
                
                # cols = st.columns([1, 4])
                # sel_setor = cols[0].radio('Qual a localidade?', df_mes.sort_values(by='qual_local_onde_ocorreu_o_incidente', ascending=True).qual_local_onde_ocorreu_o_incidente.unique())
                
                cols = st.columns([1])

                with cols[0].container():
                    if len(df_mes.query(f'qual_local_onde_ocorreu_o_incidente=="{sel_setor}"')) <= 0:
                        st.warning(f'Não foram encontrados registros para o setor "{sel_setor}" no mês selecionado')
                    else:
                        # st.dataframe(df_mes.query(f'qual_local_onde_ocorreu_o_incidente=="{sel_setor}"'))
                        tabs = st.tabs(["⦿ Grau de dano vs Tipo", "⦿ Grau de dano vs Horário do incidente", "⦿ Horário do incidente vs Tipo"])

                        with tabs[0].container():
                            df_agg_grau_dano_por_localidade = (
                                df_mes.query(f'qual_local_onde_ocorreu_o_incidente=="{sel_setor}"')
                                .groupby(['mes', 'classificacao_de_incidentes', 'grau_do_dano', 'qual_o_tipo_do_incidente'])
                                .size()
                                .reset_index(name='Quantidade')
                                .rename(columns={'classificacao_de_incidentes': 'v1', 'grau_do_dano': 'v2', 'qual_o_tipo_do_incidente': 'v3'})        
                            ).sort_values(by=['v1', 'v2', 'v3'], ascending=False)
                            # st.dataframe(df_agg_grau_dano_por_localidade)
                            
                            fig = px.sunburst(
                                df_agg_grau_dano_por_localidade, 
                                path=['v1', 'v2', 'v3'], 
                                values='Quantidade',
                            )
                            fig.update_traces(hovertemplate='<b>%{label}</b><br>Quantidade: <b>%{value}</b>')
                            fig.update_layout(margin = dict(t=0, l=0, r=0, b=0))

                            fig.update_layout(height=700)
                            st.plotly_chart(fig, theme="streamlit", use_container_width=True)

                            st.markdown("""
    - *Clique sobre o gráfico para interagir com ele.*
    - As variáveis *'Classificação do incidente'* e *'Grau de dano'* são obtidas através da classificação especializada feita pelo setor de qualidade, que analisa as notificações e as classifica conforme seu melhor entendimento. Já o campo *'Tipo de incidente'* é proveniente da auto-declaração do notificante, portanto pode haver relativa discordância entre as duas interpretações, eventualmente.""")
                        
                        with tabs[1].container():
                            df_agg_grau_dano_por_localidade = (
                                df_mes.query(f'qual_local_onde_ocorreu_o_incidente=="{sel_setor}"')
                                .groupby(['classificacao_de_incidentes', 'grau_do_dano', 'qual_horario_do_incidente'])
                                .size()
                                .reset_index(name='Quantidade')
                                .rename(columns={'classificacao_de_incidentes': 'v1', 'grau_do_dano': 'v2', 'qual_horario_do_incidente': 'v3'})        
                            ).sort_values(by=['v1', 'v2', 'v3'], ascending=False)
                            # st.dataframe(df_agg_grau_dano_por_localidade)
                            
                            fig = px.sunburst(
                                df_agg_grau_dano_por_localidade, 
                                path=['v1', 'v2', 'v3'], 
                                values='Quantidade',
                            )
                            fig.update_traces(hovertemplate='<b>%{label}</b><br>Quantidade: <b>%{value}</b>')
                            fig.update_layout(margin = dict(t=0, l=0, r=0, b=0))

                            fig.update_layout(height=700)
                            st.plotly_chart(fig, theme="streamlit", use_container_width=True)

                        with tabs[2].container():
                            df_agg_grau_dano_por_localidade = (
                                df_mes.query(f'qual_local_onde_ocorreu_o_incidente=="{sel_setor}"')
                                .groupby(['qual_horario_do_incidente', 'classificacao_de_incidentes', 'qual_o_tipo_do_incidente'])
                                .size()
                                .reset_index(name='Quantidade')
                                .rename(columns={'qual_horario_do_incidente': 'v1', 'classificacao_de_incidentes': 'v2', 'qual_o_tipo_do_incidente': 'v3'})        
                            ).sort_values(by=['v1', 'v2', 'v3'], ascending=False)
                            # st.dataframe(df_agg_grau_dano_por_localidade)
                            
                            fig = px.sunburst(
                                df_agg_grau_dano_por_localidade, 
                                path=['v1', 'v2', 'v3'], 
                                values='Quantidade',
                            )
                            fig.update_traces(hovertemplate='<b>%{label}</b><br>Quantidade: <b>%{value}</b>')
                            fig.update_layout(margin = dict(t=0, l=0, r=0, b=0))

                            fig.update_layout(height=700)
                            st.plotly_chart(fig, theme="streamlit", use_container_width=True)







# with st.expander('CLASSIFICAÇÃO', expanded=True):
#     st.subheader('CLASSIFICAÇÃO DE INCIDENTES', anchor='classificacao')
    
#     # filtar a coluna classificacao_de_incidentes do df pelo mes selecionado    
#     df_agg_tipo_mes = (
#         df_mes
#         .groupby(['mes', 'classificacao_de_incidentes'])
#         .size()
#         .reset_index(name='Quantidade')
#         .rename(columns={'mes': 'Periodo', 'classificacao_de_incidentes': 'Tipo'})        
#     )
#     # st.write(df_agg_tipo_mes.sort_values(by='Quantidade', ascending=False).head(10))
    
#     fig = px.bar(
#         df_agg_tipo_mes.sort_values(by='Quantidade', ascending=False),
#         y="Quantidade",
#         x="Tipo",
#         # x="Quantidade",
#         # y="Tipo",
#         # orientation='h',
#         title=f'Classificação de incidentes em {sel_mes}',
#         labels={
#             "Periodo": "Semana",
#             "Quantidade": "Total Notificações",
#         },
#     )
#     fig.update_layout(height=400)
#     st.plotly_chart(fig, theme="streamlit", use_container_width=True)


# with st.expander('GRAU DE DADO', expanded=True):
#     st.subheader('CLASSIFICAÇÃO x GRAU DE DADO', anchor='grau_dado')
    
#     cols = st.columns([1, 4])
#     sel_incidente = cols[0].radio('Qual o tipo dos incidentes?', df.fillna('Sem classificação').sort_values(by='classificacao_de_incidentes', ascending=True).classificacao_de_incidentes.unique())
#     df_agg_grau_dano = (
#         df_mes.query(f'classificacao_de_incidentes=="{sel_incidente}"')
#         .groupby(['mes', 'grau_do_dano'])
#         .size()
#         .reset_index(name='Quantidade')
#         .rename(columns={'mes': 'Periodo', 'grau_do_dano': 'Variavel'})        
#     )
    
#     fig = px.pie(
#         df_agg_grau_dano.sort_values(by='Quantidade', ascending=False),
#         values="Quantidade",
#         names="Variavel",
#         title=f'Grau de dano por {sel_incidente.upper()} em {sel_mes}',
#         labels={
#             "Periodo": "Mês",
#             "Variavel": "Grau de dano",
#         },
#     )
    
#     fig.update_layout(height=600)
#     cols[1].plotly_chart(fig, theme="streamlit", use_container_width=True)
















# tabs = st.tabs(["Adesivo", "Nome do funcionário", "Setor de lotação"])

# with tabs[0]:
# 	adesivos = st.multiselect("Informe o código do adesivo:", df.sort_values(by="ADESIVO", ascending=True).ADESIVO.unique())
# 	gerar_card(df.query("ADESIVO in @adesivos"))
# 	# st.table(df.query("ADESIVO in @adesivos"))

# with tabs[1]:
# 	proprietarios = st.multiselect("Informe nome do funcionario:", df.sort_values(by="NOME", ascending=True).NOME.unique())
# 	gerar_card(df.query("NOME in (@proprietarios)"))

# with tabs[2]:
# 	lotacoes = st.multiselect("Informe setor de lotação:", df.sort_values(by="LOTACAO", ascending=True).LOTACAO.unique())
# 	gerar_card(df.query("LOTACAO in (@lotacoes)"))


# Prazo para entrega:

# 18/05 - Relatorio Histórico Indicadores desde 2015 
# 26/05 - Envio E-mail para gestor que ainda não enviou todos os indicadores
# 26/05 - Apresentar para analise de indicadores apenas os que estão divergentes dos últimos meses.
# 31/05 - Alta ( ONA )
