from datetime import datetime, timedelta
import pandas as pd
import requests
import streamlit as st

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

# ESCUDOS DOS TIMES (COM CORREÇÃO DO VITÓRIA)
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
    "Vitória": "https://s.sde.globo.com/media/organizations/2018/03/12/vitoria.svg",
    "Corinthians": (
        "https://s.sde.globo.com/media/organizations/2019/09/30/Corinthians.svg"
    ),
    "Santos": "https://s.sde.globo.com/media/organizations/2018/03/12/santos.svg",
    "Botafogo": (
        "https://s.sde.globo.com/media/organizations/2019/02/04/botafogo-svg.svg"
    ),
    "Grêmio": "https://s.sde.globo.com/media/organizations/2018/03/12/gremio.svg",
    "Mirassol": (
        "data:image/jpeg;base64,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"
    ),
    "Vasco": "https://a.espncdn.com/i/teamlogos/soccer/500/3454.png",
    "Internacional": (
        "https://s.sde.globo.com/media/organizations/2018/03/11/internacional.svg"
    ),
    "Remo": "data:image/png;base64,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",
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
    "Vasco": "Vasco",
    "Botafogo-RJ": "Botafogo",
    "Botafogo": "Botafogo",
    "Grêmio RS": "Grêmio",
    "Gremio": "Grêmio",
    "Clube do Remo": "Remo",
    "Remo": "Remo",
}


def normalizar_nome(nome):
  return MAPEAMENTO_TIMES_ESPN.get(nome, nome)


def obter_escudo(nome):
  nome_padrao = normalizar_nome(nome)
  return ESCUDOS_TIMES.get(
      nome_padrao,
      "https://s.sde.globo.com/media/organizations/2018/03/11/fluminense.svg",
  )


