import streamlit as st # pip install streamlit
import pandas as pd # pip install pandas

## Google Forms
# https://docs.google.com/forms/d/1hUoQS3QCZO2uRT9eBiL9o-5pmGtdDQpG-C6WsIZI0Pg/edit#responses
#
## Google SpreadSheet
# https://docs.google.com/spreadsheets/d/1Nu43vyWJeJ1S3R1kvXHMg_r82RF0Pif_K3I1tJCnaUk/edit?resourcekey#gid=583415138
#
## 
# 

@st.cache()
def get_data():
    return pd.read_parquet("data.parquet")


st.set_page_config(
    page_title="Eventos Adversos", 
    page_icon=':tada:',
    layout="wide",
    initial_sidebar_state="auto",
    menu_items=None)

st.markdown("""<style>
    #MainMenu {visibility: hidden; }
    footer {visibility: hidden; }
    header {visibility: hidden; }
</style>""", unsafe_allow_html=True)

df = get_data()

st.header("Eventos Adversos")
placeholder = st.empty()

with st.sidebar:
    st.subheader("Filtros")
    # unidades_selecionaveis = df.UNIDADE.unique()
    # unidade_selecionada = st.selectbox("Selecione uma unidade", 
    #                                     key="unidade_selecionada", 
    #                                     options=unidades_selecionaveis)


with placeholder.container():
    tabs = st.tabs(["Estatísticas", "Dados por unidade de internação"])

    with tabs[0]:
        st.header('Estatísticas')

    with tabs[1]:
        st.header('Unidades de internação')
        st.dataframe(df)


if 'atualizar' not in st.session_state:
    st.session_state['atualizar'] = 0