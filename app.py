import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="Brasileirão 2026", layout="wide")

# Título da Aplicação
st.title("⚽ Brasileirão 2026")

# --- BUSCA AUTOMÁTICA DE RESULTADOS REAIS ---
@st.cache_data(ttl=3600)  # Atualiza a cada 1 hora
def buscar_dados_br_oficial():
    """
    Função de fallback/scraping para obter os dados atualizados da tabela
    diretamente do ambiente web caso o CSV não esteja atualizado.
    """
    url = "https://raw.githubusercontent.com/ericknsc2/Brasileiro-o-2026/main/Brasileirao%20SQL.csv"
    try:
        df = pd.read_csv(url)
        return df
    except Exception:
        # Tabela padrão de contingência
        return pd.DataFrame([
            {"nome_time": "Palmeiras", "pontos": 52, "jogos": 25, "vitorias": 15, "empates": 7, "derrotas": 3, "gols_pro": 45, "gols_contra": 21, "saldo_gols": 24},
            {"nome_time": "Flamengo", "pontos": 51, "jogos": 25, "vitorias": 15, "empates": 6, "derrotas": 4, "gols_pro": 50, "gols_contra": 21, "saldo_gols": 29},
            {"nome_time": "Athletico-PR", "pontos": 45, "jogos": 25, "vitorias": 13, "empates": 6, "derrotas": 6, "gols_pro": 37, "gols_contra": 25, "saldo_gols": 12},
            {"nome_time": "Fluminense", "pontos": 42, "jogos": 25, "vitorias": 11, "empates": 9, "derrotas": 5, "gols_pro": 39, "gols_contra": 32, "saldo_gols": 7},
            {"nome_time": "Bahia", "pontos": 40, "jogos": 25, "vitorias": 10, "empates": 10, "derrotas": 5, "gols_pro": 37, "gols_contra": 30, "saldo_gols": 7},
            {"nome_time": "Cruzeiro", "pontos": 39, "jogos": 25, "vitorias": 11, "empates": 6, "derrotas": 8, "gols_pro": 35, "gols_contra": 36, "saldo_gols": -1},
            {"nome_time": "Coritiba", "pontos": 37, "jogos": 25, "vitorias": 10, "empates": 7, "derrotas": 8, "gols_pro": 33, "gols_contra": 33, "saldo_gols": 0},
            {"nome_time": "Atlético-MG", "pontos": 36, "jogos": 24, "vitorias": 10, "empates": 6, "derrotas": 8, "gols_pro": 32, "gols_contra": 28, "saldo_gols": 4},
            {"nome_time": "Red Bull Bragantino", "pontos": 35, "jogos": 24, "vitorias": 10, "empates": 5, "derrotas": 9, "gols_pro": 29, "gols_contra": 25, "saldo_gols": 4},
            {"nome_time": "São Paulo", "pontos": 35, "jogos": 25, "vitorias": 10, "empates": 5, "derrotas": 10, "gols_pro": 31, "gols_contra": 30, "saldo_gols": 1},
            {"nome_time": "Botafogo", "pontos": 34, "jogos": 25, "vitorias": 9, "empates": 7, "derrotas": 9, "gols_pro": 30, "gols_contra": 31, "saldo_gols": -1},
            {"nome_time": "Internacional", "pontos": 33, "jogos": 25, "vitorias": 9, "empates": 6, "derrotas": 10, "gols_pro": 29, "gols_contra": 32, "saldo_gols": -3},
            {"nome_time": "Vasco", "pontos": 32, "jogos": 25, "vitorias": 8, "empates": 8, "derrotas": 9, "gols_pro": 28, "gols_contra": 33, "saldo_gols": -5},
            {"nome_time": "Santos", "pontos": 31, "jogos": 25, "vitorias": 8, "empates": 7, "derrotas": 10, "gols_pro": 26, "gols_contra": 30, "saldo_gols": -4},
            {"nome_time": "Grêmio", "pontos": 29, "jogos": 25, "vitorias": 8, "empates": 5, "derrotas": 12, "gols_pro": 25, "gols_contra": 35, "saldo_gols": -10},
            {"nome_time": "Corinthians", "pontos": 28, "jogos": 25, "vitorias": 7, "empates": 7, "derrotas": 11, "gols_pro": 24, "gols_contra": 33, "saldo_gols": -9},
            {"nome_time": "Mirassol", "pontos": 26, "jogos": 25, "vitorias": 6, "empates": 8, "derrotas": 11, "gols_pro": 22, "gols_contra": 35, "saldo_gols": -13},
            {"nome_time": "Vitória", "pontos": 24, "jogos": 25, "vitorias": 6, "empates": 6, "derrotas": 13, "gols_pro": 21, "gols_contra": 38, "saldo_gols": -17},
            {"nome_time": "Remo", "pontos": 22, "jogos": 25, "vitorias": 5, "empates": 7, "derrotas": 13, "gols_pro": 20, "gols_contra": 40, "saldo_gols": -20},
            {"nome_time": "Chapecoense", "pontos": 19, "jogos": 25, "vitorias": 4, "empates": 7, "derrotas": 14, "gols_pro": 18, "gols_contra": 42, "saldo_gols": -24}
        ])

