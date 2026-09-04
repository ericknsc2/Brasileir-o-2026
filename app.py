import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="Brasileirão 2026", layout="wide")

# Título da Aplicação
st.title("⚽ Brasileirão 2026")

# --- BUSCA AUTOMÁTICA DE RESULTADOS REAIS ---
@st.cache_data(ttl=3600)
def buscar_dados_br_oficial():
    try:
        # Lê o arquivo CSV diretamente do diretório local do projeto
        df = pd.read_csv("Brasileirao_SQL.csv")
        return df
    except Exception as e:
        st.error(f"Erro ao carregar os dados do CSV local: {e}")
        return pd.DataFrame()
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
# Criação das duas colunas com nomes personalizados
col_tabela, col_simulador = st.columns([1.2, 1])

# Bloco da tabela
with col_tabela:
    st.subheader("Tabela de Classificação")
    st.dataframe(
        df_tabela.style.apply(colorir_zonas, axis=0),
        use_container_width=True,
        hide_index=True
    )

# Bloco do simulador de jogos (linha 43)
with col_simulador:
    st.subheader("Simulador de Jogos")
    # ... código das partidas ...

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
    # Função para definir a cor de fundo de cada linha conforme a posição
def colorir_zonas(val):
    # Dicionário de cores hexadecimais para as zonas
    cores = []
    for i in range(len(val)):
        posicao = i + 1
        if posicao <= 6:
            cores.append('background-color: #d4edda; color: #155724;')  # Verde (Libertadores)
        elif 7 <= posicao <= 12:
            cores.append('background-color: #fff3cd; color: #856404;')  # Amarelo/Dourado (Sul-Americana)
        elif 17 <= posicao <= 20:
            cores.append('background-color: #f8d7da; color: #721c24;')  # Vermelho (Z-4)
        else:
            cores.append('')  # Neutro (Zona Intermediária)
    return cores

# Aplica a estilização na tabela e exibe no Streamlit
# (Certifique-se de substituir 'df_tabela' pelo nome da sua variável da tabela)
st.dataframe(
    df_tabela.style.apply(colorir_zonas, axis=0),
    use_container_width=True,
    hide_index=True
)
st.markdown("""
**Legenda:** 
🟢 **1º ao 6º:** CONMEBOL Libertadores | 
🟡 **7º ao 12º:** CONMEBOL Sul-Americana | 
🔴 **17º ao 20º:** Zona de Rebaixamento (Z-4)
""")
