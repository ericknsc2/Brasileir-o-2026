import streamlit as st
import pandas as pd
import requests

# Configuração da página
st.set_page_config(page_title="Brasileirão 2026 - GE Ao Vivo", layout="wide")

st.title("⚽ Brasileirão 2026 - Tabela & Simulador GE Ao Vivo")

# --- 1. CAPTURA DE DADOS DA API OFICIAL DO GE ---
@st.cache_data(ttl=30)  # Atualiza automaticamente a cada 30 segundos
def buscar_dados_completos_ge(num_rodada):
    """
    Busca a tabela de classificação e os jogos da rodada selecionada direto do GE
    """
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    
    # URL da API de dados do GE (Campeonato Brasileiro)
    url_tabela = "https://api.ge.globo.com/futebol/campeonato/brasileiro-serie-a/tabela"
    url_jogos = f"https://api.ge.globo.com/futebol/campeonato/brasileiro-serie-a/rodada/{num_rodada}/jogos"
    
    df_tabela = pd.DataFrame()
    jogos_lista = []
    
    try:
        # 1.1 Tabela de Classificação
        res_tab = requests.get(url_tabela, headers=headers, timeout=5)
        if res_tab.status_code == 200:
            dados_tab = res_tab.json()
            times = []
            for item in dados_tab.get("classificacao", []):
                times.append({
                    'nome_time': item['time']['nome_popular'],
                    'pontos': item['pontos'],
                    'jogos': item['jogos'],
                    'vitorias': item['vitorias'],
                    'empates': item['empates'],
                    'derrotas': item['derrotas'],
                    'gols_pro': item['gols_pro'],
                    'gols_contra': item['gols_contra'],
                    'saldo_gols': item['saldo_gols']
                })
            df_tabela = pd.DataFrame(times)
            
        # 1.2 Jogos e Placares da Rodada
        res_jogos = requests.get(url_jogos, headers=headers, timeout=5)
        if res_jogos.status_code == 200:
            dados_jogos = res_jogos.json()
            for j in dados_jogos:
                mandante = j['equipes']['mandante']['nome_popular']
                visitante = j['equipes']['visitante']['nome_popular']
                placar_m = j.get('placar_oficial_mandante')
                placar_v = j.get('placar_oficial_visitante')
                status = j.get('status') # 'ENCERRADO', 'EM_ANDAMENTO', 'AGENDADO'
                
                data_str = j.get('data_realizacao_iso', '') # Data/Hora ISO
                hora_formatada = j.get('hora_realizacao', '')
                estadio = j.get('sede', {}).get('nome_popular', '')
                
                jogos_lista.append({
                    'mandante': mandante,
                    'visitante': visitante,
                    'placar_m': placar_m,
                    'placar_v': placar_v,
                    'status': status,
                    'hora': hora_formatada,
                    'estadio': estadio
                })
    except Exception as e:
        # Fallback local de segurança se houver oscilação de conexão
        if df_tabela.empty:
            try:
                df_tabela = pd.read_csv("Brasileirao_SQL.csv")
            except Exception:
                pass

    return df_tabela, jogos_lista

# --- 2. CONTROLE DA RODADA E SELEÇÃO DE TIME ---
c_rodada, c_time = st.columns([1, 2])
with c_rodada:
    num_rodada = st.number_input("Selecione a Rodada:", min_value=1, max_value=38, value=26)

df_base, jogos_ge = buscar_dados_completos_ge(num_rodada)

with c_time:
    lista_times = ["Nenhum"] + sorted(df_base['nome_time'].unique().tolist()) if not df_base.empty else ["Nenhum"]
    time_favorito = st.selectbox("⭐ Selecione seu time para destacar na tabela:", lista_times)

# Layout principal
col_tabela, col_simulador = st.columns([1.3, 1])

# --- 3. SIMULADOR COM DADOS DO GE ---
with col_simulador:
    st.subheader(f"🎮 Jogos da {num_rodada}ª Rodada (GE)")
    
    placares_rodada = []
    
    if jogos_ge:
        for idx, jogo in enumerate(jogos_ge):
            mandante = jogo['mandante']
            visitante = jogo['visitante']
            status = jogo['status']
            hora = jogo['hora'] if jogo['hora'] else ""
            estadio = jogo['estadio'] if jogo['estadio'] else ""
            
            # Checa se o jogo já começou ou encerrou
            jogo_bloqueado = status in ['ENCERRADO', 'EM_ANDAMENTO']
            
            val_m = jogo['placar_m'] if jogo['placar_m'] is not None else 0
            val_v = jogo['placar_v'] if jogo['placar_v'] is not None else 0
            
            # Badge visual de status
            if status == 'ENCERRADO':
                badge = "🔴 FIM"
            elif status == 'EM_ANDAMENTO':
                badge = "🟢 AO VIVO"
            else:
                badge = f"🕒 {hora}"

            st.caption(f"{estadio} • {badge}")
            
            c1, c2, c3, c4, c5 = st.columns([2.5, 1, 0.4, 1, 2.5])
            with c1:
                st.markdown(f"<div style='text-align: right;'><b>{mandante}</b></div>", unsafe_allow_html=True)
            with c2:
                gm = st.number_input(
                    "", min_value=0, value=val_m, key=f"r{num_rodada}_m_{idx}", 
                    label_visibility="collapsed", disabled=jogo_bloqueado
                )
            with c3:
                st.write("🔒" if jogo_bloqueado else "x")
            with c4:
                gv = st.number_input(
                    "", min_value=0, value=val_v, key=f"r{num_rodada}_v_{idx}", 
                    label_visibility="collapsed", disabled=jogo_bloqueado
                )
            with c5:
                st.markdown(f"<b>{visitante}</b>", unsafe_allow_html=True)
            
            placares_rodada.append((mandante, gm, gv, visitante, jogo_bloqueado))
            st.divider()
    else:
        st.info("Carregando confrontos do GE...")

# --- 4. CÁLCULO E ATUALIZAÇÃO DA TABELA ---
df_tabela = df_base.copy()

if not df_tabela.empty:
    for mandante, gm, gv, visitante, bloqueado in placares_rodada:
        # Aplica palpites do usuário para jogos não iniciados/agendados
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

    # Ordenação oficial do Brasileirão
    df_tabela = df_tabela.sort_values(by=["pontos", "vitorias", "saldo_gols", "gols_pro"], ascending=False).reset_index(drop=True)
    df_tabela.index = df_tabela.index + 1

# --- 5. COR DAS ZONAS NA TABELA ---
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

# --- 6. EXIBIÇÃO DA TABELA ---
with col_tabela:
    st.subheader("📊 Classificação em Tempo Real")
    
    if not df_tabela.empty:
        # Cards Rápidos
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
        🔴 **17º ao 20º:** Rebaixamento (Z-4) | 🔒 **Ao Vivo / Encerrado**
        """)