# Jogos Fixos das Rodadas Restantes
RODADAS = {
    26: [("Red Bull Bragantino", "Bahia"), ("São Paulo", "Atlético-MG"), ("Fluminense", "Vasco"), ("Coritiba", "Mirassol"), ("Cruzeiro", "Athletico-PR"), ("Remo", "Flamengo"), ("Internacional", "Santos"), ("Botafogo", "Palmeiras"), ("Corinthians", "Chapecoense"), ("Vitória", "Grêmio")],
    27: [("Coritiba", "Athletico-PR"), ("Atlético-MG", "Fluminense"), ("Grêmio", "Vasco"), ("Chapecoense", "Internacional"), ("Palmeiras", "São Paulo"), ("Botafogo", "Red Bull Bragantino"), ("Santos", "Cruzeiro"), ("Mirassol", "Vitória"), ("Flamengo", "Corinthians"), ("Bahia", "Remo")],
    28: [("Atlético-MG", "Chapecoense"), ("Mirassol", "Botafogo"), ("Remo", "Santos"), ("Vasco", "Coritiba"), ("São Paulo", "Internacional"), ("Grêmio", "Palmeiras"), ("Corinthians", "Fluminense"), ("Vitória", "Cruzeiro"), ("Flamengo", "Red Bull Bragantino"), ("Athletico-PR", "Bahia")],
    29: [("Red Bull Bragantino", "Mirassol"), ("Internacional", "Corinthians"), ("Remo", "Grêmio"), ("Vitória", "Chapecoense"), ("Botafogo", "Vasco"), ("Cruzeiro", "São Paulo"), ("Santos", "Flamengo"), ("Athletico-PR", "Atlético-MG"), ("Fluminense", "Coritiba"), ("Palmeiras", "Bahia")],
    30: [("Vasco", "Remo"), ("São Paulo", "Vitória"), ("Atlético-MG", "Santos"), ("Flamengo", "Fluminense"), ("Palmeiras", "Corinthians"), ("Grêmio", "Internacional"), ("Coritiba", "Botafogo"), ("Bahia", "Mirassol"), ("Chapecoense", "Athletico-PR"), ("Red Bull Bragantino", "Cruzeiro")],
    31: [("Santos", "Coritiba"), ("Fluminense", "Botafogo"), ("Flamengo", "Palmeiras"), ("Vasco", "Red Bull Bragantino"), ("Internacional", "Vitória"), ("Bahia", "Atlético-MG"), ("Cruzeiro", "Chapecoense"), ("Athletico-PR", "Remo"), ("Corinthians", "São Paulo"), ("Mirassol", "Grêmio")],
    32: [("Botafogo", "Santos"), ("Palmeiras", "Mirassol"), ("São Paulo", "Bahia"), ("Atlético-MG", "Corinthians"), ("Grêmio", "Flamengo"), ("Red Bull Bragantino", "Fluminense"), ("Coritiba", "Cruzeiro"), ("Vitória", "Athletico-PR"), ("Remo", "Internacional"), ("Chapecoense", "Vasco")],
    33: [("Flamengo", "Botafogo"), ("Santos", "Palmeiras"), ("Vasco", "São Paulo"), ("Fluminense", "Chapecoense"), ("Internacional", "Atlético-MG"), ("Bahia", "Grêmio"), ("Cruzeiro", "Red Bull Bragantino"), ("Athletico-PR", "Coritiba"), ("Corinthians", "Vitória"), ("Mirassol", "Remo")],
    34: [("Palmeiras", "Fluminense"), ("São Paulo", "Flamengo"), ("Atlético-MG", "Vasco"), ("Botafogo", "Internacional"), ("Grêmio", "Santos"), ("Red Bull Bragantino", "Athletico-PR"), ("Coritiba", "Bahia"), ("Vitória", "Mirassol"), ("Remo", "Corinthians"), ("Chapecoense", "Cruzeiro")],
    35: [("Flamengo", "Atlético-MG"), ("Vasco", "Palmeiras"), ("Fluminense", "São Paulo"), ("Santos", "Red Bull Bragantino"), ("Internacional", "Grêmio"), ("Bahia", "Botafogo"), ("Cruzeiro", "Vitória"), ("Athletico-PR", "Chapecoense"), ("Corinthians", "Coritiba"), ("Mirassol", "Remo")],
    36: [("Palmeiras", "Flamengo"), ("São Paulo", "Santos"), ("Atlético-MG", "Botafogo"), ("Botafogo", "Fluminense"), ("Grêmio", "Athletico-PR"), ("Red Bull Bragantino", "Internacional"), ("Coritiba", "Vasco"), ("Vitória", "Bahia"), ("Remo", "Cruzeiro"), ("Chapecoense", "Corinthians")],
    37: [("Flamengo", "Santos"), ("Vasco", "Botafogo"), ("Fluminense", "Grêmio"), ("Internacional", "Palmeiras"), ("Bahia", "São Paulo"), ("Cruzeiro", "Atlético-MG"), ("Athletico-PR", "Red Bull Bragantino"), ("Corinthians", "Mirassol"), ("Vitória", "Coritiba"), ("Chapecoense", "Remo")],
    38: [("Flamengo", "Chapecoense"), ("Vasco", "Vitória"), ("Santos", "Botafogo"), ("Palmeiras", "Coritiba"), ("Red Bull Bragantino", "Fluminense"), ("Cruzeiro", "Bahia"), ("São Paulo", "Athletico-PR"), ("Atlético-MG", "Mirassol"), ("Grêmio", "Remo"), ("Internacional", "Corinthians")]
}