# --- DADOS DA TABELA BASE OFICIAL (Atualizada até o Fim da Rodada 28) ---
@st.cache_data(ttl=1)
def carregar_tabela_oficial():
  dados_tabela = [
      {
          "nome_time": "Flamengo",
          "pontos": 60,
          "jogos": 28,
          "vitorias": 18,
          "empates": 6,
          "derrotas": 4,
          "gols_pro": 55,
          "gols_contra": 23,
      },
      {
          "nome_time": "Palmeiras",
          "pontos": 57,
          "jogos": 28,
          "vitorias": 16,
          "empates": 9,
          "derrotas": 3,
          "gols_pro": 47,
          "gols_contra": 21,
      },
      {
          "nome_time": "Athletico-PR",
          "pontos": 49,
          "jogos": 28,
          "vitorias": 14,
          "empates": 7,
          "derrotas": 7,
          "gols_pro": 43,
          "gols_contra": 32,
      },
      {
          "nome_time": "Fluminense",
          "pontos": 48,
          "jogos": 28,
          "vitorias": 13,
          "empates": 9,
          "derrotas": 6,
          "gols_pro": 44,
          "gols_contra": 36,
      },
      {
          "nome_time": "Bahia",
          "pontos": 46,
          "jogos": 28,
          "vitorias": 12,
          "empates": 10,
          "derrotas": 6,
          "gols_pro": 43,
          "gols_contra": 35,
      },
      {
          "nome_time": "Cruzeiro",
          "pontos": 45,
          "jogos": 28,
          "vitorias": 13,
          "empates": 6,
          "derrotas": 9,
          "gols_pro": 42,
          "gols_contra": 40,
      },
      {
          "nome_time": "Atlético-MG",
          "pontos": 40,
          "jogos": 27,
          "vitorias": 11,
          "empates": 7,
          "derrotas": 9,
          "gols_pro": 36,
          "gols_contra": 32,
      },
      {
          "nome_time": "Santos",
          "pontos": 38,
          "jogos": 27,
          "vitorias": 10,
          "empates": 8,
          "derrotas": 9,
          "gols_pro": 41,
          "gols_contra": 40,
      },
      {
          "nome_time": "Coritiba",
          "pontos": 38,
          "jogos": 28,
          "vitorias": 10,
          "empates": 8,
          "derrotas": 10,
          "gols_pro": 37,
          "gols_contra": 43,
      },
      {
          "nome_time": "Red Bull Bragantino",
          "pontos": 36,
          "jogos": 27,
          "vitorias": 10,
          "empates": 6,
          "derrotas": 11,
          "gols_pro": 33,
          "gols_contra": 31,
      },
      {
          "nome_time": "São Paulo",
          "pontos": 36,
          "jogos": 27,
          "vitorias": 10,
          "empates": 6,
          "derrotas": 11,
          "gols_pro": 32,
          "gols_contra": 30,
      },
      {
          "nome_time": "Botafogo",
          "pontos": 35,
          "jogos": 28,
          "vitorias": 9,
          "empates": 8,
          "derrotas": 11,
          "gols_pro": 41,
          "gols_contra": 45,
      },
      {
          "nome_time": "Vitória",
          "pontos": 33,
          "jogos": 28,
          "vitorias": 9,
          "empates": 6,
          "derrotas": 13,
          "gols_pro": 28,
          "gols_contra": 42,
      },
      {
          "nome_time": "Corinthians",
          "pontos": 32,
          "jogos": 28,
          "vitorias": 8,
          "empates": 8,
          "derrotas": 12,
          "gols_pro": 29,
          "gols_contra": 32,
      },
      {
          "nome_time": "Mirassol",
          "pontos": 32,
          "jogos": 28,
          "vitorias": 8,
          "empates": 8,
          "derrotas": 12,
          "gols_pro": 33,
          "gols_contra": 42,
      },
      {
          "nome_time": "Vasco",
          "pontos": 31,
          "jogos": 27,
          "vitorias": 8,
          "empates": 7,
          "derrotas": 12,
          "gols_pro": 34,
          "gols_contra": 41,
      },
      {
          "nome_time": "Grêmio",
          "pontos": 29,
          "jogos": 28,
          "vitorias": 7,
          "empates": 8,
          "derrotas": 13,
          "gols_pro": 30,
          "gols_contra": 38,
      },
      {
          "nome_time": "Internacional",
          "pontos": 28,
          "jogos": 28,
          "vitorias": 6,
          "empates": 10,
          "derrotas": 12,
          "gols_pro": 30,
          "gols_contra": 36,
      },
      {
          "nome_time": "Remo",
          "pontos": 23,
          "jogos": 28,
          "vitorias": 5,
          "empates": 8,
          "derrotas": 15,
          "gols_pro": 32,
          "gols_contra": 47,
      },
      {
          "nome_time": "Chapecoense",
          "pontos": 18,
          "jogos": 27,
          "vitorias": 3,
          "empates": 9,
          "derrotas": 15,
          "gols_pro": 29,
          "gols_contra": 53,
      },
  ]
  df = pd.DataFrame(dados_tabela)
  df["saldo_gols"] = df["gols_pro"] - df["gols_contra"]
  df["pos_inicial"] = df.index + 1
  return df


# API ESPN COM SALVAMENTO AUTOMÁTICO DE PARTIDAS ENCERRADAS
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

        # Salva automaticamente se o jogo terminou
        if state == "post":
          st.session_state.jogos_encerrados[chave] = (m_score, v_score)
      return jogos
  except Exception:
    pass
  return {}


