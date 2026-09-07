import streamlit as st
import pandas as pd
import requests

# Configuração da página - Layout Wide
st.set_page_config(page_title="Brasileirão 2026", layout="wide", initial_sidebar_state="collapsed")

# --- CSS PARA ELEVAR O CABEÇALHO E OTIMIZAR ESPAÇAMENTOS ---
st.markdown("""
<style>
    /* Elevação do layout para otimizar espaço no topo */
    .block-container {
        padding-top: 0.3rem !important;
        padding-bottom: 0rem !important;
    }
    
    /* Redução de margem do título principal */
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

    .time-nome-m { text-align: right; font-weight: bold; font-size: 13px; }
    .time-nome-v { text-align: left; font-weight: bold; font-size: 13px; }
    .status-badge { font-size: 11px; color: #555; margin-bottom: 2px; font-weight: 600; text-align: center; }

    @media (max-width: 768px) {
        .block-container {
            padding-left: 0.4rem !important;
            padding-right: 0.4rem !important;
        }
    }
</style>
""", unsafe_allow_html=True)

st.title("⚽ Brasileirão 2026")

# --- 1. DADOS DA TABELA BASE OFICIAL (CONSOLIDADA NA 26ª RODADA) ---
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

# --- 2. CONSULTA API PUBLICA DA ESPN (AO VIVO) ---
def buscar_jogos_espn():
    url = "https://site.api.espn.com/apis/site/v2/sports/soccer/bra.1/scoreboard"
    try:
        res = requests.get(url, timeout=2)
        if res.status_code == 200:
            dados = res.json()
            eventos = dados.get('events', [])
            jogos = {}
            for ev in eventos:
                comp = ev['competitions'][0]
                m_nome = comp['competitors'][0]['team']['shortDisplayName']
                v_nome = comp['competitors'][1]['team']['shortDisplayName']
                m_score = int(comp['competitors'][0]['score'])
                v_score = int(comp['competitors'][1]['score'])
                state = ev['status']['type']['state']
                detail = ev['status']['type']['shortDetail']
                
                jogos[f"{m_nome}x{v_nome}"] = {
                    'gm': m_score, 'gv': v_score, 'state': state, 'detail': detail
                }
            return jogos
    except Exception:
        pass
    return {}

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
        ("Bahia", "Remo", "Segunda, 14/09 - 20:00")
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
        ("Athletico-PR", "Bahia", "Segunda, 21/09 - 20:00")
    ]
}

placar_live = buscar_jogos_espn()

# CONTROLES SUPERIORES
c_ctrl1, c_ctrl2 = st.columns([1, 2])
with c_ctrl1:
    num_rodada = st.selectbox("Rodada:", list(CALENDARIO_RODADAS.keys()), index=0)
with c_ctrl2:
    df_base = carregar_tabela_oficial()
    lista_times = ["Nenhum"] + sorted(df_base['nome_time'].unique().tolist())
    time_favorito = st.selectbox("⭐ Destaque o Time do Coração:", lista_times)

# --- 3. RECALCULO REATIVO DA TABELA BASEADO NOS PALPITES DO SIMULADOR OU JOGOS REALIZADOS ---
df_simulado = df_base.copy()
confrontos = CALENDARIO_RODADAS.get(num_rodada, [])

for idx, (mandante, visitante, _) in enumerate(confrontos):
    key_m = f"sim_r{num_rodada}_m_{idx}"
    key_v = f"sim_r{num_rodada}_v_{idx}"
    chave_live = f"{mandante}x{visitante}"
    
    if chave_live in placar_live and placar_live[chave_live]['state'] in ['in', 'post']:
        gm = placar_live[chave_live]['gm']
        gv = placar_live[chave_live]['gv']
        jogou = True
    elif key_m in st.session_state and key_v in st.session_state:
        gm = st.session_state[key_m]
        gv = st.session_state[key_v]
        jogou = True
    else:
        jogou = False

    if jogou and mandante in df_simulado['nome_time'].values and visitante in df_simulado['nome_time'].values:
        idx_m = df_simulado[df_simulado['nome_time'] == mandante].index[0]
        idx_v = df_simulado[df_simulado['nome_time'] == visitante].index[0]
        
        df_simulado.at[idx_m, 'jogos'] += 1
        df_simulado.at[idx_v, 'jogos'] += 1
        df_simulado.at[idx_m, 'gols_pro'] += gm
        df_simulado.at[idx_m, 'gols_contra'] += gv
        df_simulado.at[idx_v, 'gols_pro'] += gv
        df_simulado.at[idx_v, 'gols_contra'] += gm
        
        if gm > gv:
            df_simulado.at[idx_m, 'pontos'] += 3
            df_simulado.at[idx_m, 'vitorias'] += 1
            df_simulado.at[idx_v, 'derrotas'] += 1
        elif gv > gm:
            df_simulado.at[idx_v, 'pontos'] += 3
            df_simulado.at[idx_v, 'vitorias'] += 1
            df_simulado.at[idx_m, 'derrotas'] += 1
        else:
            df_simulado.at[idx_m, 'pontos'] += 1
            df_simulado.at[idx_v, 'pontos'] += 1
            df_simulado.at[idx_m, 'empates'] += 1
            df_simulado.at[idx_v, 'empates'] += 1

