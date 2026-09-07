import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# Tenta importar o st_autorefresh para atualização em tempo real (2 segundos)
try:
    from streamlit_autorefresh import st_autorefresh
    # Atualiza a página a cada 2000 ms (2 segundos)
    st_autorefresh(interval=2000, key="autoupdate_brasileirao")
except ImportError:
    pass

# Configuração da página - Layout Wide
st.set_page_config(page_title="Brasileirão 2026", layout="wide", initial_sidebar_state="collapsed")

# --- CSS RESPONSIVO HÍBRIDO E OTIMIZAÇÃO DE ESPAÇO ---
st.markdown("""
<style>
    /* Subir todo o conteúdo da página para aproveitar o topo */
    .block-container {
        padding-top: 0.8rem !important;
        padding-bottom: 0rem !important;
    }

    /* DESKTOP (Telas maiores que 768px):
       Oculta o cabeçalho das abas e posiciona Tabela e Simulador em 2 colunas lado a lado */
    @media (min-width: 769px) {
        div[data-testid="stTabs"] > div:first-child {
            display: none !important;
        }
        div[data-testid="stTabs"] {
            display: flex !important;
            flex-direction: row !important;
            gap: 24px !important;
        }
        div[data-testid="stTabContent"] {
            width: 50% !important;
            display: block !important;
        }
    }

    /* MOBILE (Telas até 768px):
       Mantém as 2 abas nativas no topo e ajusta as margens internas */
    @media (max-width: 768px) {
        .block-container {
            padding-left: 0.5rem !important;
            padding-right: 0.5rem !important;
        }
        .stNumberInput input {
            text-align: center;
            font-size: 16px !important;
            font-weight: bold;
        }
    }

    .time-nome-m { text-align: right; font-weight: bold; font-size: 14px; }
    .time-nome-v { text-align: left; font-weight: bold; font-size: 14px; }
    .status-badge { font-size: 12px; color: #666; margin-bottom: 2px; }
</style>
""", unsafe_allow_html=True)

st.title("⚽ Brasileirão 2026")

# --- 1. TABELA BASE OFICIAL CONSOLIDADA (PÓS 26ª RODADA) ---
@st.cache_data(ttl=10)
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
        {"nome_time": "Corinthians", "pontos": 32, "jogos": 26, "vitorias": 8, "empates": 8, "derrotas": 10, "gols_pro": 27, "gols_contra": 27},
        {"nome_time": "Santos", "pontos": 32, "jogos": 25, "vitorias": 8, "empates": 8, "derrotas": 9, "gols_pro": 37, "gols_contra": 38},
        {"nome_time": "Botafogo", "pontos": 31, "jogos": 25, "vitorias": 8, "empates": 7, "derrotas": 10, "gols_pro": 37, "gols_contra": 40},
        {"nome_time": "Vitória", "pontos": 29, "jogos": 25, "vitorias": 8, "empates": 5, "derrotas": 12, "gols_pro": 24, "gols_contra": 37},
        {"nome_time": "Grêmio", "pontos": 28, "jogos": 24, "vitorias": 7, "empates": 7, "derrotas": 10, "gols_pro": 27, "gols_contra": 32},
        {"nome_time": "Mirassol", "pontos": 28, "jogos": 26, "vitorias": 7, "empates": 7, "derrotas": 12, "gols_pro": 29, "gols_contra": 40},
        {"nome_time": "Vasco", "pontos": 25, "jogos": 25, "vitorias": 6, "empates": 7, "derrotas": 12, "gols_pro": 27, "gols_contra": 40},
        {"nome_time": "Internacional", "pontos": 25, "jogos": 26, "vitorias": 5, "empates": 10, "derrotas": 11, "gols_pro": 28, "gols_contra": 34},
        {"nome_time": "Remo", "pontos": 23, "jogos": 26, "vitorias": 5, "empates": 8, "derrotas": 13, "gols_pro": 30, "gols_contra": 43},
        {"nome_time": "Chapecoense", "pontos": 17, "jogos": 25, "vitorias": 3, "empates": 8, "derrotas": 14, "gols_pro": 27, "gols_contra": 50}
    ]
    df = pd.DataFrame(dados_tabela)
    df['saldo_gols'] = df['gols_pro'] - df['gols_contra']
    return df