# --- CALENDÁRIO COM DATAS E HORÁRIOS CORRIGIDOS (A PARTIR DA RODADA 27) ---
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
        ("Corinthians", "Fluminense", "Domingo, 20/09 - 16:00"),
        ("Vitória", "Cruzeiro", "Domingo, 20/09 - 16:00"),
        ("Red Bull Bragantino", "Flamengo", "Domingo, 20/09 - 18:30"),
        ("Athletico-PR", "Bahia", "Segunda, 21/09 - 20:00"),
    ],
    29: [
        ("Remo", "Grêmio", "Quarta, 07/10 - 19:30"),
        ("Red Bull Bragantino", "Mirassol", "Quarta, 07/10 - 19:30"),
        ("Internacional", "Corinthians", "Quarta, 07/10 - 19:30"),
        ("Vitória", "Chapecoense", "Quarta, 07/10 - 20:00"),
        ("Botafogo", "Vasco", "Quarta, 07/10 - 20:30"),
        ("Cruzeiro", "São Paulo", "Quarta, 07/10 - 21:30"),
        ("Santos", "Flamengo", "Quinta, 08/10 - 19:30"),
        ("Athletico-PR", "Atlético-MG", "Quinta, 08/10 - 20:00"),
        ("Fluminense", "Coritiba", "Quinta, 08/10 - 21:30"),
        ("Palmeiras", "Bahia", "Quinta, 08/10 - 21:30"),
    ],
    30: [
        ("Vasco", "Remo", "Sábado, 10/10 - 17:00"),
        ("São Paulo", "Vitória", "Sábado, 10/10 - 21:00"),
        ("Atlético-MG", "Santos", "Domingo, 11/10 - 16:00"),
        ("Flamengo", "Fluminense", "Domingo, 11/10 - 17:30"),
        ("Palmeiras", "Corinthians", "Domingo, 11/10 - 17:30"),
        ("Grêmio", "Internacional", "Domingo, 11/10 - 17:30"),
        ("Bahia", "Mirassol", "Domingo, 11/10 - 19:30"),
        ("Coritiba", "Botafogo", "Segunda, 12/10 - 16:00"),
        ("Chapecoense", "Athletico-PR", "Segunda, 12/10 - 19:30"),
        ("Red Bull Bragantino", "Cruzeiro", "Segunda, 12/10 - 21:00"),
    ],
    31: [
        ("Fluminense", "Santos", "Sábado, 17/10 - 16:00"),
        ("Botafogo", "Chapecoense", "Sábado, 17/10 - 18:30"),
        ("São Paulo", "Vasco", "Sábado, 17/10 - 21:00"),
        ("Athletico-PR", "Grêmio", "Domingo, 18/10 - 16:00"),
        ("Coritiba", "Palmeiras", "Domingo, 18/10 - 16:00"),
        ("Internacional", "Flamengo", "Domingo, 18/10 - 18:30"),
        ("Bahia", "Cruzeiro", "Domingo, 18/10 - 18:30"),
        ("Vitória", "Atlético-MG", "Segunda, 19/10 - 20:00"),
        ("Red Bull Bragantino", "Remo", "Segunda, 19/10 - 20:00"),
        ("Corinthians", "Mirassol", "Segunda, 19/10 - 21:00"),
    ],
    32: [
        ("Flamengo", "Atlético-MG", "Sábado, 24/10 - 16:00"),
        ("Palmeiras", "Red Bull Bragantino", "Sábado, 24/10 - 18:30"),
        ("Vasco", "Corinthians", "Sábado, 24/10 - 21:00"),
        ("Santos", "Bahia", "Domingo, 25/10 - 16:00"),
        ("Grêmio", "São Paulo", "Domingo, 25/10 - 16:00"),
        ("Cruzeiro", "Coritiba", "Domingo, 25/10 - 18:30"),
        ("Mirassol", "Botafogo", "Domingo, 25/10 - 18:30"),
        ("Chapecoense", "Fluminense", "Segunda, 26/10 - 20:00"),
        ("Remo", "Vitória", "Segunda, 26/10 - 20:00"),
        ("Athletico-PR", "Internacional", "Segunda, 26/10 - 21:00"),
    ],
    33: [
        ("Fluminense", "Internacional", "Quarta, 28/10 - 19:30"),
        ("Vasco", "Flamengo", "Quarta, 28/10 - 20:00"),
        ("Santos", "Palmeiras", "Quarta, 28/10 - 21:30"),
        ("Botafogo", "Coritiba", "Quinta, 29/10 - 19:30"),
        ("São Paulo", "Mirassol", "Quinta, 29/10 - 20:00"),
        ("Corinthians", "Cruzeiro", "Quinta, 29/10 - 20:30"),
        ("Atlético-MG", "Grêmio", "Quinta, 29/10 - 21:00"),
        ("Bahia", "Chapecoense", "Quinta, 29/10 - 21:30"),
        ("Red Bull Bragantino", "Vitória", "Quinta, 29/10 - 21:30"),
        ("Athletico-PR", "Remo", "Quinta, 29/10 - 21:30"),
    ],
    34: [
        ("Flamengo", "Grêmio", "Quarta, 04/11 - 19:30"),
        ("Botafogo", "Atlético-MG", "Quarta, 04/11 - 20:00"),
        ("São Paulo", "Corinthians", "Quarta, 04/11 - 21:30"),
        ("Palmeiras", "Internacional", "Quinta, 05/11 - 19:30"),
        ("Fluminense", "Cruzeiro", "Quinta, 05/11 - 20:00"),
        ("Santos", "Vasco", "Quinta, 05/11 - 20:30"),
        ("Bahia", "Coritiba", "Quinta, 05/11 - 21:00"),
        ("Red Bull Bragantino", "Chapecoense", "Quinta, 05/11 - 21:30"),
        ("Mirassol", "Remo", "Quinta, 05/11 - 21:30"),
        ("Vitória", "Athletico-PR", "Quinta, 05/11 - 21:30"),
    ],
    35: [
        ("Fluminense", "São Paulo", "Quarta, 18/11 - 19:30"),
        ("Vasco", "Internacional", "Quarta, 18/11 - 20:00"),
        ("Flamengo", "Athletico-PR", "Quarta, 18/11 - 21:30"),
        ("Palmeiras", "Remo", "Quinta, 19/11 - 19:30"),
        ("Botafogo", "Bahia", "Quinta, 19/11 - 20:00"),
        ("Corinthians", "Santos", "Quinta, 19/11 - 20:30"),
        ("Cruzeiro", "Chapecoense", "Quinta, 19/11 - 21:00"),
        ("Red Bull Bragantino", "Atlético-MG", "Quinta, 19/11 - 21:30"),
        ("Mirassol", "Grêmio", "Quinta, 19/11 - 21:30"),
        ("Coritiba", "Vitória", "Quinta, 19/11 - 21:30"),
    ],
    36: [
        ("Fluminense", "Mirassol", "Sábado, 21/11 - 16:00"),
        ("Botafogo", "São Paulo", "Sábado, 21/11 - 18:30"),
        ("Santos", "Grêmio", "Sábado, 21/11 - 21:00"),
        ("Flamengo", "Remo", "Domingo, 22/11 - 16:00"),
        ("Palmeiras", "Vitória", "Domingo, 22/11 - 16:00"),
        ("Vasco", "Atlético-MG", "Domingo, 22/11 - 18:30"),
        ("Corinthians", "Red Bull Bragantino", "Domingo, 22/11 - 18:30"),
        ("Cruzeiro", "Internacional", "Segunda, 23/11 - 20:00"),
        ("Bahia", "Athletico-PR", "Segunda, 23/11 - 20:00"),
        ("Coritiba", "Chapecoense", "Segunda, 23/11 - 21:00"),
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

# --- PLACARES REAIS OFICIAIS DAS RODADAS 27 E 28 ---
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

PLACARES_RODADA_28_REAIS = {
    ("Atlético-MG", "Chapecoense"): (1, 1),
    ("Mirassol", "Botafogo"): (2, 0),
    ("Remo", "Santos"): (0, 1),
    ("Vasco", "Coritiba"): (5, 0),
    ("São Paulo", "Internacional"): (2, 1),
    ("Grêmio", "Palmeiras"): (0, 1),
    ("Corinthians", "Fluminense"): (1, 3),
    ("Vitória", "Cruzeiro"): (0, 3),
    ("Red Bull Bragantino", "Flamengo"): (1, 2),
    ("Athletico-PR", "Bahia"): (2, 1),
}

# Carrega rodadas 27 e 28 no session_state de forma permanente
for (m, v), (gm, gv) in PLACARES_RODADA_27_REAIS.items():
  st.session_state.jogos_encerrados[f"{m}X{v}"] = (gm, gv)

for (m, v), (gm, gv) in PLACARES_RODADA_28_REAIS.items():
  st.session_state.jogos_encerrados[f"{m}X{v}"] = (gm, gv)

placar_live = buscar_jogos_espn()

# CONTROLES SUPERIORES
c_ctrl1, c_ctrl2 = st.columns([1, 2])
with c_ctrl1:
  rodadas_disponiveis = sorted(list(CALENDARIO_RODADAS.keys()))
  default_idx = (
      rodadas_disponiveis.index(29) if 29 in rodadas_disponiveis else 0
  )
  num_rodada = st.selectbox(
      "Rodada:", rodadas_disponiveis, index=default_idx
  )
with c_ctrl2:
  df_base = carregar_tabela_oficial()
  lista_times = ["Nenhum"] + sorted(df_base["nome_time"].unique().tolist())
  time_favorito = st.selectbox("⭐ Destaque o Time do Coração:", lista_times)

# --- CÁLCULO REATIVO DA TABELA (Acumulando AO VIVO + ENCERRADOS + SIMULADOR) ---
df_simulado = df_base.copy()

for r_num, lista_jogos in CALENDARIO_RODADAS.items():
  if r_num >= 29:
    for idx, (mandante, visitante, _) in enumerate(lista_jogos):
      chave_live = f"{mandante}X{visitante}"
      chave_sim = f"sim_r{r_num}_{idx}"

      jogou = False
      gm, gv = 0, 0

      # Prioridade 1: Jogo Encerrado salvo automaticamente
      if chave_live in st.session_state.jogos_encerrados:
        gm, gv = st.session_state.jogos_encerrados[chave_live]
        jogou = True
      # Prioridade 2: Jogo Acontecendo Ao Vivo na API da ESPN (Reflete na tabela em tempo real!)
      elif chave_live in placar_live and placar_live[chave_live]["state"] in [
          "in",
          "post",
      ]:
        gm = placar_live[chave_live]["gm"]
        gv = placar_live[chave_live]["gv"]
        jogou = True
      # Prioridade 3: Palpites manuais feitos no Simulador
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
    if num_rodada >= 29:
      if st.button("🧮 Calcular Todos os Palpites"):
        for idx in range(len(confrontos_rodada_atual)):
          key_m = f"input_r{num_rodada}_m_{idx}"
          key_v = f"input_r{num_rodada}_v_{idx}"
          if key_m in st.session_state and key_v in st.session_state:
            gm = st.session_state[key_m]
            gv = st.session_state[key_v]
            if gm is not None and gv is not None:
              st.session_state.palpites_confirmados[
                  f"sim_r{num_rodada}_{idx}"
              ] = (gm, gv)
        st.rerun()

  with col_btn2:
    if num_rodada >= 29:
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

    if num_rodada in [27, 28]:
      jogo_bloqueado = True
      if num_rodada == 27:
        val_m, val_v = PLACARES_RODADA_27_REAIS.get(
            (mandante, visitante), (0, 0)
        )
      elif num_rodada == 28:
        val_m, val_v = PLACARES_RODADA_28_REAIS.get(
            (mandante, visitante), (0, 0)
        )
    else:
      if chave_live in st.session_state.jogos_encerrados:
        val_m, val_v = st.session_state.jogos_encerrados[chave_live]
        jogo_bloqueado = True
      elif chave_live in placar_live and placar_live[chave_live]["state"] in [
          "in",
          "post",
      ]:
        val_m = placar_live[chave_live]["gm"]
        val_v = placar_live[chave_live]["gv"]
        if placar_live[chave_live]["state"] == "post":
          jogo_bloqueado = True
      elif chave_sim in st.session_state.palpites_confirmados:
        val_m, val_v = st.session_state.palpites_confirmados[chave_sim]

    col_m, col_img_m, col_txt, col_img_v, col_v, col_calc = st.columns(
        [1.1, 0.5, 2.0, 0.5, 1.1, 0.8]
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
    with col_calc:
      if not jogo_bloqueado:
        if st.button("Salvar", key=f"btn_calc_{num_rodada}_{idx}"):
          st.session_state.palpites_confirmados[chave_sim] = (val_m, val_v)
          st.rerun()
      else:
        st.markdown(
            "<div style='text-align:center; font-size:12px; color:gray;'>"
            "Encerrado</div>",
            unsafe_allow_html=True,
        )

    st.markdown("---")

# ABA 3: AO VIVO / PLACARES DA RODADA SELECIONADA
with tab_aovivo:
  st.subheader(f"🔴 Placar / Jogos da {num_rodada}ª Rodada")


  @st.fragment(run_every=30)
  def renderizar_ao_vivo():
    confrontos = CALENDARIO_RODADAS.get(num_rodada, [])
    placar_live_atual = buscar_jogos_espn()

    if num_rodada == 27:
      st.success("Resultados oficiais da **Rodada 27** encerrada:")
      for mandante, visitante, data_hora_str in confrontos:
        gm, gv = PLACARES_RODADA_27_REAIS.get((mandante, visitante), (0, 0))
        col_img_m, col_txt, col_img_v = st.columns([0.6, 3.8, 0.6])
        with col_img_m:
          st.image(obter_escudo(mandante), width=28)
        with col_txt:
          st.markdown(
              f"<div style='text-align: center;'><b>{mandante}</b>"
              f" &nbsp;&nbsp;<span style='font-size: 1.1em; color:"
              f" #d9534f;'><b>{gm} x {gv}</b></span>&nbsp;&nbsp;"
              f" <b>{visitante}</b><br><span style='font-size: 0.85em; color:"
              f" #666;'>{data_hora_str} (Encerrado)</span></div>",
              unsafe_allow_html=True,
          )
        with col_img_v:
          st.image(obter_escudo(visitante), width=28)
        st.markdown("---")
    elif num_rodada == 28:
      st.success("Resultados oficiais da **Rodada 28** encerrada:")
      for mandante, visitante, data_hora_str in confrontos:
        gm, gv = PLACARES_RODADA_28_REAIS.get((mandante, visitante), (0, 0))
        col_img_m, col_txt, col_img_v = st.columns([0.6, 3.8, 0.6])
        with col_img_m:
          st.image(obter_escudo(mandante), width=28)
        with col_txt:
          st.markdown(
              f"<div style='text-align: center;'><b>{mandante}</b>"
              f" &nbsp;&nbsp;<span style='font-size: 1.1em; color:"
              f" #d9534f;'><b>{gm} x {gv}</b></span>&nbsp;&nbsp;"
              f" <b>{visitante}</b><br><span style='font-size: 0.85em; color:"
              f" #666;'>{data_hora_str} (Encerrado)</span></div>",
              unsafe_allow_html=True,
          )
        with col_img_v:
          st.image(obter_escudo(visitante), width=28)
        st.markdown("---")
    else:
      st.caption(
          "🔄 Atualizando placares e status de jogos ao vivo via API da"
          " ESPN..."
      )
      for mandante, visitante, data_hora_str in confrontos:
        chave = f"{mandante}X{visitante}"
        col_img_m, col_txt, col_img_v = st.columns([0.6, 3.8, 0.6])

        if chave in placar_live_atual:
          info = placar_live_atual[chave]
          with col_img_m:
            st.image(obter_escudo(mandante), width=28)
          with col_txt:
            st.markdown(
                f"<div style='text-align: center;'><b>{mandante}</b>"
                f" &nbsp;&nbsp;<span style='font-size: 1.1em; color:"
                f" #d9534f;'><b>{info['gm']} x"
                f" {info['gv']}</b></span>&nbsp;&nbsp; <b>{visitante}</b><br><span"
                f" style='font-size: 0.85em; color: #666;'>Status:"
                f" {info['detail']}</span></div>",
                unsafe_allow_html=True,
            )
          with col_img_v:
            st.image(obter_escudo(visitante), width=28)
        elif chave in st.session_state.jogos_encerrados:
          gm, gv = st.session_state.jogos_encerrados[chave]
          with col_img_m:
            st.image(obter_escudo(mandante), width=28)
          with col_txt:
            st.markdown(
                f"<div style='text-align: center;'><b>{mandante}</b>"
                f" &nbsp;&nbsp;<span style='font-size: 1.1em; color:"
                f" #d9534f;'><b>{gm} x {gv}</b></span>&nbsp;&nbsp;"
                f" <b>{visitante}</b><br><span style='font-size: 0.85em; color:"
                f" #666;'>Encerrado</span></div>",
                unsafe_allow_html=True,
            )
          with col_img_v:
            st.image(obter_escudo(visitante), width=28)
        else:
          with col_img_m:
            st.image(obter_escudo(mandante), width=28)
          with col_txt:
            st.markdown(
                f"<div style='text-align: center;'><b>{mandante} x"
                f" {visitante}</b><br><span style='font-size: 0.85em; color:"
                f" #666;'>{data_hora_str}</span></div>",
                unsafe_allow_html=True,
            )
          with col_img_v:
            st.image(obter_escudo(visitante), width=28)
        st.markdown("---")


  renderizar_ao_vivo()
