from datetime import datetime, date, timedelta
from io import StringIO
import requests # pip install requests
import pandas as pd # pip install pandas
import streamlit as st # pip install streamlit
import plotly.graph_objects as go
import plotly.express as px

## Google Forms
# https://docs.google.com/forms/d/1hUoQS3QCZO2uRT9eBiL9o-5pmGtdDQpG-C6WsIZI0Pg/edit#responses
#
## Google SpreadSheet
# https://docs.google.com/spreadsheets/d/1Nu43vyWJeJ1S3R1kvXHMg_r82RF0Pif_K3I1tJCnaUk/edit?resourcekey#gid=583415138
#
## Dados CSV
# https://docs.google.com/spreadsheets/d/e/2PACX-1vSOr5Q2RvQYwF1EMCyA43kDu-eEkA-m6Mmy_TNWxapsal78_v8hX8XEtwlllyJVv7fD-J1WRV03uHBN/pub?gid=583415138&single=true&output=csv

def read_spreadsheet(url: str) -> pd.DataFrame:
    content = requests.get(url).content
    df = pd.read_csv(StringIO(content.decode('utf-8')))
    # df.columns = df.columns.str.lower().str.replace(' ', '_').str.replace('/', '_')
    df.columns = [ f"col_{n}" for n in range(len(df.columns))]
    df['ano'] = df['col_8'].str[6:11] #.astype(int)
    df['mes'] = df['col_8'].str[3:5] #.astype(int)
    # df['ano'] = df['data'].str[-4:] #.astype(int)
    # df['mes'] = df['data'].str[3:5] #.astype(int)
    df['classificacao'] = df['col_126'].astype(str)
    
    # remover as colunas onde todos os dados são nulos
    df = df.dropna(axis=1, how='all')

    return(df)

# @st.cache_data()
def get_data():
    # url = "https://docs.google.com/spreadsheets/d/1uP1yIENzwkEJPH7xIMm-eWVV_p40qOI3mvZd3-L4gqw/pub?gid=0&single=true&output=csv"
    url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSOr5Q2RvQYwF1EMCyA43kDu-eEkA-m6Mmy_TNWxapsal78_v8hX8XEtwlllyJVv7fD-J1WRV03uHBN/pub?gid=583415138&single=true&output=csv"
    df = read_spreadsheet(url)
    return df

def grafico_001(df_p0):
    # converte a coluna 'periodo' em uma lista de strings
    periodo_str = df_p0['periodo'].dt.strftime('%Y-%m-%d').tolist()

    # obtém a data atual
    data_atual = datetime.now()

    # cria o objeto Scatter
    # scatter = go.Scatter(x=periodo_str, y=df_p0['classificacao'], mode='lines')
    scatter = go.Scatter(x=periodo_str, 
                        y=df_p0['classificacao'],
                        mode='markers+lines', 
                        marker=dict(size=7, color="royalblue"),
                        hovertemplate='Total: %{y}<br>Periodo: %{x}')

    # cria o objeto Figure
    fig = go.Figure(scatter)

    # define o layout do gráfico
    fig.update_layout(
        xaxis=dict(range=[periodo_str[0], data_atual.strftime('%Y-%m-%d')]),
        template='plotly_white',
        title='<b>Notificações de eventos adversos</b><br><sup>Evolução das notificações realizadas</sup>',
        xaxis_title='',
        yaxis_title='Total de notificações',
        height=400,
    )

    # exibe o gráfico
    # fig.show()
    return fig


st.set_page_config(
    page_title="Eventos Adversos", 
    page_icon=':bell:',
    layout="wide",
    initial_sidebar_state="auto",
    menu_items=None)

st.markdown("""<style>
    #MainMenu {visibility: hidden; }
    footer {visibility: hidden; }
    header {visibility: hidden; }
</style>""", unsafe_allow_html=True)

df = get_data()

