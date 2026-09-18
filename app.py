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
        "data:image/jpeg;base64,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"
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

# CONTROLES SUPERIORES (Definem a variável num_rodada)
c_ctrl1, c_ctrl2 = st.columns([1, 2])
with c_ctrl1:
  num_rodada = st.selectbox(
      "Rodada:", list(CALENDARIO_RODADAS.keys()), index=1
  )
with c_ctrl2:
  df_base = carregar_tabela_oficial()
  lista_times = ["Nenhum"] + sorted(df_base["nome_time"].unique().tolist())
  time_favorito = st.selectbox("⭐ Destaque o Time do Coração:", lista_times)

# POPULAR PLACARES REAIS DA RODADA 27 JÁ FINALIZADA
PLACARES_RODADA_27_REAIS = {
    ("Coritiba", "Athletico-PR"): (1, 2),
    ("Atlético-MG", "Fluminense"): (1, 1),
    ("Grêmio", "Vasco"): (2, 0),
    ("Chapecoense", "Internacional"): (0, 0),
    ("Palmeiras", "São Paulo"): (2, 1),
    ("Botafogo", "Red Bull Bragantino"): (1, 0),
    ("Santos", "Cruzeiro"): (2, 2),
    ("Mirassol", "Vitória"): (1, 0),
    ("Flamengo", "Corinthians"): (2, 0),
    ("Bahia", "Remo"): (2, 1),
}
if num_rodada == 27:
  for idx, (m, v, _) in enumerate(CALENDARIO_RODADAS[27]):
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

    if (
        r_num == 27
        and (mandante, visitante) in PLACARES_RODADA_27_REAIS
        and f"{mandante}X{visitante}" not in st.session_state.jogos_encerrados
    ):
      st.session_state.jogos_encerrados[f"{mandante}X{visitante}"] = (
          PLACARES_RODADA_27_REAIS[(mandante, visitante)]
      )

    if chave_live in st.session_state.jogos_encerrados:
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

    try:
      partes_data = data_hora_str.split(", ")[1]
      dt_jogo = datetime.strptime(
          partes_data, "%d/%m - %H:%M"
      ).replace(year=datetime.now().year)
      limite_bloqueio = dt_jogo - timedelta(minutes=5)
      if num_rodada == 27 and datetime.now() >= limite_bloqueio:
        jogo_bloqueado = True
    except Exception:
      pass

    if num_rodada == 27 and chave_live in st.session_state.jogos_encerrados:
      val_m, val_v = st.session_state.jogos_encerrados[chave_live]
      jogo_bloqueado = True
    elif (
        num_rodada == 27
        and chave_live in placar_live
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

# ABA 3: AO VIVO / PARTIDAS DA RODADA
with tab_aovivo:
  st.subheader(f"🔴 Partidas ao Vivo / Jogos da {num_rodada}ª Rodada")

  # Exibe os jogos ao vivo da API caso existam, senão exibe a agenda da rodada selecionada
  if placar_live:
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
