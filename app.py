import streamlit as st

import pandas as pd

import requests



# Configuração da página - Layout Wide

st.set_page_config(page_title="Brasileirão 2026", layout="wide", initial_sidebar_state="collapsed")



# --- CSS PARA ELEVAR O CABEÇALHO E OTIMIZAR ESPAÇAMENTOS ---

st.markdown("""

<style>

    .block-container {

        padding-top: 0.3rem !important;

        padding-bottom: 0rem !important;

    }

    

    h1 {

        padding-top: 0rem !important;

        margin-top: -0.5rem !important;

        margin-bottom: 0.5rem !important;

        font-size: 1.8rem !important;

    }



    .stNumberInput input {

        text-align: center;

        font-size: 15px !important;

        font-weight: bold;

    }



    .status-badge { font-size: 11px; color: #555; margin-bottom: 4px; font-weight: 600; text-align: center; }



    @media (max-width: 768px) {

        .block-container {

            padding-left: 0.4rem !important;

            padding-right: 0.4rem !important;

        }

    }

</style>

""", unsafe_allow_html=True)



st.title("⚽ Brasileirão 2026")



# --- Inicialização da Session State ---

if "palpites_confirmados" not in st.session_state:

    st.session_state.palpites_confirmados = {}



# Jogo já encerrado: Coritiba 3 x 3 Athletico-PR

if "jogos_encerrados" not in st.session_state:

    st.session_state.jogos_encerrados = {

        "CoritibaXAthletico-PR": (3, 3)

    }

else:

    st.session_state.jogos_encerrados["CoritibaXAthletico-PR"] = (3, 3)



# ESCUDOS COM OPÇÕES ROBUSTAS (Mirassol e Remo ajustados para links diretos de alta compatibilidade)

ESCUDOS_TIMES = {

    "Flamengo": "https://a.espncdn.com/i/teamlogos/soccer/500/819.png",

    "Palmeiras": "https://s.sde.globo.com/media/organizations/2019/07/06/Palmeiras.svg",

    "Athletico-PR": "https://s.sde.globo.com/media/organizations/2019/09/09/Athletico-PR.svg",

    "Fluminense": "https://s.sde.globo.com/media/organizations/2018/03/11/fluminense.svg",

    "Bahia": "https://s.sde.globo.com/media/organizations/2018/03/11/bahia.svg",

    "Cruzeiro": "https://s.sde.globo.com/media/organizations/2021/02/13/cruzeiro_2021.svg",

    "Coritiba": "https://s.sde.globo.com/media/organizations/2018/03/11/coritiba.svg",

    "Atlético-MG": "https://s.sde.globo.com/media/organizations/2018/03/10/atletico-mg.svg",

    "Red Bull Bragantino": "https://a.espncdn.com/i/teamlogos/soccer/500/6079.png",

    "São Paulo": "https://s.sde.globo.com/media/organizations/2018/03/11/sao-paulo.svg",

    "Vitória": "https://a.espncdn.com/i/teamlogos/soccer/500/3456.png",

    "Corinthians": "https://s.sde.globo.com/media/organizations/2019/09/30/Corinthians.svg",

    "Santos": "https://s.sde.globo.com/media/organizations/2018/03/12/santos.svg",

    "Botafogo": "https://s.sde.globo.com/media/organizations/2019/02/04/botafogo-svg.svg",

    "Grêmio": "https://s.sde.globo.com/media/organizations/2018/03/12/gremio.svg",

    "Mirassol": "data:image/png;base64,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",

    "Vasco": "https://a.espncdn.com/i/teamlogos/soccer/500/3454.png",

    "Internacional": "https://s.sde.globo.com/media/organizations/2018/03/11/internacional.svg",

    "Remo": "data:image/png;base64,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",

    "Chapecoense": "https://s.sde.globo.com/media/organizations/2018/03/11/chapecoense.svg"

}



MAPEAMENTO_TIMES_ESPN = {

    "Athletico-PR": "Athletico-PR",

    "Athletico Paranaense": "Athletico-PR",

    "CAP": "Athletico-PR",

    "Atlético-MG": "Atlético-MG",

    "Atletico Mineiro": "Atlético-MG",

    "CAM": "Atlético-MG",

    "Red Bull Bragantino": "Red Bull Bragantino",

    "Bragantino": "Red Bull Bragantino",

    "RBB": "Red Bull Bragantino",

    "São Paulo": "São Paulo",

    "Sao Paulo": "São Paulo",

    "SPFC": "São Paulo",

    "Vasco da Gama": "Vasco",

    "Botafogo-RJ": "Botafogo",

    "Grêmio RS": "Grêmio",

    "Gremio": "Grêmio"

}



def normalizar_nome(nome):

    return MAPEAMENTO_TIMES_ESPN.get(nome, nome)



def obter_escudo(nome):

    nome_padrao = normalizar_nome(nome)

    return ESCUDOS_TIMES.get(nome_padrao, "https://s.sde.globo.com/media/organizations/2018/03/11/fluminense.svg")



