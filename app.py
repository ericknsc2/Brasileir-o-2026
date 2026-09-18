
from datetime import datetime, timedelta
import requests
import streamlit as st
import pandas as pd

# Configuração da página - Layout Wide
st.set_page_config(
    page_title="Brasileirão 2026",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# --- CSS PARA ELEVAR O CABEÇALHO E OTIMIZAR ESPAÇAMENTOS ---
st.markdown(
    """
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
""",
    unsafe_allow_html=True,
)

st.title("⚽ Brasileirão 2026")

# --- Inicialização da Session State ---
if "palpites_confirmados" not in st.session_state:
  st.session_state.palpites_confirmados = {}

if "jogos_encerrados" not in st.session_state:
  st.session_state.jogos_encerrados = {}

# ESCUDOS DOS TIMES
ESCUDOS_TIMES = {
    "Flamengo": "https://a.espncdn.com/i/teamlogos/soccer/500/819.png",
    "Palmeiras": (
        "https://s.sde.globo.com/media/organizations/2019/07/06/Palmeiras.svg"
    ),
    "Athletico-PR": (
        "https://s.sde.globo.com/media/organizations/2019/09/09/Athletico-PR.svg"
    ),
    "Fluminense": (
        "https://s.sde.globo.com/media/organizations/2018/03/11/fluminense.svg"
    ),
    "Bahia": "https://s.sde.globo.com/media/organizations/2018/03/11/bahia.svg",
    "Cruzeiro": (
        "https://s.sde.globo.com/media/organizations/2021/02/13/cruzeiro_2021.svg"
    ),
    "Coritiba": (
        "https://s.sde.globo.com/media/organizations/2018/03/11/coritiba.svg"
    ),
    "Atlético-MG": (
        "https://s.sde.globo.com/media/organizations/2018/03/10/atletico-mg.svg"
    ),
    "Red Bull Bragantino": (
        "https://a.espncdn.com/i/teamlogos/soccer/500/6079.png"
    ),
    "São Paulo": (
        "https://s.sde.globo.com/media/organizations/2018/03/11/sao-paulo.svg"
    ),
    "Vitória": "https://a.espncdn.com/i/teamlogos/soccer/500/3456.png",
    "Corinthians": (
        "https://s.sde.globo.com/media/organizations/2019/09/30/Corinthians.svg"
    ),
    "Santos": "https://s.sde.globo.com/media/organizations/2018/03/12/santos.svg",
    "Botafogo": (
        "https://s.sde.globo.com/media/organizations/2019/02/04/botafogo-svg.svg"
    ),
    "Grêmio": "https://s.sde.globo.com/media/organizations/2018/03/12/gremio.svg",
    "Mirassol": "https://icon2.cleanpng.com/20180623/lzg/aazulkonx.webp",
    "Vasco": "https://a.espncdn.com/i/teamlogos/soccer/500/3454.png",
    "Internacional": (
        "https://s.sde.globo.com/media/organizations/2018/03/11/internacional.svg"
    ),
    "Remo": (
        "data:image/png;base64,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"
    ),
    "Chapecoense": (
        "https://s.sde.globo.com/media/organizations/2018/03/11/chapecoense.svg"
    ),
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
    "Gremio": "Grêmio",
}


def normalizar_nome(nome):
  return MAPEAMENTO_TIMES_ESPN.get(nome, nome)


def obter_escudo(nome):
  nome_padrao = normalizar_nome(nome)
  return ESCUDOS_TIMES.get(
      nome_padrao,
      "https://s.sde.globo.com/media/organizations/2018/03/11/fluminense.svg",
  )


# --- DADOS DA TABELA BASE OFICIAL (ATUALIZADA) ---
@st.cache_data(ttl=1)
def carregar_tabela_oficial():
  dados_tabela = [
      {
          "nome_time": "Flamengo",
          "pontos": 57,
          "jogos": 27,
          "vitorias": 17,
          "empates": 6,
          "derrotas": 4,
          "gols_pro": 53,
          "gols_contra": 22,
      },
      {
          "nome_time": "Palmeiras",
          "pontos": 56,
          "jogos": 27,
          "vitorias": 16,
          "empates": 8,
          "derrotas": 3,
          "gols_pro": 47,
          "gols_contra": 21,
      },
      {
          "nome_time": "Athletico-PR",
          "pontos": 46,
          "jogos": 27,
          "vitorias": 13,
          "empates": 7,
          "derrotas": 7,
          "gols_pro": 41,
          "gols_contra": 31,
      },
      {
          "nome_time": "Bahia",
          "pontos": 46,
          "jogos": 27,
          "vitorias": 12,
          "empates": 10,
          "derrotas": 5,
          "gols_pro": 42,
          "gols_contra": 33,
      },
      {
          "nome_time": "Fluminense",
          "pontos": 45,
          "jogos": 27,
          "vitorias": 12,
          "empates": 9,
          "derrotas": 6,
          "gols_pro": 41,
          "gols_contra": 35,
      },
      {
          "nome_time": "Cruzeiro",
          "pontos": 42,
          "jogos": 27,
          "vitorias": 12,
          "empates": 6,
          "derrotas": 9,
          "gols_pro": 39,
          "gols_contra": 39,
      },
      {
          "nome_time": "Atlético-MG",
          "pontos": 39,
          "jogos": 26,
          "vitorias": 11,
          "empates": 6,
          "derrotas": 9,
          "gols_pro": 35,
          "gols_contra": 31,
      },
      {
          "nome_time": "Coritiba",
          "pontos": 38,
          "jogos": 27,
          "vitorias": 10,
          "empates": 8,
          "derrotas": 9,
          "gols_pro": 37,
          "gols_contra": 38,
      },
      {
          "nome_time": "Red Bull Bragantino",
          "pontos": 36,
          "jogos": 26,
          "vitorias": 10,
          "empates": 6,
          "derrotas": 10,
          "gols_pro": 32,
          "gols_contra": 29,
      },
      {
          "nome_time": "Santos",
          "pontos": 35,
          "jogos": 26,
          "vitorias": 9,
          "empates": 8,
          "derrotas": 9,
          "gols_pro": 39,
          "gols_contra": 39,
      },
      {
          "nome_time": "Botafogo",
          "pontos": 35,
          "jogos": 27,
          "vitorias": 9,
          "empates": 8,
          "derrotas": 10,
          "gols_pro": 41,
          "gols_contra": 43,
      },
      {
          "nome_time": "São Paulo",
          "pontos": 33,
          "jogos": 26,
          "vitorias": 9,
          "empates": 6,
          "derrotas": 11,
          "gols_pro": 31,
          "gols_contra": 30,
      },
      {
          "nome_time": "Vitória",
          "pontos": 33,
          "jogos": 27,
          "vitorias": 9,
          "empates": 6,
          "derrotas": 12,
          "gols_pro": 27,
          "gols_contra": 39,
      },
      {
          "nome_time": "Corinthians",
          "pontos": 32,
          "jogos": 27,
          "vitorias": 8,
          "empates": 8,
          "derrotas": 11,
          "gols_pro": 28,
          "gols_contra": 29,
      },
      {
          "nome_time": "Mirassol",
          "pontos": 29,
          "jogos": 27,
          "vitorias": 7,
          "empates": 8,
          "derrotas": 12,
          "gols_pro": 31,
          "gols_contra": 42,
      },
      {
          "nome_time": "Grêmio",
          "pontos": 28,
          "jogos": 27,
          "vitorias": 7,
          "empates": 7,
          "derrotas": 13,
          "gols_pro": 30,
          "gols_contra": 38,
      },
      {
          "nome_time": "Vasco",
          "pontos": 28,
          "jogos": 26,
          "vitorias": 7,
          "empates": 7,
          "derrotas": 12,
          "gols_pro": 29,
          "gols_contra": 41,
      },
      {
          "nome_time": "Internacional",
          "pontos": 28,
          "jogos": 27,
          "vitorias": 6,
          "empates": 10,
          "derrotas": 11,
          "gols_pro": 30,
          "gols_contra": 35,
      },
      {
          "nome_time": "Remo",
          "pontos": 23,
          "jogos": 27,
          "vitorias": 5,
          "empates": 8,
          "derrotas": 14,
          "gols_pro": 31,
          "gols_contra": 45,
      },
      {
          "nome_time": "Chapecoense",
          "pontos": 17,
          "jogos": 26,
          "vitorias": 3,
          "empates": 8,
          "derrotas": 15,
          "gols_pro": 28,
          "gols_contra": 52,
      },
  ]
  df = pd.DataFrame(dados_tabela)
  df["saldo_gols"] = df["gols_pro"] - df["gols_contra"]
  df["pos_inicial"] = df.index + 1
  return df


# API ESPN (Com User-Agent para evitar bloqueios)
def buscar_jogos_espn():
  url = "https://site.api.espn.com/apis/site/v2/sports/soccer/bra.1/scoreboard"
  headers = {
      "User-Agent": (
          "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,"
          " like Gecko) Chrome/120.0.0.0 Safari/537.36"
      )
  }
  try:
    res = requests.get(url, headers=headers, timeout=3)
    if res.status_code == 200:
      dados = res.json()
      eventos = dados.get("events", [])
      jogos = {}
      for ev in eventos:
        comp = ev["competitions"][0]
        m_nome = normalizar_nome(
            comp["competitors"][0]["team"]["shortDisplayName"]
        )
        v_nome = normalizar_nome(
            comp["competitors"][1]["team"]["shortDisplayName"]
        )

        m_score = (
            int(comp["competitors"][0]["score"])
            if "score" in comp["competitors"][0]
            else 0
        )
        v_score = (
            int(comp["competitors"][1]["score"])
            if "score" in comp["competitors"][1]
            else 0
        )

        state = ev["status"]["type"]["state"]
        detail = ev["status"]["type"]["shortDetail"]

        chave = f"{m_nome}X{v_nome}"
        jogos[chave] = {
            "gm": m_score,
            "gv": v_score,
            "state": state,
            "detail": detail,
        }

        if state == "post":
          st.session_state.jogos_encerrados[chave] = (m_score, v_score)
      return jogos
  except Exception:
    pass
  return {}


# --- CALENDÁRIO COMPLETO ATÉ A RODADA 38 ---
CALENDARIO_RODADAS = {
    27: [
        ("Coritiba", "Athletico-PR", "Sexta, 11/09 - 21:00"),
        ("Atlético-MG", "Fluminense", "Sábado, 12/09 - 16:00"),
        ("Grêmio", "Vasco", "Sábado, 12/09 - 16:00"),
        ("Chapecoense", "Internacional", "Sábado, 12/09 - 17:00"),
        ("Palmeiras", "São Paulo", "Sábado, 12/09 - 18:30"),
        ("Botafogo", "Red Bull Bragantino", "Sábado, 12/09 - 20:30"),
        ("Santos", "Cruzeiro", "Sábado, 12/09 - 21:00"),
        ("Mirassol", "Vitória", "Domingo, 13/09 - 16:00"),
        ("Flamengo", "Corinthians", "Domingo, 13/09 - 17:30"),
        ("Bahia", "Remo", "Segunda, 14/09 - 20:00"),
    ],
    28: [
        ("Atlético-MG", "Chapecoense", "Sábado, 19/09 - 16:00"),
        ("Mirassol", "Botafogo", "Sábado, 19/09 - 17:00"),
        ("Remo", "Santos", "Sábado, 19/09 - 18:30"),
        ("Vasco", "Coritiba", "Sábado, 19/09 - 20:30"),
        ("São Paulo", "Internacional", "Sábado, 19/09 - 21:00"),
        ("Grêmio", "Palmeiras", "Domingo, 20/09 - 11:00"),
        ("Vitória", "Cruzeiro", "Domingo, 20/09 - 16:00"),
        ("Corinthians", "Fluminense", "Domingo, 20/09 - 16:00"),
        ("Red Bull Bragantino", "Flamengo", "Domingo, 20/09 - 18:30"),
        ("Athletico-PR", "Bahia", "Segunda, 21/09 - 20:00"),
    ],
    29: [
        ("Fluminense", "Grêmio", "Sábado, 26/09 - 16:00"),
        ("Palmeiras", "Mirassol", "Sábado, 26/09 - 18:30"),
        ("Cruzeiro", "Vasco", "Sábado, 26/09 - 21:00"),
        ("Bahia", "Atlético-MG", "Domingo, 27/09 - 16:00"),
        ("Flamengo", "São Paulo", "Domingo, 27/09 - 16:00"),
        ("Internacional", "Corinthians", "Domingo, 27/09 - 18:30"),
        ("Botafogo", "Remo", "Domingo, 27/09 - 18:30"),
        ("Santos", "Athletico-PR", "Segunda, 28/09 - 20:00"),
        ("Coritiba", "Red Bull Bragantino", "Segunda, 28/09 - 20:00"),
        ("Chapecoense", "Vitória", "Segunda, 28/09 - 21:00"),
    ],
    30: [
        ("Atlético-MG", "Palmeiras", "Sábado, 03/10 - 16:00"),
        ("Vasco", "Flamengo", "Sábado, 03/10 - 18:30"),
        ("Grêmio", "Santos", "Sábado, 03/10 - 21:00"),
        ("São Paulo", "Bahia", "Domingo, 04/10 - 16:00"),
        ("Corinthians", "Botafogo", "Domingo, 04/10 - 16:00"),
        ("Red Bull Bragantino", "Internacional", "Domingo, 04/10 - 18:30"),
        ("Mirassol", "Fluminense", "Domingo, 04/10 - 18:30"),
        ("Athletico-PR", "Chapecoense", "Segunda, 05/10 - 20:00"),
        ("Remo", "Coritiba", "Segunda, 05/10 - 20:00"),
        ("Vitória", "Cruzeiro", "Segunda, 05/10 - 21:00"),
    ],
    31: [
        ("Flamengo", "Grêmio", "Sábado, 10/10 - 16:00"),
        ("Palmeiras", "Vasco", "Sábado, 10/10 - 18:30"),
        ("Fluminense", "São Paulo", "Sábado, 10/10 - 21:00"),
        ("Botafogo", "Atlético-MG", "Domingo, 11/10 - 16:00"),
        ("Bahia", "Corinthians", "Domingo, 11/10 - 16:00"),
        ("Santos", "Mirassol", "Domingo, 11/10 - 18:30"),
        ("Internacional", "Remo", "Domingo, 11/10 - 18:30"),
        ("Coritiba", "Vitória", "Segunda, 12/10 - 20:00"),
        ("Chapecoense", "Red Bull Bragantino", "Segunda, 12/10 - 20:00"),
        ("Cruzeiro", "Athletico-PR", "Segunda, 12/10 - 21:00"),
    ],
    32: [
        ("Atlético-MG", "Santos", "Sábado, 17/10 - 16:00"),
        ("Grêmio", "Bahia", "Sábado, 17/10 - 18:30"),
        ("São Paulo", "Coritiba", "Sábado, 17/10 - 21:00"),
        ("Vasco", "Fluminense", "Domingo, 18/10 - 16:00"),
        ("Corinthians", "Palmeiras", "Domingo, 18/10 - 16:00"),
        ("Red Bull Bragantino", "Botafogo", "Domingo, 18/10 - 18:30"),
        ("Mirassol", "Flamengo", "Domingo, 18/10 - 18:30"),
        ("Remo", "Chapecoense", "Segunda, 19/10 - 20:00"),
        ("Vitória", "Internacional", "Segunda, 19/10 - 20:00"),
        ("Athletico-PR", "Cruzeiro", "Segunda, 19/10 - 21:00"),
    ],
    33: [
        ("Flamengo", "Atlético-MG", "Sábado, 24/10 - 16:00"),
        ("Palmeiras", "Red Bull Bragantino", "Sábado, 24/10 - 18:30"),
        ("Fluminense", "Remo", "Sábado, 24/10 - 21:00"),
        ("Botafogo", "São Paulo", "Domingo, 25/10 - 16:00"),
        ("Bahia", "Vasco", "Domingo, 25/10 - 16:00"),
        ("Santos", "Corinthians", "Domingo, 25/10 - 18:30"),
        ("Coritiba", "Grêmio", "Domingo, 25/10 - 18:30"),
        ("Internacional", "Athletico-PR", "Segunda, 26/10 - 20:00"),
        ("Chapecoense", "Mirassol", "Segunda, 26/10 - 20:00"),
        ("Cruzeiro", "Vitória", "Segunda, 26/10 - 21:00"),
    ],
    34: [
        ("Atlético-MG", "Coritiba", "Sábado, 31/10 - 16:00"),
        ("Grêmio", "Botafogo", "Sábado, 31/10 - 18:30"),
        ("São Paulo", "Santos", "Sábado, 31/10 - 21:00"),
        ("Vasco", "Internacional", "Domingo, 01/11 - 16:00"),
        ("Corinthians", "Flamengo", "Domingo, 01/11 - 16:00"),
        ("Red Bull Bragantino", "Fluminense", "Domingo, 01/11 - 18:30"),
        ("Mirassol", "Bahia", "Domingo, 01/11 - 18:30"),
        ("Remo", "Palmeiras", "Segunda, 02/11 - 20:00"),
        ("Vitória", "Chapecoense", "Segunda, 02/11 - 20:00"),
        ("Athletico-PR", "Remo", "Segunda, 02/11 - 21:00"),
    ],
    35: [
        ("Flamengo", "Palmeiras", "Sábado, 07/11 - 16:00"),
        ("Fluminense", "Athletico-PR", "Sábado, 07/11 - 18:30"),
        ("Botafogo", "Vasco", "Sábado, 07/11 - 21:00"),
        ("Bahia", "Red Bull Bragantino", "Domingo, 08/11 - 16:00"),
        ("Santos", "Vitória", "Domingo, 08/11 - 16:00"),
        ("Coritiba", "Corinthians", "Domingo, 08/11 - 18:30"),
        ("Internacional", "Atlético-MG", "Domingo, 08/11 - 18:30"),
        ("Chapecoense", "Grêmio", "Segunda, 09/11 - 20:00"),
        ("Remo", "Mirassol", "Segunda, 09/11 - 20:00"),
        ("Cruzeiro", "São Paulo", "Segunda, 09/11 - 21:00"),
    ],
    36: [
        ("Atlético-MG", "Cruzeiro", "Sábado, 21/11 - 16:00"),
        ("Palmeiras", "Bahia", "Sábado, 21/11 - 18:30"),
        ("Grêmio", "Internacional", "Sábado, 21/11 - 21:00"),
        ("São Paulo", "Remo", "Domingo, 22/11 - 16:00"),
        ("Vasco", "Santos", "Domingo, 22/11 - 16:00"),
        ("Corinthians", "Chapecoense", "Domingo, 22/11 - 18:30"),
        ("Red Bull Bragantino", "Mirassol", "Domingo, 22/11 - 18:30"),
        ("Athletico-PR", "Flamengo", "Segunda, 23/11 - 20:00"),
        ("Vitória", "Botafogo", "Segunda, 23/11 - 20:00"),
        ("Coritiba", "Fluminense", "Segunda, 23/11 - 21:00"),
    ],
    37: [
        ("Flamengo", "Cruzeiro", "Quarta, 25/11 - 20:00"),
        ("Fluminense", "Bahia", "Quarta, 25/11 - 20:00"),
        ("Botafogo", "Palmeiras", "Quarta, 25/11 - 21:30"),
        ("Grêmio", "Atlético-MG", "Quarta, 25/11 - 21:30"),
        ("Santos", "Chapecoense", "Quinta, 26/11 - 19:00"),
        ("Corinthians", "São Paulo", "Quinta, 26/11 - 20:00"),
        ("Vasco", "Vitória", "Quinta, 26/11 - 20:00"),
        ("Mirassol", "Athletico-PR", "Quinta, 26/11 - 21:30"),
        ("Remo", "Red Bull Bragantino", "Quinta, 26/11 - 21:30"),
        ("Internacional", "Coritiba", "Quinta, 26/11 - 21:30"),
    ],
    38: [
        ("Atlético-MG", "Mirassol", "Domingo, 29/11 - 16:00"),
        ("Palmeiras", "Fluminense", "Domingo, 29/11 - 16:00"),
        ("Bahia", "Santos", "Domingo, 29/11 - 16:00"),
        ("São Paulo", "Vasco", "Domingo, 29/11 - 16:00"),
        ("Cruzeiro", "Corinthians", "Domingo, 29/11 - 16:00"),
        ("Red Bull Bragantino", "Grêmio", "Domingo, 29/11 - 16:00"),
        ("Athletico-PR", "Botafogo", "Domingo, 29/11 - 16:00"),
        ("Vitória", "Flamengo", "Domingo, 29/11 - 16:00"),
        ("Coritiba", "Remo", "Domingo, 29/11 - 16:00"),
        ("Chapecoense", "Internacional", "Domingo, 29/11 - 16:00"),
    ],
}

placar_live = buscar_jogos_espn()

# CONTROLES SUPERIORES (Definem a variável num_rodada de forma dinâmica e segura)
c_ctrl1, c_ctrl2 = st.columns([1, 2])
with c_ctrl1:
  rodadas_disponiveis = sorted(list(CALENDARIO_RODADAS.keys()))
  default_idx = (
      rodadas_disponiveis.index(27) if 27 in rodadas_disponiveis else 0
  )
  num_rodada = st.selectbox(
      "Rodada:", rodadas_disponiveis, index=default_idx
  )
with c_ctrl2:
  df_base = carregar_tabela_oficial()
  lista_times = ["Nenhum"] + sorted(df_base["nome_time"].unique().tolist())
  time_favorito = st.selectbox("⭐ Destaque o Time do Coração:", lista_times)

    # PLACARES REAIS OFICIAIS DA RODADA 27
PLACARES_RODADA_27_REAIS = {
    ("Coritiba", "Athletico-PR"): (1, 2),
    ("Atlético-MG", "Fluminense"): (3, 1),
    ("Grêmio", "Vasco"): (1, 2),
    ("Chapecoense", "Internacional"): (1, 2),
    ("Palmeiras", "São Paulo"): (2, 0),
    ("Botafogo", "Red Bull Bragantino"): (1, 1),
    ("Santos", "Cruzeiro"): (2, 1),
    ("Mirassol", "Vitória"): (2, 2),
    ("Flamengo", "Corinthians"): (2, 1),
    ("Bahia", "Remo"): (2, 1),
}

# --- BLINDAGEM DE SEGURANÇA PARA A RODADA 27 ---
# Garante que CALENDARIO_RODADAS é um dicionário antes de chamar .get()
if isinstance(CALENDARIO_RODADAS, dict):
  jogos_r27 = CALENDARIO_RODADAS.get(27, [])
  for m, v, _ in jogos_r27:  # Adicionado o '_' para capturar a data/hora
    if (m, v) in PLACARES_RODADA_27_REAIS:
      st.session_state.jogos_encerrados[f"{m}X{v}"] = PLACARES_RODADA_27_REAIS[
          (m, v)
      ]
# --- CÁLCULO REATIVO DA TABELA ---
df_simulado = df_base.copy()

for r_num, lista_jogos in CALENDARIO_RODADAS.items():
  for idx, (mandante, visitante, _) in enumerate(lista_jogos):
    chave_live = f"{mandante}X{visitante}"
    chave_sim = f"sim_r{r_num}_{idx}"

    jogou = False
    gm, gv = 0, 0

    if r_num == 27 and (mandante, visitante) in PLACARES_RODADA_27_REAIS:
      gm, gv = PLACARES_RODADA_27_REAIS[(mandante, visitante)]
      jogou = True
    elif chave_live in st.session_state.jogos_encerrados:
      gm, gv = st.session_state.jogos_encerrados[chave_live]
      jogou = True
    elif (
        r_num == 27
        and chave_live in placar_live
        and placar_live[chave_live]["state"] in ["in", "post"]
    ):
      gm = placar_live[chave_live]["gm"]
      gv = placar_live[chave_live]["gv"]
      jogou = True
    elif chave_sim in st.session_state.palpites_confirmados:
      gm, gv = st.session_state.palpites_confirmados[chave_sim]
      jogou = True

    if (
        jogou
        and mandante in df_simulado["nome_time"].values
        and visitante in df_simulado["nome_time"].values
    ):
      idx_m = df_simulado[df_simulado["nome_time"] == mandante].index[0]
      idx_v = df_simulado[df_simulado["nome_time"] == visitante].index[0]

      df_simulado.at[idx_m, "jogos"] += 1
      df_simulado.at[idx_v, "jogos"] += 1
      df_simulado.at[idx_m, "gols_pro"] += gm
      df_simulado.at[idx_m, "gols_contra"] += gv
      df_simulado.at[idx_v, "gols_pro"] += gv
      df_simulado.at[idx_v, "gols_contra"] += gm

      if gm > gv:
        df_simulado.at[idx_m, "pontos"] += 3
        df_simulado.at[idx_m, "vitorias"] += 1
        df_simulado.at[idx_v, "derrotas"] += 1
      elif gv > gm:
        df_simulado.at[idx_v, "pontos"] += 3
        df_simulado.at[idx_v, "vitorias"] += 1
        df_simulado.at[idx_m, "derrotas"] += 1
      else:
        df_simulado.at[idx_m, "pontos"] += 1
        df_simulado.at[idx_v, "pontos"] += 1
        df_simulado.at[idx_m, "empates"] += 1
        df_simulado.at[idx_v, "empates"] += 1

df_simulado["saldo_gols"] = df_simulado["gols_pro"] - df_simulado["gols_contra"]
df_simulado["aproveitamento"] = (
    df_simulado["pontos"] / (df_simulado["jogos"] * 3) * 100
).round(1)
df_simulado = df_simulado.sort_values(
    by=["pontos", "vitorias", "saldo_gols", "gols_pro"], ascending=False
).reset_index(drop=True)
df_simulado["pos_atual"] = df_simulado.index + 1


def calcular_variacao(row):
  diff = row["pos_inicial"] - row["pos_atual"]
  if diff > 0:
    return f"🟢 ⬆️ +{diff}"
  elif diff < 0:
    return f"🔴 ⬇️ {diff}"
  else:
    return "➖"


df_simulado["var"] = df_simulado.apply(calcular_variacao, axis=1)
df_simulado["escudo"] = df_simulado["nome_time"].apply(obter_escudo)


def colorir_zonas(val):
  cores = []
  for i in range(len(val)):
    posicao = i + 1
    nome_time = df_simulado.iloc[i]["nome_time"]
    if time_favorito != "Nenhum" and nome_time == time_favorito:
      cores.append(
          "background-color: #ffe8a1; color: #000000; font-weight: bold;"
      )
      continue
    if posicao <= 4:
      cores.append("background-color: #d4edda; color: #155724;")
    elif posicao == 5:
      cores.append("background-color: #cce5ff; color: #004085;")
    elif 6 <= posicao <= 11:
      cores.append("background-color: #fff3cd; color: #856404;")
    elif 17 <= posicao <= 20:
      cores.append("background-color: #f8d7da; color: #721c24;")
    else:
      cores.append("")
  return cores


# --- ABAS ---
tab_tabela, tab_simulador, tab_aovivo = st.tabs(
    ["📊 Classificação", "🎮 Simulador", "🔴 Ao Vivo"]
)

# Proteção absoluta com .get()
confrontos_rodada_atual = CALENDARIO_RODADAS.get(num_rodada, [])

# ABA 1: CLASSIFICAÇÃO
with tab_tabela:
  if not df_simulado.empty:
    m1, m2 = st.columns(2)
    m1.metric(
        "🏆 Líder",
        f"{df_simulado.iloc[0]['nome_time']}",
        f"{df_simulado.iloc[0]['pontos']} pts",
    )
    m2.metric(
        "🛡️ G-4",
        f"{df_simulado.iloc[3]['nome_time']}",
        f"{df_simulado.iloc[3]['pontos']} pts",
    )

    cols_exibir = [
        "escudo",
        "nome_time",
        "pontos",
        "jogos",
        "vitorias",
        "empates",
        "derrotas",
        "gols_pro",
        "gols_contra",
        "saldo_gols",
        "aproveitamento",
    ]

    df_exibir = df_simulado[cols_exibir].copy()
    df_exibir["nome_time"] = df_simulado["nome_time"] + " " + df_simulado["var"]
    df_exibir.index = df_simulado["pos_atual"]

    st.dataframe(
        df_exibir.style.apply(colorir_zonas, axis=0).format(
            {"aproveitamento": "{:.1f}%"}
        ),
        column_config={
            "escudo": st.column_config.ImageColumn(
                "Escudo", help="Escudo do clube", width="small"
            ),
            "nome_time": st.column_config.TextColumn("Clube"),
        },
        use_container_width=True,
        hide_index=False,
        height=820,
    )
    st.caption("🟢 G-4 | 🔵 Pré-Libertadores | 🟡 Sul-Americana | 🔴 Z-4")

# ABA 2: SIMULADOR
with tab_simulador:
  st.subheader(f"🎮 Palpites para a {num_rodada}ª Rodada")

  col_btn1, col_btn2 = st.columns(2)
  with col_btn1:
    if st.button("🧮 Calcular Todos os Palpites"):
      for idx in range(len(confrontos_rodada_atual)):
        key_m = f"input_r{num_rodada}_m_{idx}"
        key_v = f"input_r{num_rodada}_v_{idx}"
        if key_m in st.session_state and key_v in st.session_state:
          gm = st.session_state[key_m]
          gv = st.session_state[key_v]
          if gm is not None and gv is not None:
            st.session_state.palpites_confirmados[f"sim_r{num_rodada}_{idx}"] = (
                gm,
                gv,
            )
      st.rerun()

  with col_btn2:
    if st.button("🧹 Limpar Meus Palpites"):
      st.session_state.palpites_confirmados.clear()
      for idx in range(len(confrontos_rodada_atual)):
        st.session_state[f"input_r{num_rodada}_m_{idx}"] = 0
        st.session_state[f"input_r{num_rodada}_v_{idx}"] = 0
      st.rerun()

  st.write("")

  for idx, (mandante, visitante, data_hora_str) in enumerate(
      confrontos_rodada_atual
  ):
    chave_live = f"{mandante}X{visitante}"
    chave_sim = f"sim_r{num_rodada}_{idx}"

    jogo_bloqueado = False
    val_m, val_v = 0, 0

    if num_rodada == 27 and (mandante, visitante) in PLACARES_RODADA_27_REAIS:
      val_m, val_v = PLACARES_RODADA_27_REAIS[(mandante, visitante)]
      jogo_bloqueado = True
    else:
      try:
        partes_data = data_hora_str.split(", ")[1]
        dt_jogo = datetime.strptime(
            partes_data, "%d/%m - %H:%M"
        ).replace(year=datetime.now().year)
        limite_bloqueio = dt_jogo - timedelta(minutes=5)
        if datetime.now() >= limite_bloqueio:
          jogo_bloqueado = True
      except Exception:
        pass

      if chave_live in st.session_state.jogos_encerrados:
        val_m, val_v = st.session_state.jogos_encerrados[chave_live]
        jogo_bloqueado = True
      elif (
          chave_live in placar_live
          and placar_live[chave_live]["state"] in ["in", "post"]
      ):
        val_m = placar_live[chave_live]["gm"]
        val_v = placar_live[chave_live]["gv"]
        jogo_bloqueado = True
      elif chave_sim in st.session_state.palpites_confirmados:
        val_m, val_v = st.session_state.palpites_confirmados[chave_sim]

    col_m, col_img_m, col_txt, col_img_v, col_v = st.columns(
        [1.2, 0.6, 2.2, 0.6, 1.2]
    )

    with col_m:
      val_m = st.number_input(
          f"Gols {mandante}",
          min_value=0,
          max_value=20,
          value=int(val_m),
          key=f"input_r{num_rodada}_m_{idx}",
          disabled=jogo_bloqueado,
          label_visibility="collapsed",
      )
    with col_img_m:
      st.image(obter_escudo(mandante), width=30)
    with col_txt:
      st.markdown(
          f"<div class='status-badge'>{data_hora_str}</div><p"
          f" style='text-align:center; font-weight:bold; margin:0;'>{mandante}"
          f" x {visitante}</p>",
          unsafe_allow_html=True,
      )
    with col_img_v:
      st.image(obter_escudo(visitante), width=30)
    with col_v:
      val_v = st.number_input(
          f"Gols {visitante}",
          min_value=0,
          max_value=20,
          value=int(val_v),
          key=f"input_r{num_rodada}_v_{idx}",
          disabled=jogo_bloqueado,
          label_visibility="collapsed",
      )

    if not jogo_bloqueado:
      st.session_state.palpites_confirmados[chave_sim] = (val_m, val_v)

    st.markdown("---")

# ABA 3: AO VIVO / PLACARES DA RODADA SELECIONADA
with tab_aovivo:
  st.subheader(f"🔴 Placar / Jogos da {num_rodada}ª Rodada")

  if num_rodada == 27:
    st.success("Resultados oficiais da **Rodada 27** já encerrada:")
    for mandante, visitante, data_hora_str in confrontos_rodada_atual:
      gm, gv = PLACARES_RODADA_27_REAIS.get((mandante, visitante), (0, 0))
      col_img_m, col_txt, col_img_v = st.columns([0.6, 3.8, 0.6])
      with col_img_m:
        st.image(obter_escudo(mandante), width=28)
      with col_txt:
        st.markdown(
            f"<div style='text-align: center;'><b>{mandante}</b> &nbsp;&nbsp;<span"
            f" style='font-size: 1.1em; color: #d9534f;'><b>{gm} x"
            f" {gv}</b></span>&nbsp;&nbsp; <b>{visitante}</b><br><span"
            f" style='font-size: 0.85em; color: #666;'>{data_hora_str} (Encerrado)</span></div>",
            unsafe_allow_html=True,
        )
      with col_img_v:
        st.image(obter_escudo(visitante), width=28)
      st.markdown("---")
  elif placar_live:
    for chave, info in placar_live.items():
      times = chave.split("X")
      if len(times) == 2:
        m_nome, v_nome = times[0], times[1]
        st.write(
            f"**{m_nome}** {info['gm']} x {info['gv']} **{v_nome}** —"
            f" *Status: {info['detail']}*"
        )
  else:
    st.info(
        f"Nenhum jogo ao vivo no momento pela API da ESPN. Exibindo os"
        f" confrontos programados para a **Rodada {num_rodada}**:"
    )
    for mandante, visitante, data_hora_str in confrontos_rodada_atual:
      col_img_m, col_txt, col_img_v = st.columns([0.6, 3.8, 0.6])
      with col_img_m:
        st.image(obter_escudo(mandante), width=28)
      with col_txt:
        st.markdown(
            f"**{mandante} x {visitante}** &nbsp;&nbsp;|&nbsp;&nbsp; *{data_hora_str}*"
        )
      with col_img_v:
        st.image(obter_escudo(visitante), width=28)
      st.markdown("---")
