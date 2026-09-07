import streamlit as st
import pandas as pd
import requests

# Configuração da página - Layout Wide
st.set_page_config(page_title="Brasileirão 2026", layout="wide", initial_sidebar_state="collapsed")

# --- CSS RESPONSIVO HÍBRIDO ---
st.markdown("""
<style>
    /* Elevação e otimização de espaço superior */
    .block-container {
        padding-top: 0.8rem !important;
        padding-bottom: 0rem !important;
    }

    /* DESKTOP (Telas maiores que 768px): esconde abas e posiciona em 2 colunas */
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

    /* MOBILE (Telas até 768px): mantém 2 abas e reduz margens */
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

# --- 1. BUSCA DA TABELA BASE OFICIAL EM TEMPO REAL ---
@st.cache_data(ttl=30) # Atualiza o cache a cada 30 segundos
def buscar_tabela_base():
    url = "https://www.espn.com.br/futebol/liga/_/nome/bra.1/tabela"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    try:
        res = requests.get(url, headers=headers, timeout=5)
        if res.status_code == 200:
            tables = pd.read_html(res.text)
            df_times = tables[0]
            df_stats = tables[1]
            df = pd.concat([df_times, df_stats], axis=1)
            df.columns = ['Time_Raw', 'J', 'V', 'E', 'D', 'GP', 'GC', 'SG', 'PTS']
            df['nome_time'] = df['Time_Raw'].str.replace(r'^[0-9]+', '', regex=True).str.strip()
            
            return pd.DataFrame({
                'nome_time': df['nome_time'],
                'pontos': df['PTS'].astype(int),
                'jogos': df['J'].astype(int),
                'vitorias': df['V'].astype(int),
                'empates': df['E'].astype(int),
                'derrotas': df['D'].astype(int),
                'gols_pro': df['GP'].astype(int),
                'gols_contra': df['GC'].astype(int),
                'saldo_gols': df['SG'].astype(int)
            })
    except Exception:
        pass
    
    try:
        return pd.read_csv("Brasileirao_SQL.csv")
    except Exception:
        return pd.DataFrame()

# --- 2. REGISTRO DE CONFRONTOS OFICIAIS ---
CONFRONTOS_PADRAO = {
    27: [
        ("Coritiba", "Athletico-PR", "Sexta, 11/09 - 21:00", None, None, "AGENDADO"),
        ("Atlético-MG", "Fluminense", "Sábado, 12/09 - 16:00", None, None, "AGENDADO"),
        ("Grêmio", "Vasco", "Sábado, 12/09 - 16:00", None, None, "AGENDADO"),
        ("Chapecoense", "Internacional", "Sábado, 12/09 - 17:00", None, None, "AGENDADO"),
        ("Palmeiras", "São Paulo", "Sábado, 12/09 - 18:30", None, None, "AGENDADO"),
        ("Botafogo", "Red Bull Bragantino", "Sábado, 12/09 - 20:30", None, None, "AGENDADO"),
        ("Santos", "Cruzeiro", "Sábado, 12/09 - 21:00", None, None, "AGENDADO"),
        ("Mirassol", "Vitória", "Domingo, 13/09 - 16:00", None, None, "AGENDADO"),
        ("Flamengo", "Corinthians", "Domingo, 13/09 - 17:30", None, None, "AGENDADO"),
        ("Bahia", "Remo", "Segunda, 14/09 - 20:00", None, None, "AGENDADO")
    ],
    28: [
        ("Atlético-MG", "Chapecoense", "Sábado, 19/09 - 16:00", None, None, "AGENDADO"),
        ("Mirassol", "Botafogo", "Sábado, 19/09 - 17:00", None, None, "AGENDADO"),
        ("Remo", "Santos", "Sábado, 19/09 - 18:30", None, None, "AGENDADO"),
        ("Vasco", "Coritiba", "Sábado, 19/09 - 20:30", None, None, "AGENDADO"),
        ("São Paulo", "Internacional", "Sábado, 19/09 - 21:00", None, None, "AGENDADO"),
        ("Grêmio", "Palmeiras", "Domingo, 20/09 - 11:00", None, None, "AGENDADO"),
        ("Vitória", "Cruzeiro", "Domingo, 20/09 - 16:00", None, None, "AGENDADO"),
        ("Corinthians", "Fluminense", "Domingo, 20/09 - 16:00", None, None, "AGENDADO")
    ]
}

df_base = buscar_tabela_base()

# CONTROLES SUPERIORES
c1, c2 = st.columns([1, 2])
with c1:
    num_rodada = st.selectbox("Rodada:", list(CONFRONTOS_PADRAO.keys()), index=0)
with c2:
    lista_times = ["Nenhum"] + sorted(df_base['nome_time'].unique().tolist()) if not df_base.empty else ["Nenhum"]
    time_favorito = st.selectbox("⭐ Time do Coração:", lista_times)

# --- 3. RECALCULO REATIVO DA TABELA COM OS PALPITES ---
df_tabela = df_base.copy()
jogos_atuais = CONFRONTOS_PADRAO.get(num_rodada, [])

if not df_tabela.empty:
    for idx, jogo in enumerate(jogos_atuais):
        mandante, visitante, data_hora_str, gm_real, gv_real, status = jogo
        
        key_m = f"r{num_rodada}_m_{idx}"
        key_v = f"r{num_rodada}_v_{idx}"
        
        # Pega os valores preenchidos no formulário pelo usuário
        if key_m in st.session_state and key_v in st.session_state:
            gm = st.session_state[key_m]
            gv = st.session_state[key_v]
            
            if mandante in df_tabela['nome_time'].values and visitante in df_tabela['nome_time'].values:
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
        for idx in range(10):
            k_m = f"r{num_rodada}_m_{idx}"
            k_v = f"r{num_rodada}_v_{idx}"
            if k_m in st.session_state:
                del st.session_state[k_m]
            if k_v in st.session_state:
                del st.session_state[k_v]
        st.rerun()

    jogos = CONFRONTOS_PADRAO.get(num_rodada, [])
    
    for idx, jogo in enumerate(jogos):
        mandante, visitante, data_hora_str, gm_real, gv_real, status = jogo
        
        st.markdown(f"<div class='status-badge'>📅 {data_hora_str}</div>", unsafe_allow_html=True)
        
        col_m, col_pm, col_x, col_pv, col_v = st.columns([2.2, 1.1, 0.4, 1.1, 2.2])
        with col_m:
            st.markdown(f"<div class='time-nome-m'>{mandante}</div>", unsafe_allow_html=True)
        with col_pm:
            st.number_input(
                "", min_value=0, value=0, key=f"r{num_rodada}_m_{idx}", 
                label_visibility="collapsed"
            )
        with col_x:
            st.write("x")
        with col_pv:
            st.number_input(
                "", min_value=0, value=0, key=f"r{num_rodada}_v_{idx}", 
                label_visibility="collapsed"
            )
        with col_v:
            st.markdown(f"<div class='time-nome-v'>{visitante}</div>", unsafe_allow_html=True)
            
        st.divider()