# --- DADOS DA TABELA BASE OFICIAL ---

@st.cache_data(ttl=1)

def carregar_tabela_oficial():

    dados_tabela = [

        {"nome_time": "Flamengo", "pontos": 54, "jogos": 26, "vitorias": 16, "empates": 6, "derrotas": 4, "gols_pro": 51, "gols_contra": 21},

        {"nome_time": "Palmeiras", "pontos": 53, "jogos": 26, "vitorias": 15, "empates": 8, "derrotas": 3, "gols_pro": 45, "gols_contra": 21},

        {"nome_time": "Athletico-PR", "pontos": 45, "jogos": 26, "vitorias": 13, "empates": 6, "derrotas": 7, "gols_pro": 38, "gols_contra": 28},

        {"nome_time": "Fluminense", "pontos": 45, "jogos": 26, "vitorias": 12, "empates": 9, "derrotas": 5, "gols_pro": 40, "gols_contra": 32},

        {"nome_time": "Bahia", "pontos": 43, "jogos": 26, "vitorias": 11, "empates": 10, "derrotas": 5, "gols_pro": 40, "gols_contra": 32},

        {"nome_time": "Cruzeiro", "pontos": 42, "jogos": 26, "vitorias": 12, "empates": 6, "derrotas": 8, "gols_pro": 38, "gols_contra": 37},

        {"nome_time": "Coritiba", "pontos": 37, "jogos": 26, "vitorias": 10, "empates": 7, "derrotas": 9, "gols_pro": 34, "gols_contra": 35},

        {"nome_time": "Atlético-MG", "pontos": 36, "jogos": 25, "vitorias": 10, "empates": 6, "derrotas": 9, "gols_pro": 32, "gols_contra": 30},

        {"nome_time": "Red Bull Bragantino", "pontos": 35, "jogos": 25, "vitorias": 10, "empates": 5, "derrotas": 10, "gols_pro": 31, "gols_contra": 28},

        {"nome_time": "São Paulo", "pontos": 33, "jogos": 25, "vitorias": 9, "empates": 6, "derrotas": 10, "gols_pro": 31, "gols_contra": 28},

        {"nome_time": "Vitória", "pontos": 32, "jogos": 26, "vitorias": 9, "empates": 5, "derrotas": 12, "gols_pro": 25, "gols_contra": 37},

        {"nome_time": "Corinthians", "pontos": 32, "jogos": 26, "vitorias": 8, "empates": 8, "derrotas": 10, "gols_pro": 27, "gols_contra": 27},

        {"nome_time": "Santos", "pontos": 32, "jogos": 25, "vitorias": 8, "empates": 8, "derrotas": 9, "gols_pro": 37, "gols_contra": 38},

        {"nome_time": "Botafogo", "pontos": 31, "jogos": 25, "vitorias": 8, "empates": 7, "derrotas": 10, "gols_pro": 37, "gols_contra": 40},

        {"nome_time": "Grêmio", "pontos": 28, "jogos": 25, "vitorias": 7, "empates": 7, "derrotas": 11, "gols_pro": 27, "gols_contra": 33},

        {"nome_time": "Mirassol", "pontos": 28, "jogos": 26, "vitorias": 7, "empates": 7, "derrotas": 12, "gols_pro": 29, "gols_contra": 40},

        {"nome_time": "Vasco", "pontos": 25, "jogos": 25, "vitorias": 6, "empates": 7, "derrotas": 12, "gols_pro": 27, "gols_contra": 40},

        {"nome_time": "Internacional", "pontos": 25, "jogos": 26, "vitorias": 5, "empates": 10, "derrotas": 11, "gols_pro": 28, "gols_contra": 34},

        {"nome_time": "Remo", "pontos": 23, "jogos": 26, "vitorias": 5, "empates": 8, "derrotas": 13, "gols_pro": 30, "gols_contra": 43},

        {"nome_time": "Chapecoense", "pontos": 17, "jogos": 25, "vitorias": 3, "empates": 8, "derrotas": 14, "gols_pro": 27, "gols_contra": 50}

    ]

    df = pd.DataFrame(dados_tabela)

    df['saldo_gols'] = df['gols_pro'] - df['gols_contra']

    df['pos_inicial'] = df.index + 1

    return df



# API ESPN

def buscar_jogos_espn():

    url = "https://site.api.espn.com/apis/site/v2/sports/soccer/bra.1/scoreboard"

    try:

        res = requests.get(url, timeout=3)

        if res.status_code == 200:

            dados = res.json()

            eventos = dados.get('events', [])

            jogos = {}

            for ev in eventos:

                comp = ev['competitions'][0]

                m_nome = normalizar_nome(comp['competitors'][0]['team']['shortDisplayName'])

                v_nome = normalizar_nome(comp['competitors'][1]['team']['shortDisplayName'])

                

                m_score = int(comp['competitors'][0]['score']) if 'score' in comp['competitors'][0] else 0

                v_score = int(comp['competitors'][1]['score']) if 'score' in comp['competitors'][1] else 0

                

                state = ev['status']['type']['state'] 

