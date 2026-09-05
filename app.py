import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# Configuração da página - Layout Responsivo
st.set_page_config(page_title="Brasileirão 2026", layout="wide", initial_sidebar_state="collapsed")

# CSS Customizado para Otimização Mobile
st.markdown("""
<style>
    /* Ajustes para telas pequenas (smartphones) */
    @media (max-width: 768px) {
        .block-container {
            padding-left: 0.8rem !important;
            padding-right: 0.8rem !important;
            padding-top: 1rem !important;
        }
        div[data-baseweb="select"] {
            font-size: 14px;
        }
        .stNumberInput input {
            text-align: center;
            font-size: 16px !important;
            font-weight: bold;
        }
    }
    /* Estilização dos cards de times no simulador */
    .time-nome-m { text-align: right; font-weight: bold; font-size: 15px; }
    .time-nome-v { text-align: left; font-weight: bold; font-size: 15px; }
    .status-badge { font-size: 12px; color: #666; margin-bottom: 2px; }
</style>
""", unsafe_allow_html=True)

st.title("⚽ Brasileirão 2026")

# --- 1. BUSCA DA TABELA BASE ---
@st.cache_data(ttl=60)
def buscar_tabela_base():
    url = "https://www.espn.com.br/futebol/liga/_/nome/bra.1/tabela"
    headers = {'User-Agent': 'Mozilla/5.0'}
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

# --- 2. JOGOS DA RODADA COM PLACARES FIXADOS ---
CONFRONTOS_PADRAO = {
    26: [
        ("Red Bull Bragantino", "Bahia", "2026-09-05 16:00", 2, 3, "ENCERRADO"),
        ("São Paulo", "Atlético-MG", "2026-09-05 18:30", 0, 0, "EM_ANDAMENTO"),
        ("Fluminense", "Vasco", "2026-09-05 21:00", None, None, "AGENDADO"),
        ("Coritiba", "Mirassol", "2026-09-06 11:00", None, None, "AGENDADO"),
        ("Cruzeiro", "Athletico-PR", "2026-09-06 16:00", None, None, "AGENDADO"),
        ("Remo", "Flamengo", "2026-09-06 16:00", None, None, "AGENDADO"),
        ("Internacional", "Santos", "2026-09-06 16:00", None, None, "AGENDADO"),
        ("Botafogo", "Palmeiras", "2026-09-06 18:30", None, None, "AGENDADO"),
        ("Corinthians", "Chapecoense", "2026-09-06 19:30", None, None, "AGENDADO"),
        ("Vitória", "Grêmio", "2026-09-07 20:00", None, None, "AGENDADO")
    ],
    27: [
        ("Coritiba", "Athletico-PR", "2026-09-11 21:00", None, None, "AGENDADO"),
        ("Atlético-MG", "Fluminense", "2026-09-12 16:00", None, None, "AGENDADO"),
        ("Grêmio", "Vasco", "2026-09-12 16:00", None, None, "AGENDADO"),
        ("Chapecoense", "Internacional", "2026-09-12 17:00", None, None, "AGENDADO"),
        ("Palmeiras", "São Paulo", "2026-09-12 18:30", None, None, "AGENDADO"),
        ("Botafogo", "Red Bull Bragantino", "2026-09-12 20:30", None, None, "AGENDADO"),
        ("Santos", "Cruzeiro", "2026-09-12 21:00", None, None, "AGENDADO"),
        ("Mirassol", "Vitória", "2026-09-13 16:00", None, None, "AGENDADO"),
        ("Flamengo", "Corinthians", "2026-09-13 17:30", None, None, "AGENDADO"),
        ("Bahia", "Remo", "2026-09-14 20:00", None, None, "AGENDADO")
    ]
}

df_base = buscar_tabela_base()

# --- 3. SELEÇÃO DE CONTROLES ---
c1, c2 = st.columns([1, 2])
with c1:
    num_rodada = st.selectbox("Rodada:", list(range(26, 39)))
with c2:
    lista_times = ["Nenhum"] + sorted(df_base['nome_time'].unique().tolist()) if not df_base.empty else ["Nenhum"]
    time_favorito = st.selectbox("⭐ Time do Coração:", lista_times)

# --- 4. ABAS PARA NAVEGAÇÃO MOBILE PERFEITA ---
aba_tabela, aba_simulador = st.tabs(["📊 Classificação", "🎮 Simulador de Jogos"])

