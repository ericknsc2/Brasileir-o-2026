import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# Configuração da página
st.set_page_config(page_title="Brasileirão 2026", layout="wide")

# Título da Aplicação
st.title("⚽ Brasileirão 2026 - Tabela & Simulador ao Vivo")

# --- 1. BUSCA DE DADOS E CONFRONTOS VIA GE (GLOBO ESPORTE) ---
@st.cache_data(ttl=120)  # Atualiza os dados do ge a cada 2 minutos (120 segundos)
def buscar_dados_ge():
    try:
        # Endpoint público de dados do Brasileirão Série A no GE
        url_tabela = "https://api.ge.globo.com/futebol/campeonato/brasileiro-serie-a/tabela"
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(url_tabela, headers=headers, timeout=5)
        
        if res.status_code == 200:
            dados = res.json()
            times = []
            for t in dados.get("classificacao", []):
                times.append({
                    'nome_time': t['time']['nome_popular'],
                    'pontos': t['pontos'],
                    'jogos': t['jogos'],
                    'vitorias': t['vitorias'],
                    'empates': t['empates'],
                    'derrotas': t['derrotas'],
                    'gols_pro': t['gols_pro'],
                    'gols_contra': t['gols_contra'],
                    'saldo_gols': t['saldo_gols']
                })
            return pd.DataFrame(times)
        else:
            return pd.read_csv("Brasileirao_SQL.csv")
    except Exception:
        # Fallback de segurança para o CSV local caso haja instabilidade de rede
        try:
            return pd.read_csv("Brasileirao_SQL.csv")
        except Exception:
            return pd.DataFrame()

# Estrutura com confrontos e horários oficiais (Servirá para checagem e travamento)
RODADAS = {
    26: [
        ("Red Bull Bragantino", "Bahia", "2026-09-05 16:00"),
        ("São Paulo", "Atlético-MG", "2026-09-05 18:30"),
        ("Fluminense", "Vasco", "2026-09-05 21:00"),
        ("Coritiba", "Mirassol", "2026-09-06 11:00"),
        ("Cruzeiro", "Athletico-PR", "2026-09-06 16:00"),
        ("Remo", "Flamengo", "2026-09-06 16:00"),
        ("Internacional", "Santos", "2026-09-06 16:00"),
        ("Botafogo", "Palmeiras", "2026-09-06 18:30"),
        ("Corinthians", "Chapecoense", "2026-09-06 19:30"),
        ("Vitória", "Grêmio", "2026-09-07 20:00")
    ],
    27: [
        ("Coritiba", "Athletico-PR", "2026-09-11 21:00"),
        ("Atlético-MG", "Fluminense", "2026-09-12 16:00"),
        ("Grêmio", "Vasco", "2026-09-12 16:00"),
        ("Chapecoense", "Internacional", "2026-09-12 17:00"),
        ("Palmeiras", "São Paulo", "2026-09-12 18:30"),
        ("Botafogo", "Red Bull Bragantino", "2026-09-12 20:30"),
        ("Santos", "Cruzeiro", "2026-09-12 21:00"),
        ("Mirassol", "Vitória", "2026-09-13 16:00"),
        ("Flamengo", "Corinthians", "2026-09-13 17:30"),
        ("Bahia", "Remo", "2026-09-14 20:00")
    ]
}

# --- 2. SELEÇÃO DO TIME DO CORAÇÃO ---
df_base = buscar_dados_ge()
lista_times = ["Nenhum"] + sorted(df_base['nome_time'].unique().tolist()) if not df_base.empty else ["Nenhum"]
time_favorito = st.selectbox("⭐ Selecione seu time para destacar na tabela:", lista_times)

# Layout principal em 2 Colunas
col_tabela, col_simulador = st.columns([1.3, 1])