df_simulado['saldo_gols'] = df_simulado['gols_pro'] - df_simulado['gols_contra']
df_simulado['aproveitamento'] = (df_simulado['pontos'] / (df_simulado['jogos'] * 3) * 100).round(1)
df_simulado = df_simulado.sort_values(by=["pontos", "vitorias", "saldo_gols", "gols_pro"], ascending=False).reset_index(drop=True)
df_simulado.index = df_simulado.index + 1

def colorir_zonas(val):
    cores = []
    for i in range(len(val)):
        posicao = i + 1
        nome_time = df_simulado.iloc[i]['nome_time']
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

# --- 4. NAVEGAÇÃO POR ABAS FIXAS (3 ABAS NATIVAS) ---
tab_tabela, tab_simulador, tab_aovivo = st.tabs(["📊 Classificação", "🎮 Simulador", "🔴 Ao Vivo"])

# ABA 1: CLASSIFICAÇÃO COMPLETA
with tab_tabela:
    if not df_simulado.empty:
        m1, m2 = st.columns(2)
        m1.metric("🏆 Líder", f"{df_simulado.iloc[0]['nome_time']}", f"{df_simulado.iloc[0]['pontos']} pts")
        m2.metric("🛡️ G-4", f"{df_simulado.iloc[3]['nome_time']}", f"{df_simulado.iloc[3]['pontos']} pts")
        
        cols_exibir = ['nome_time', 'pontos', 'jogos', 'vitorias', 'empates', 'derrotas', 'gols_pro', 'gols_contra', 'saldo_gols', 'aproveitamento']
        st.dataframe(
            df_simulado[cols_exibir].style.apply(colorir_zonas, axis=0).format({"aproveitamento": "{:.1f}%"}),
            use_container_width=True,
            hide_index=False,
            height=820
        )
        st.caption("🟢 G-4 | 🔵 Pré-Libertadores | 🟡 Sul-Americana | 🔴 Z-4")

# ABA 2: SIMULADOR DE PALPITES (INTERATIVO)
with tab_simulador:
    st.subheader(f"🎮 Palpites para a {num_rodada}ª Rodada")
    
    if st.button("🧹 Limpar Meus Palpites"):
        for idx in range(len(confrontos)):
            k_m = f"sim_r{num_rodada}_m_{idx}"
            k_v = f"sim_r{num_rodada}_v_{idx}"
            if k_m in st.session_state:
                del st.session_state[k_m]
            if k_v in st.session_state:
                del st.session_state[k_v]
        st.rerun()

    for idx, (mandante, visitante, data_hora_str) in enumerate(confrontos):
        st.markdown(f"<div class='status-badge'>📅 {data_hora_str}</div>", unsafe_allow_html=True)
        
        c_m, c_pm, c_x, c_pv, c_v = st.columns([2.2, 1.1, 0.3, 1.1, 2.2])
        with c_m:
            st.markdown(f"<div class='time-nome-m'>{mandante}</div>", unsafe_allow_html=True)
        with c_pm:
            st.number_input("", min_value=0, value=0, key=f"sim_r{num_rodada}_m_{idx}", label_visibility="collapsed")
        with c_x:
            st.write("x")
        with c_pv:
            st.number_input("", min_value=0, value=0, key=f"sim_r{num_rodada}_v_{idx}", label_visibility="collapsed")
        with c_v:
            st.markdown(f"<div class='time-nome-v'>{visitante}</div>", unsafe_allow_html=True)
            
        st.divider()

# ABA 3: PAINEL AO VIVO (COM BOTÃO DE ATUALIZAÇÃO MANUALE SEM PULOS)
with tab_aovivo:
    c_tit, c_btn = st.columns([2, 1])
    with c_tit:
        st.subheader(f"🔴 Central Ao Vivo - {num_rodada}ª Rodada")
    with c_btn:
        if st.button("🔄 Atualizar Placar Ao Vivo"):
            st.cache_data.clear()
            st.rerun()

    for idx, (mandante, visitante, data_hora_str) in enumerate(confrontos):
        chave_live = f"{mandante}x{visitante}"
        
        if chave_live in placar_live:
            st_info = placar_live[chave_live]
            if st_info['state'] == 'in':
                badge = f"🟢 AO VIVO ({st_info['detail']})"
                p_m = st_info['gm']
                p_v = st_info['gv']
            elif st_info['state'] == 'post':
                badge = "🔴 FIM DE JOGO"
                p_m = st_info['gm']
                p_v = st_info['gv']
            else:
                badge = f"🕒 AGENDADO - {data_hora_str}"
                p_m = "-"
                p_v = "-"
        else:
            badge = f"🕒 AGENDADO - {data_hora_str}"
            p_m = "-"
            p_v = "-"

        st.markdown(f"<div class='status-badge'>{badge}</div>", unsafe_allow_html=True)
        
        c_m, c_pm, c_x, c_pv, c_v = st.columns([2.2, 1.0, 0.4, 1.0, 2.2])
        with c_m:
            st.markdown(f"<div class='time-nome-m'>{mandante}</div>", unsafe_allow_html=True)
        with c_pm:
            st.markdown(f"<h3 style='text-align: center; margin: 0;'>{p_m}</h3>", unsafe_allow_html=True)
        with c_x:
            st.markdown("<div style='text-align: center; font-weight: bold;'>x</div>", unsafe_allow_html=True)
        with c_pv:
            st.markdown(f"<h3 style='text-align: center; margin: 0;'>{p_v}</h3>", unsafe_allow_html=True)
        with c_v:
            st.markdown(f"<div class='time-nome-v'>{visitante}</div>", unsafe_allow_html=True)
            
        st.divider()