# --- 2. CONSULTA DE PLACARES AO VIVO EM TEMPO REAL (API PÚBLICA ESPN) ---
def buscar_jogos_ao_vivo():
    url = "https://site.api.espn.com/apis/site/v2/sports/soccer/bra.1/scoreboard"
    try:
        res = requests.get(url, timeout=2)
        if res.status_code == 200:
            dados = res.json()
            eventos = dados.get('events', [])
            jogos_ao_vivo = {}
            for ev in eventos:
                comp = ev['competitions'][0]
                m_nome = comp['competitors'][0]['team']['shortDisplayName']
                v_nome = comp['competitors'][1]['team']['shortDisplayName']
                m_score = int(comp['competitors'][0]['score'])
                v_score = int(comp['competitors'][1]['score'])
                status_state = ev['status']['type']['state'] # 'in', 'post', 'pre'
                status_detail = ev['status']['type']['shortDetail']
                
                chave = f"{m_nome}x{v_nome}"
                jogos_ao_vivo[chave] = {
                    'gm': m_score,
                    'gv': v_score,
                    'state': status_state,
                    'detail': status_detail
                }
            return jogos_ao_vivo
    except Exception:
        pass
    return {}

# --- CONFRONTOS OFICIAIS DA 27ª RODADA ---
CONFRONTOS_27 = [
    ("Coritiba", "Athletico-PR", "Sexta, 11/09 - 21:00"),
    ("Atlético-MG", "Fluminense", "Sábado, 12/09 - 16:00"),
    ("Grêmio", "Vasco", "Sábado, 12/09 - 16:00"),
    ("Chapecoense", "Internacional", "Sábado, 12/09 - 17:00"),
    ("Palmeiras", "São Paulo", "Sábado, 12/09 - 18:30"),
    ("Botafogo", "Red Bull Bragantino", "Sábado, 12/09 - 20:30"),
    ("Santos", "Cruzeiro", "Sábado, 12/09 - 21:00"),
    ("Mirassol", "Vitória", "Domingo, 13/09 - 16:00"),
    ("Flamengo", "Corinthians", "Domingo, 13/09 - 17:30"),
    ("Bahia", "Remo", "Segunda, 14/09 - 20:00")
]

df_base = carregar_tabela_oficial()
placar_live = buscar_jogos_ao_vivo()

# CONTROLES SUPERIORES
c1, c2 = st.columns([1, 2])
with c1:
    num_rodada = st.selectbox("Rodada:", [27], index=0)
with c2:
    lista_times = ["Nenhum"] + sorted(df_base['nome_time'].unique().tolist()) if not df_base.empty else ["Nenhum"]
    time_favorito = st.selectbox("⭐ Time do Coração:", lista_times)

# --- 3. RECALCULO REATIVO DA TABELA COM OS PALPITES E DADOS AO VIVO ---
df_tabela = df_base.copy()

if not df_tabela.empty:
    for idx, jogo in enumerate(CONFRONTOS_27):
        mandante, visitante, data_hora_str = jogo
        
        key_m = f"r{num_rodada}_m_{idx}"
        key_v = f"r{num_rodada}_v_{idx}"
        
        chave_live = f"{mandante}x{visitante}"
        
        # Se o jogo estiver ao vivo na API da ESPN, sobrescreve com o placar oficial em tempo real
        if chave_live in placar_live and placar_live[chave_live]['state'] in ['in', 'post']:
            gm = placar_live[chave_live]['gm']
            gv = placar_live[chave_live]['gv']
            computar = True
        elif key_m in st.session_state and key_v in st.session_state:
            gm = st.session_state[key_m]
            gv = st.session_state[key_v]
            computar = True
        else:
            computar = False

        if computar and (mandante in df_tabela['nome_time'].values) and (visitante in df_tabela['nome_time'].values):
            idx_m = df_tabela[df_tabela['nome_time'] == mandante].index[0]
            idx_v = df_tabela[df_tabela['nome_time'] == visitante].index[0]
            
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
    df_tabela['aproveitamento'] = (df_tabela['pontos'] / (df_tabela['jogos'] * 3) * 100).round(1)
    df_tabela = df_tabela.sort_values(by=["pontos", "vitorias", "saldo_gols", "gols_pro"], ascending=False).reset_index(drop=True)
    df_tabela.index = df_tabela.index + 1