# Organização visual em Colunas
col_tabela, col_simulador = st.columns([1.3, 1])

# --- COLUNA DA DIREITA: SIMULADOR ---
with col_simulador:
    st.subheader("🎮 Simulador de Jogos")
    num_rodada = st.selectbox("Selecione a Rodada:", list(range(26, 39)))
    
    st.write(f"**Confrontos da {num_rodada}ª Rodada:**")
    jogos = RODADAS[num_rodada]
    
    placares_rodada = []
    
    for idx, (mandante, visitante) in enumerate(jogos):
        c1, c2, c3, c4, c5 = st.columns([2.5, 1, 0.3, 1, 2.5])
        with c1:
            st.markdown(f"<div style='text-align: right;'><b>{mandante}</b></div>", unsafe_allow_html=True)
        with c2:
            gm = st.number_input("", min_value=0, value=0, key=f"r{num_rodada}_m_{idx}", label_visibility="collapsed")
        with c3:
            st.write("x")
        with c4:
            gv = st.number_input("", min_value=0, value=0, key=f"r{num_rodada}_v_{idx}", label_visibility="collapsed")
        with c5:
            st.markdown(f"<b>{visitante}</b>", unsafe_allow_html=True)
            
        placares_rodada.append((mandante, gm, gv, visitante))

# --- CÁLCULO E ATUALIZAÇÃO DA TABELA ---
df_tabela = buscar_dados_br_oficial().copy()

for mandante, gm, gv, visitante in placares_rodada:
    if mandante in df_tabela['nome_time'].values and visitante in df_tabela['nome_time'].values:
        idx_m = df_tabela[df_tabela['nome_time'] == mandante].index[0]
        idx_v = df_tabela[df_tabela['nome_time'] == visitante].index[0]
        
        if gm > 0 or gv > 0:
            df_tabela.at[idx_m, 'jogos'] += 1
            df_tabela.at[idx_v, 'jogos'] += 1
            
            df_tabela.at[idx_m, 'gols_pro'] += gm
            df_tabela.at[idx_m, 'gols_contra'] += gv
            df_tabela.at[idx_v, 'gols_pro'] += gv
            df_tabela.at[idx_v, 'gols_contra'] += gm
            
            if gm > gv:
                df_tabela.at[idx_m, 'pontos'] += 3
                df_tabela.at[idx_m, 'vitorias'] += 1
                df_tabela.at[idx_v, 'derrotas'] += 1
            elif gv > gm:
                df_tabela.at[idx_v, 'pontos'] += 3
                df_tabela.at[idx_v, 'vitorias'] += 1
                df_tabela.at[idx_m, 'derrotas'] += 1
            else:
                df_tabela.at[idx_m, 'pontos'] += 1
                df_tabela.at[idx_v, 'pontos'] += 1
                df_tabela.at[idx_m, 'empates'] += 1
                df_tabela.at[idx_v, 'empates'] += 1

df_tabela['saldo_gols'] = df_tabela['gols_pro'] - df_tabela['gols_contra']

# Ordenar por Pontos > Vitórias > Saldo de Gols > Gols Pró
df_tabela = df_tabela.sort_values(by=["pontos", "vitorias", "saldo_gols", "gols_pro"], ascending=False).reset_index(drop=True)
df_tabela.index = df_tabela.index + 1

# --- COLUNA DA ESQUERDA: TABELA COMPLETA ---
with col_tabela:
    st.subheader("📊 Classificação Atualizada")
    st.dataframe(
        df_tabela[["nome_time", "pontos", "jogos", "vitorias", "empates", "derrotas", "gols_pro", "gols_contra", "saldo_gols"]], 
        height=730, 
        use_container_width=True
    )