# filtra apenas os que tiverem 'Data da ocorrência'
df1 = df[df['col_8'].map(lambda x: len(str(x))) == 10].sort_values(by="col_8", ascending=True)
df1['ano'] = df1['ano'].astype(int)
df1['mes'] = df1['mes'].astype(int)
df1['col_8'] = pd.to_datetime(df1['col_8'])
df1['periodo'] = pd.to_datetime(df1['ano'].astype(str) + '-' + df1['mes'].astype(str) + '-01')



st.header("Monitoramento de Notificações de Segurança do Paciente")
placeholder = st.empty()

with st.sidebar:
    st.subheader("Filtros")
    
    data_atual = date.today()
    # calcula a data do mês anterior
    periodo_anterior = date(data_atual.year, data_atual.month, 1) - timedelta(days=365)
    # calcula o primeiro dia do mês anterior
    primeiro_dia_mes_anterior = date(periodo_anterior.year, periodo_anterior.month, 1)

    # cria um input para ler um range de datas
    data_inicio = st.date_input('Selecione a data de início', value=primeiro_dia_mes_anterior)
    data_fim = st.date_input('Selecione a data de fim', value=data_atual)

    # verifica se as datas foram selecionadas
    # if data_inicio is not None and data_fim is not None:
    #     st.write('Você selecionou o range de datas de {} até {}'.format(data_inicio, data_fim))
    # unidades_selecionaveis = df.UNIDADE.unique()
    # unidade_selecionada = st.selectbox("Selecione uma unidade", 
    #                                     key="unidade_selecionada", 
    #                                     options=unidades_selecionaveis)
    unidades_selecionaveis = df.sort_values(by='col_10', ascending=True).col_10.unique()
    unidades_selecionadas = st.multiselect("Selecione uma unidade de internação", 
                                        options=unidades_selecionaveis,
                                        default=unidades_selecionaveis)

df_filtrado = df1.query('col_8>=@data_inicio and col_8<=@data_fim and col_10 in @unidades_selecionadas').sort_values(by="col_8", ascending=True)
df_p0 = df_filtrado[['periodo', 'classificacao']].groupby(['periodo']).count().reset_index().sort_values(by=['periodo'], ascending=True)
df_p1 = df_p0.set_index('periodo')

with placeholder.container():
    tabs = st.tabs(["Estatísticas", "Dados por unidade de internação"])

    with tabs[0]:
        st.header('Dados limpos')
        st.metric(label=f"Total de notificações", value=df_filtrado.shape[0])
        st.write(f"Notificações registradas entre {data_inicio} e {data_fim}")
        st.dataframe(df_filtrado)
        st.plotly_chart(grafico_001(df_p0), use_container_width=True)
        st.dataframe(df_filtrado[['col_8', 'periodo', 'classificacao']].groupby(['periodo', 'classificacao']).count().reset_index().sort_values(by=['periodo', 'classificacao'], ascending=True))
        st.plotly_chart(px.line(df_filtrado[['col_8', 'periodo', 'classificacao']].groupby(['periodo', 'classificacao']).count().reset_index().sort_values(by=['periodo', 'classificacao'], ascending=True), x='periodo', y='col_8', color='classificacao'))
        st.plotly_chart(px.bar(df_filtrado[['col_8', 'periodo', 'col_10']].groupby(['periodo', 'col_10']).count().reset_index().sort_values(by=['periodo', 'col_10'], ascending=True), x='periodo', y='col_8', color='col_10', barmode="group"))
        
        st.header('Dados completos')
        st.dataframe(df)
        st.header('Dados sem data nula')
        st.dataframe(df.query("col_0.notnull()").sort_values(by="col_0", ascending=True))
        st.header('Dados com data nula')
        st.dataframe(df.query("col_0.isnull()").sort_values(by="col_0", ascending=True))
        st.header('Dados históricos')
        st.dataframe(df.query("col_0.notnull()")[['col_0', 'ano', 'mes', 'col_126']].groupby(['ano', 'mes', 'col_126']).count().reset_index().sort_values(by=['ano', 'mes', 'col_126'], ascending=True))

    with tabs[1]:
        st.header('Unidades de internação')
        st.dataframe(df)


if 'atualizar' not in st.session_state:
    st.session_state['atualizar'] = 0