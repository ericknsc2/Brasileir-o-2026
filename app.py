import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# Configuração da página - Layout Wide
st.set_page_config(page_title="Brasileirão 2026", layout="wide", initial_sidebar_state="collapsed")

# --- CSS RESPONSIVO HÍBRIDO ---
st.markdown("""
<style>
    /* Subir todo o conteúdo da página para aproveitar o topo */
    .block-container {
        padding-top: 0.8rem !important;
        padding-bottom: 0rem !important;
    }

    /* DESKTOP (Telas maiores que 768px):
       Oculta o cabeçalho das abas e posiciona o conteúdo em 2 colunas lado a lado */
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

# --- OBTENÇÃO DA API KEY VIA SECRETS ---
API_KEY = st.secrets.get("FOOTBALL_API_KEY", "")
HEADERS = {'X-Auth-Token': API_KEY} if API_KEY else {}

# --- 1. BUSCA DA TABELA E JOGOS VIA API (FOOTBALL-DATA.ORG) ---
@st.cache_data(ttl=60)
def carregar_dados_api(rodada_sel):
    if not API_KEY:
        st.warning("⚠️ Adicione a chave 'FOOTBALL_API_KEY' nos Secrets do Streamlit para ativar a API ao vivo.")
        return pd.DataFrame(), []

    url_tabela = "https://api.football-data.org/v4/competitions/BSA/standings"
    url_jogos = f"https://api.football-data.org/v4/competitions/BSA/matches?matchday={rodada_sel}"
    
    df_tabela = pd.DataFrame()
    jogos_lista = []
    
    try:
        # A) Busca Tabela de Classificação
        res_tab = requests.get(url_tabela, headers=HEADERS, timeout=8)
        if res_tab.status_code == 200:
            dados_tab = res_tab.json()
            times = []
            for item in dados_tab['standings'][0]['table']:
                times.append({
                    'nome_time': item['team']['shortName'],
                    'pontos': item['points'],
                    'jogos': item['playedGames'],
                    'vitorias': item['won'],
                    'empates': item['draw'],
                    'derrotas': item['lost'],
                    'gols_pro': item['goalsFor'],
                    'gols_contra': item['goalsAgainst'],
                    'saldo_gols': item['goalDifference']
                })
            df_tabela = pd.DataFrame(times)

        # B) Busca Jogos da Rodada Selecionada
        res_jogos = requests.get(url_jogos, headers=HEADERS, timeout=8)
        if res_jogos.status_code == 200:
            dados_jogos = res_jogos.json()
            for match in dados_jogos.get('matches', []):
                mandante = match['homeTeam']['shortName']
                visitante = match['awayTeam']['shortName']
                gm = match['score']['fullTime']['home']
                gv = match['score']['fullTime']['away']
                status = match['status'] # FINISHED, IN_PLAY, PAUSED, TIMED
                data_iso = match['utcDate']
                
                # Formatador de Horário
                try:
                    dt = datetime.fromisoformat(data_iso.replace('Z', '+00:00'))
                    hora_str = dt.strftime("%H:%M")
                except Exception:
                    hora_str = "--:--"

                jogos_lista.append({
                    'mandante': mandante,
                    'visitante': visitante,
                    'gm': gm if gm is not None else 0,
                    'gv': gv if gv is not None else 0,
                    'status': status,
                    'hora': hora_str
                })

    except Exception as e:
        st.error(f"Erro na conexão com a API: {e}")

    return df_tabela, jogos_lista

# --- CONTROLES SUPERIORES ---
c1, c2 = st.columns([1, 2])
with c1:
    num_rodada = st.selectbox("Rodada:", list(range(1, 39)), index=25) # Padrão na 26ª rodada

df_base, jogos_api = carregar_dados_api(num_rodada)

with c2:
    lista_times = ["Nenhum"] + sorted(df_base['nome_time'].unique().tolist()) if not df_base.empty else ["Nenhum"]
    time_favorito = st.selectbox("⭐ Time do Coração:", lista_times)

# --- RECALCULO E ESTILIZAÇÃO DA TABELA ---
df_tabela = df_base.copy()

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

# --- ESTRUTURA HÍBRIDA DE ABAS ---
tab_tabela, tab_simulador = st.tabs(["📊 Classificação", "🎮 Simulador"])

# 1. PAINEL DE CLASSIFICAÇÃO
with tab_tabela:
    st.subheader("📊 Classificação em Tempo Real (Oficial)")
    if not df_tabela.empty:
        m1, m2 = st.columns(2)
        m1.metric("🏆 Líder", f"{df_tabela.iloc[0]['nome_time']}", f"{df_tabela.iloc[0]['pontos']} pts")
        m2.metric("🛡️ Corte G-4", f"{df_tabela.iloc[3]['nome_time']}", f"{df_tabela.iloc[3]['pontos']} pts")
        st.write("")
        
        # Adiciona a coluna de aproveitamento
        df_tabela['aproveitamento'] = (df_tabela['pontos'] / (df_tabela['jogos'] * 3) * 100).round(1)
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
        for i in range(len(jogos_api)):
            if f"r{num_rodada}_m_{i}" in st.session_state:
                st.session_state[f"r{num_rodada}_m_{i}"] = 0
            if f"r{num_rodada}_v_{i}" in st.session_state:
                st.session_state[f"r{num_rodada}_v_{i}"] = 0
        st.rerun()

    if jogos_api:
        for idx, jogo in enumerate(jogos_api):
            mandante = jogo['mandante']
            visitante = jogo['visitante']
            status = jogo['status']
            hora = jogo['hora']
            
            # Bloqueia caso o jogo já tenha terminado ou esteja ao vivo
            jogo_bloqueado = status in ["FINISHED", "IN_PLAY", "PAUSED"]
            
            val_m = jogo['gm'] if jogo_bloqueado else 0
            val_v = jogo['gv'] if jogo_bloqueado else 0
            
            if status == "FINISHED":
                badge = "🔴 FIM"
            elif status in ["IN_PLAY", "PAUSED"]:
                badge = "🟢 AO VIVO"
            else:
                badge = f"🕒 {hora}"

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
    else:
        st.info("Nenhum confronto encontrado para esta rodada ou aguardando conexão com a API.")