def colorir_zonas(val):
    cores = []
    for i in range(len(val)):
        posicao = i + 1
        nome_time = df_tabela.iloc[i]['nome_time']
        if time_favorito != "Nenhum" and nome_time == time_favorito:
            cores.append('background-color: #ffe8a1; color: #000000; font-weight: bold;')
            continue
        if posicao <= 4:
            cores.append('background-color: #d4edda; color: #155724;')
        elif posicao == 5:
            cores.append('background-color: #cce5ff; color: #004085;')
        elif 6 <= posicao <= 11:
            cores.append('background-color: #fff3cd; color: #856404;')
        elif 17 <= posicao <= 20:
            cores.append('background-color: #f8d7da; color: #721c24;')
        else:
            cores.append('')
    return cores

# --- ESTRUTURA DE ABAS ---
tab_tabela, tab_simulador = st.tabs(["📊 Classificação", "🎮 Simulador"])

# 1. PAINEL DE CLASSIFICAÇÃO
with tab_tabela:
    st.subheader("📊 Classificação em Tempo Real")
    if not df_tabela.empty:
        m1, m2 = st.columns(2)
        m1.metric("🏆 Líder", f"{df_tabela.iloc[0]['nome_time']}", f"{df_tabela.iloc[0]['pontos']} pts")
        m2.metric("🛡️ Corte G-4", f"{df_tabela.iloc[3]['nome_time']}", f"{df_tabela.iloc[3]['pontos']} pts")
        st.write("")
        
        cols_exibir = ['nome_time', 'pontos', 'jogos', 'vitorias', 'empates', 'derrotas', 'gols_pro', 'gols_contra', 'saldo_gols', 'aproveitamento']
        st.dataframe(
            df_tabela[cols_exibir].style.apply(colorir_zonas, axis=0).format({"aproveitamento": "{:.1f}%"}),
            use_container_width=True,
            hide_index=False,
            height=740
        )
        st.caption("🟢 G-4 | 🔵 Pré-Libertadores | 🟡 Sul-Americana | 🔴 Z-4")

# 2. PAINEL DO SIMULADOR DE JOGOS
with tab_simulador:
    st.subheader(f"🎮 Jogos da {num_rodada}ª Rodada")
    
    if st.button("🧹 Limpar Meus Palpites"):
        for idx in range(len(CONFRONTOS_27)):
            k_m = f"r{num_rodada}_m_{idx}"
            k_v = f"r{num_rodada}_v_{idx}"
            if k_m in st.session_state:
                del st.session_state[k_m]
            if k_v in st.session_state:
                del st.session_state[k_v]
        st.rerun()

    for idx, jogo in enumerate(CONFRONTOS_27):
        mandante, visitante, data_hora_str = jogo
        chave_live = f"{mandante}x{visitante}"
        
        # Configuração de status ao vivo
        if chave_live in placar_live:
            st_info = placar_live[chave_live]
            if st_info['state'] == 'in':
                badge = f"🟢 AO VIVO ({st_info['detail']})"
                jogo_bloqueado = True
                val_m = st_info['gm']
                val_v = st_info['gv']
            elif st_info['state'] == 'post':
                badge = "🔴 FIM"
                jogo_bloqueado = True
                val_m = st_info['gm']
                val_v = st_info['gv']
            else:
                badge = f"📅 {data_hora_str}"
                jogo_bloqueado = False
                val_m = 0
                val_v = 0
        else:
            badge = f"📅 {data_hora_str}"
            jogo_bloqueado = False
            val_m = 0
            val_v = 0

        st.markdown(f"<div class='status-badge'>{badge}</div>", unsafe_allow_html=True)
        
        col_m, col_pm, col_x, col_pv, col_v = st.columns([2.2, 1.1, 0.4, 1.1, 2.2])
        with col_m:
            st.markdown(f"<div class='time-nome-m'>{mandante}</div>", unsafe_allow_html=True)
        with col_pm:
            st.number_input(
                "", min_value=0, value=val_m, key=f"r{num_rodada}_m_{idx}", 
                label_visibility="collapsed", disabled=jogo_bloqueado
            )
        with col_x:
            st.write("🔒" if jogo_bloqueado else "x")
        with col_pv:
            st.number_input(
                "", min_value=0, value=val_v, key=f"r{num_rodada}_v_{idx}", 
                label_visibility="collapsed", disabled=jogo_bloqueado
            )
        with col_v:
            st.markdown(f"<div class='time-nome-v'>{visitante}</div>", unsafe_allow_html=True)
            
        st.divider()