# RENDERIZAÇÃO DO SIMULADOR (ABA 2)
with aba_simulador:
    st.subheader(f"Jogos da {num_rodada}ª Rodada")
    
    if st.button("🧹 Limpar Meus Palpites"):
        for i in range(10):
            if f"r{num_rodada}_m_{i}" in st.session_state:
                st.session_state[f"r{num_rodada}_m_{i}"] = 0
            if f"r{num_rodada}_v_{i}" in st.session_state:
                st.session_state[f"r{num_rodada}_v_{i}"] = 0
        st.rerun()

    jogos = CONFRONTOS_PADRAO.get(num_rodada, [])
    placares_rodada = []
    agora = datetime.now()
    
    for idx, jogo in enumerate(jogos):
        mandante, visitante, data_hora_str, gm_real, gv_real, status = jogo
        data_jogo = datetime.strptime(data_hora_str, "%Y-%m-%d %H:%M")
        
        jogo_bloqueado = (agora >= data_jogo) or (status in ["ENCERRADO", "EM_ANDAMENTO"])
        
        val_m = gm_real if gm_real is not None else 0
        val_v = gv_real if gv_real is not None else 0
        
        hora_exibicao = data_hora_str.split(" ")[1]
        if status == "ENCERRADO":
            badge = "🔴 FIM"
        elif status == "EM_ANDAMENTO":
            badge = "🟢 AO VIVO"
        else:
            badge = f"🕒 {hora_exibicao}"

        st.markdown(f"<div class='status-badge'>{badge}</div>", unsafe_allow_html=True)
        
        col_m, col_pm, col_x, col_pv, col_v = st.columns([2.2, 1.1, 0.4, 1.1, 2.2])
        with col_m:
            st.markdown(f"<div class='time-nome-m'>{mandante}</div>", unsafe_allow_html=True)
        with col_pm:
            gm = st.number_input(
                "", min_value=0, value=val_m, key=f"r{num_rodada}_m_{idx}", 
                label_visibility="collapsed", disabled=jogo_bloqueado
            )
        with col_x:
            st.write("🔒" if jogo_bloqueado else "x")
        with col_pv:
            gv = st.number_input(
                "", min_value=0, value=val_v, key=f"r{num_rodada}_v_{idx}", 
                label_visibility="collapsed", disabled=jogo_bloqueado
            )
        with col_v:
            st.markdown(f"<div class='time-nome-v'>{visitante}</div>", unsafe_allow_html=True)
            
        placares_rodada.append((mandante, gm, gv, visitante, status, jogo_bloqueado))
        st.divider()

# --- 5. RECALCULO COMPLETO DA TABELA (INCLUINDO JOGOS ENCERRADOS) ---
df_tabela = df_base.copy()

if not df_tabela.empty:
    for mandante, gm, gv, visitante, status, bloqueado in placares_rodada:
        # CONDIÇÃO CORRIGIDA: Processa tanto jogos ENCERRADOS/AO VIVO quanto palpites simulados
        if (status in ["ENCERRADO", "EM_ANDAMENTO"]) or (not bloqueado and (gm > 0 or gv > 0)):
            # Se o jogo já está no CSV/Base com jogos somados, evitamos duplicação controlando a flag
            if mandante in df_tabela['nome_time'].values and visitante in df_tabela['nome_time'].values:
                idx_m = df_tabela[df_tabela['nome_time'] == mandante].index[0]
                idx_v = df_tabela[df_tabela['nome_time'] == visitante].index[0]
                
                # Se a base externa ainda não somou o jogo de hoje do Bahia (25 jogos em vez de 26)
                if status == "ENCERRADO" and mandante == "Red Bull Bragantino" and df_tabela.at[idx_v, 'jogos'] == 25:
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

                # Para palpites do usuário em jogos futuros
                elif not bloqueado and (gm > 0 or gv > 0):
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

# --- 6. RENDERIZAÇÃO DA TABELA (ABA 1) ---
with aba_tabela:
    st.subheader("Classificação em Tempo Real")
    
    if not df_tabela.empty:
        # Métricas Rápidas no topo
        m1, m2 = st.columns(2)
        m1.metric("🏆 Líder", f"{df_tabela.iloc[0]['nome_time']}", f"{df_tabela.iloc[0]['pontos']} pts")
        m2.metric("🛡️ Corte G-4", f"{df_tabela.iloc[3]['nome_time']}", f"{df_tabela.iloc[3]['pontos']} pts")
        
        st.write("")
        
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

        # Tabela Formatada para telas móveis
        cols_exibir = ['nome_time', 'pontos', 'jogos', 'vitorias', 'saldo_gols', 'aproveitamento']
        
        st.dataframe(
            df_tabela[cols_exibir].style.apply(colorir_zonas, axis=0).format({"aproveitamento": "{:.1f}%"}),
            use_container_width=True,
            hide_index=False,
            height=650
        )
        
        st.caption("🟢 G-4 (Libertadores) | 🔵 Pré-Libertadores | 🟡 Sul-Americana | 🔴 Z-4")