# --- 3. COLUNA DA DIREITA: SIMULADOR COM TRAVAMENTO AUTOMÁTICO ---
with col_simulador:
    st.subheader("🎮 Simulador de Jogos")
    
    col_rodada, col_botao = st.columns([2, 1])
    with col_rodada:
        num_rodada = st.selectbox("Selecione a Rodada:", list(RODADAS.keys()))
    with col_botao:
        st.write("")
        st.write("")
        if st.button("🧹 Limpar Placares", use_container_width=True):
            for i in range(10):
                if f"r{num_rodada}_m_{i}" in st.session_state:
                    st.session_state[f"r{num_rodada}_m_{i}"] = 0
                if f"r{num_rodada}_v_{i}" in st.session_state:
                    st.session_state[f"r{num_rodada}_v_{i}"] = 0
            st.rerun()

    st.write(f"**Confrontos da {num_rodada}ª Rodada:**")
    jogos = RODADAS.get(num_rodada, [])
    
    placares_rodada = []
    agora = datetime.now()
    
    for idx, jogo in enumerate(jogos):
        mandante, visitante, data_hora_str = jogo
        data_jogo = datetime.strptime(data_hora_str, "%Y-%m-%d %H:%M")
        
        # O jogo é bloqueado se o horário atual for maior/igual ao início da partida
        jogo_bloqueado = agora >= data_jogo

        c1, c2, c3, c4, c5 = st.columns([2.5, 1, 0.4, 1, 2.5])
        with c1:
            st.markdown(f"<div style='text-align: right;'><b>{mandante}</b></div>", unsafe_allow_html=True)
        with c2:
            gm = st.number_input(
                "", min_value=0, value=0, key=f"r{num_rodada}_m_{idx}", 
                label_visibility="collapsed", disabled=jogo_bloqueado
            )
        with c3:
            st.write("🔒" if jogo_bloqueado else "x")
        with c4:
            gv = st.number_input(
                "", min_value=0, value=0, key=f"r{num_rodada}_v_{idx}", 
                label_visibility="collapsed", disabled=jogo_bloqueado
            )
        with c5:
            st.markdown(f"<b>{visitante}</b>", unsafe_allow_html=True)
            
        placares_rodada.append((mandante, gm, gv, visitante, jogo_bloqueado))

# --- 4. CÁLCULO E RECLASSIFICAÇÃO DINÂMICA ---
df_tabela = df_base.copy()

if not df_tabela.empty:
    for mandante, gm, gv, visitante, bloqueado in placares_rodada:
        # Aplica a alteração apenas para jogos futuros simulação do usuário
        if not bloqueado and (gm > 0 or gv > 0):
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

    # Critérios de desempate do Brasileirão
    df_tabela = df_tabela.sort_values(by=["pontos", "vitorias", "saldo_gols", "gols_pro"], ascending=False).reset_index(drop=True)
    df_tabela.index = df_tabela.index + 1

# --- 5. FUNÇÃO DE ESTILIZAÇÃO VISUAL ---
def colorir_zonas(val):
    cores = []
    for i in range(len(val)):
        posicao = i + 1
        nome_time = df_tabela.iloc[i]['nome_time']
        
        if time_favorito != "Nenhum" and nome_time == time_favorito:
            cores.append('background-color: #ffe8a1; color: #000000; font-weight: bold;')
            continue

        if posicao <= 4:
            cores.append('background-color: #d4edda; color: #155724;')  # Libertadores
        elif posicao == 5:
            cores.append('background-color: #cce5ff; color: #004085;')  # Pré-Libertadores
        elif 6 <= posicao <= 11:
            cores.append('background-color: #fff3cd; color: #856404;')  # Sul-Americana
        elif 17 <= posicao <= 20:
            cores.append('background-color: #f8d7da; color: #721c24;')  # Z-4
        else:
            cores.append('')
    return cores

# --- 6. EXIBIÇÃO DA TABELA NA COLUNA DA ESQUERDA ---
with col_tabela:
    st.subheader("📊 Classificação Atualizada (GE)")
    
    if not df_tabela.empty:
        # Cards de métricas rápidas
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("🏆 Líder", f"{df_tabela.iloc[0]['nome_time']}", f"{df_tabela.iloc[0]['pontos']} pts")
        m2.metric("🛡️ Corte G-4", f"{df_tabela.iloc[3]['nome_time']}", f"{df_tabela.iloc[3]['pontos']} pts")
        m3.metric("🟡 Sul-Americana", f"{df_tabela.iloc[10]['nome_time']}", f"{df_tabela.iloc[10]['pontos']} pts")
        m4.metric("⚠️ Z-4 (17º)", f"{df_tabela.iloc[16]['nome_time']}", f"{df_tabela.iloc[16]['pontos']} pts")
        
        st.write("")
        
        st.dataframe(
            df_tabela.style.apply(colorir_zonas, axis=0).format({"aproveitamento": "{:.1f}%"}),
            use_container_width=True,
            hide_index=False,
            height=800
        )
        st.markdown("""
        **Legenda:** 
        🟢 **1º ao 4º:** Libertadores | 
        🔵 **5º:** Pré-Libertadores | 
        🟡 **6º ao 11º:** Sul-Americana | 
        🔴 **17º ao 20º:** Rebaixamento (Z-4) | 🔒 **Partida bloqueada**
        """)
