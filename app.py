import streamlit as st
import pandas as pd
import requests

# Configuração da página - Layout Wide
st.set_page_config(page_title="Brasileirão 2026", layout="wide", initial_sidebar_state="collapsed")

# --- CSS PARA ELEVAR O CABEÇALHO E OTIMIZAR ESPAÇAMENTOS ---
st.markdown("""
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
""", unsafe_allow_html=True)

st.title("⚽ Brasileirão 2026")

# --- Inicialização da Session State ---
if "palpites_confirmados" not in st.session_state:
    st.session_state.palpites_confirmados = {}

# Jogo já encerrado: Coritiba 3 x 3 Athletico-PR
if "jogos_encerrados" not in st.session_state:
    st.session_state.jogos_encerrados = {
        "CoritibaXAthletico-PR": (3, 3)
    }
else:
    st.session_state.jogos_encerrados["CoritibaXAthletico-PR"] = (3, 3)

# ESCUDOS COM OPÇÕES ROBUSTAS (Mirassol e Remo ajustados para links diretos de alta compatibilidade)
ESCUDOS_TIMES = {
    "Flamengo": "https://a.espncdn.com/i/teamlogos/soccer/500/819.png",
    "Palmeiras": "https://s.sde.globo.com/media/organizations/2019/07/06/Palmeiras.svg",
    "Athletico-PR": "https://s.sde.globo.com/media/organizations/2019/09/09/Athletico-PR.svg",
    "Fluminense": "https://s.sde.globo.com/media/organizations/2018/03/11/fluminense.svg",
    "Bahia": "https://s.sde.globo.com/media/organizations/2018/03/11/bahia.svg",
    "Cruzeiro": "https://s.sde.globo.com/media/organizations/2021/02/13/cruzeiro_2021.svg",
    "Coritiba": "https://s.sde.globo.com/media/organizations/2018/03/11/coritiba.svg",
    "Atlético-MG": "https://s.sde.globo.com/media/organizations/2018/03/10/atletico-mg.svg",
    "Red Bull Bragantino": "https://a.espncdn.com/i/teamlogos/soccer/500/6079.png",
    "São Paulo": "https://s.sde.globo.com/media/organizations/2018/03/11/sao-paulo.svg",
    "Vitória": "https://a.espncdn.com/i/teamlogos/soccer/500/3456.png",
    "Corinthians": "https://s.sde.globo.com/media/organizations/2019/09/30/Corinthians.svg",
    "Santos": "https://s.sde.globo.com/media/organizations/2018/03/12/santos.svg",
    "Botafogo": "https://s.sde.globo.com/media/organizations/2019/02/04/botafogo-svg.svg",
    "Grêmio": "https://s.sde.globo.com/media/organizations/2018/03/12/gremio.svg",
    "Mirassol": "https://logodetimes.com/wp-content/uploads/mirassol-futebol-clube.png",
    "Vasco": "https://a.espncdn.com/i/teamlogos/soccer/500/3454.png",
    "Internacional": "https://s.sde.globo.com/media/organizations/2018/03/11/internacional.svg",
    "Remo": "https://logodetimes.com/wp-content/uploads/remo-brasao.png",
    "Chapecoense": "https://s.sde.globo.com/media/organizations/2018/03/11/chapecoense.svg"
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
    "Botafogo-RJ": "Botafogo",
    "Grêmio RS": "Grêmio",
    "Gremio": "Grêmio"
}

def normalizar_nome(nome):
    return MAPEAMENTO_TIMES_ESPN.get(nome, nome)

def obter_escudo(nome):
    nome_padrao = normalizar_nome(nome)
    return ESCUDOS_TIMES.get(nome_padrao, "https://s.sde.globo.com/media/organizations/2018/03/11/fluminense.svg")

# --- DADOS DA TABELA BASE OFICIAL ---
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
        {"nome_time": "Vitória", "pontos": 32, "jogos": 26, "vitorias": 9, "empates": 5, "derrotas": 12, "gols_pro": 25, "gols_contra": 37},
        {"nome_time": "Corinthians", "pontos": 32, "jogos": 26, "vitorias": 8, "empates": 8, "derrotas": 10, "gols_pro": 27, "gols_contra": 27},
        {"nome_time": "Santos", "pontos": 32, "jogos": 25, "vitorias": 8, "empates": 8, "derrotas": 9, "gols_pro": 37, "gols_contra": 38},
        {"nome_time": "Botafogo", "pontos": 31, "jogos": 25, "vitorias": 8, "empates": 7, "derrotas": 10, "gols_pro": 37, "gols_contra": 40},
        {"nome_time": "Grêmio", "pontos": 28, "jogos": 25, "vitorias": 7, "empates": 7, "derrotas": 11, "gols_pro": 27, "gols_contra": 33},
        {"nome_time": "Mirassol", "pontos": 28, "jogos": 26, "vitorias": 7, "empates": 7, "derrotas": 12, "gols_pro": 29, "gols_contra": 40},
        {"nome_time": "Vasco", "pontos": 25, "jogos": 25, "vitorias": 6, "empates": 7, "derrotas": 12, "gols_pro": 27, "gols_contra": 40},
        {"nome_time": "Internacional", "pontos": 25, "jogos": 26, "vitorias": 5, "empates": 10, "derrotas": 11, "gols_pro": 28, "gols_contra": 34},
        {"nome_time": "Remo", "pontos": 23, "jogos": 26, "vitorias": 5, "empates": 8, "derrotas": 13, "gols_pro": 30, "gols_contra": 43},
        {"nome_time": "Chapecoense", "pontos": 17, "jogos": 25, "vitorias": 3, "empates": 8, "derrotas": 14, "gols_pro": 27, "gols_contra": 50}
    ]
    df = pd.DataFrame(dados_tabela)
    df['saldo_gols'] = df['gols_pro'] - df['gols_contra']
    df['pos_inicial'] = df.index + 1
    return df

# API ESPN
def buscar_jogos_espn():
    url = "https://site.api.espn.com/apis/site/v2/sports/soccer/bra.1/scoreboard"
    try:
        res = requests.get(url, timeout=3)
        if res.status_code == 200:
            dados = res.json()
            eventos = dados.get('events', [])
            jogos = {}
            for ev in eventos:
                comp = ev['competitions'][0]
                m_nome = normalizar_nome(comp['competitors'][0]['team']['shortDisplayName'])
                v_nome = normalizar_nome(comp['competitors'][1]['team']['shortDisplayName'])
                
                m_score = int(comp['competitors'][0]['score']) if 'score' in comp['competitors'][0] else 0
                v_score = int(comp['competitors'][1]['score']) if 'score' in comp['competitors'][1] else 0
                
                state = ev['status']['type']['state']
                detail = ev['status']['type']['shortDetail']
                
                chave = f"{m_nome}X{v_nome}"
                jogos[chave] = {'gm': m_score, 'gv': v_score, 'state': state, 'detail': detail}
                
                if state == 'post':
                    st.session_state.jogos_encerrados[chave] = (m_score, v_score)
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

# --- CÁLCULO REATIVO DA TABELA ---
df_simulado = df_base.copy()

for r_num, lista_jogos in CALENDARIO_RODADAS.items():
    for idx, (mandante, visitante, _) in enumerate(lista_jogos):
        chave_live = f"{mandante}X{visitante}"
        chave_sim = f"sim_r{r_num}_{idx}"
        
        jogou = False
        gm, gv = 0, 0
        
        if chave_live in st.session_state.jogos_encerrados:
            gm, gv = st.session_state.jogos_encerrados[chave_live]
            jogou = True
        elif chave_live in placar_live and placar_live[chave_live]['state'] in ['in', 'post']:
            gm = placar_live[chave_live]['gm']
            gv = placar_live[chave_live]['gv']
            jogou = True
        elif chave_sim in st.session_state.palpites_confirmados:
            gm, gv = st.session_state.palpites_confirmados[chave_sim]
            jogou = True

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
df_simulado['pos_atual'] = df_simulado.index + 1

def calcular_variacao(row):
    diff = row['pos_inicial'] - row['pos_atual']
    if diff > 0:
        return f"🟢 ⬆️ +{diff}"
    elif diff < 0:
        return f"🔴 ⬇️ {diff}"
    else:
        return "➖"

df_simulado['var'] = df_simulado.apply(calcular_variacao, axis=1)
df_simulado['escudo'] = df_simulado['nome_time'].apply(obter_escudo)

mapa_variacoes = dict(zip(df_simulado['nome_time'], df_simulado['var']))

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

# --- ABAS ---
tab_tabela, tab_simulador, tab_aovivo = st.tabs(["📊 Classificação", "🎮 Simulador", "🔴 Ao Vivo"])

confrontos_rodada_atual = CALENDARIO_RODADAS.get(num_rodada, [])

# ABA 1: CLASSIFICAÇÃO
with tab_tabela:
    if not df_simulado.empty:
        m1, m2 = st.columns(2)
        m1.metric("🏆 Líder", f"{df_simulado.iloc[0]['nome_time']}", f"{df_simulado.iloc[0]['pontos']} pts")
        m2.metric("🛡️ G-4", f"{df_simulado.iloc[3]['nome_time']}", f"{df_simulado.iloc[3]['pontos']} pts")
        
        cols_exibir = ['escudo', 'nome_time', 'pontos', 'jogos', 'vitorias', 'empates', 'derrotas', 'gols_pro', 'gols_contra', 'saldo_gols', 'aproveitamento']
        
        df_exibir = df_simulado[cols_exibir].copy()
        df_exibir['nome_time'] = df_simulado['nome_time'] + " " + df_simulado['var']
        df_exibir.index = df_simulado['pos_atual']
        
        st.dataframe(
            df_exibir.style.apply(colorir_zonas, axis=0).format({"aproveitamento": "{:.1f}%"}),
            column_config={
                "escudo": st.column_config.ImageColumn("Escudo", help="Escudo do clube", width="small"),
                "nome_time": st.column_config.TextColumn("Clube"),
            },
            use_container_width=True,
            hide_index=False,
            height=820
        )
        st.caption("🟢 G-4 | 🔵 Pré-Libertadores | 🟡 Sul-Americana | 🔴 Z-4")

# ABA 2: SIMULADOR
with tab_simulador:
    st.subheader(f"🎮 Palpites para a {num_rodada}ª Rodada")
    
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("🧮 Calcular Todos os Palpites"):
            for idx in range(len(confrontos_rodada_atual)):
                key_m = f"input_r{num_rodada}_m_{idx}"
                key_v = f"input_r{num_rodada}_v_{idx}"
                if key_m in st.session_state and key_v in st.session_state:
                    gm = st.session_state[key_m]
                    gv = st.session_state[key_v]
                    if gm is not None and gv is not None:
                        st.session_state.palpites_confirmados[f"sim_r{num_rodada}_{idx}"] = (gm, gv)
            st.rerun()
            
    with col_btn2:
        if st.button("🧹 Limpar Meus Palpites"):
            st.session_state.palpites_confirmados.clear()
            for idx in range(len(confrontos_rodada_atual)):
                st.session_state[f"input_r{num_rodada}_m_{idx}"] = None
                st.session_state[f"input_r{num_rodada}_v_{idx}"] = None
            st.rerun()

    st.write("")

    for idx, (mandante, visitante, data_hora_str) in enumerate(confrontos_rodada_atual):
        chave_live = f"{mandante}X{visitante}"
        chave_sim = f"sim_r{num_rodada}_{idx}"
        
        jogo_bloqueado = False
        val_m, val_v = None, None
        
        if chave_live in st.session_state.jogos_encerrados:
            val_m, val_v = st.session_state.jogos_encerrados[chave_live]
            jogo_bloqueado = True
            badge_sim = "🔴 FIM DE JOGO (Placar Real)"
        elif chave_live in placar_live and placar_live[chave_live]['state'] in ['in', 'post']:
            val_m = placar_live[chave_live]['gm']
            val_v = placar_live[chave_live]['gv']
            jogo_bloqueado = True
            badge_sim = f"🟢 EM ANDAMENTO / FINALIZADO ({placar_live[chave_live]['detail']})"
        else:
            badge_sim = f"📅 {data_hora_str}"
            if chave_sim in st.session_state.palpites_confirmados:
                val_m, val_v = st.session_state.palpites_confirmados[chave_sim]

        st.markdown(f"<div class='status-badge'>{badge_sim}</div>", unsafe_allow_html=True)
        
        c_nm, c_im, c_pm, c_x, c_pv, c_iv, c_nv, c_btn = st.columns([1.8, 0.4, 0.9, 0.2, 0.9, 0.4, 1.8, 1.2])
        
        with c_nm:
            st.markdown(f"<div style='text-align: right; font-weight: bold;'>{mandante}</div>", unsafe_allow_html=True)
        with c_im:
            st.image(obter_escudo(mandante), width=24)
        with c_pm:
            gm_val = st.number_input(
                "", min_value=0, key=f"input_r{num_rodada}_m_{idx}", 
                label_visibility="collapsed", value=val_m, placeholder="-",
                disabled=jogo_bloqueado
            )
        with c_x:
            st.markdown("<div style='text-align: center; font-weight: bold;'>x</div>", unsafe_allow_html=True)
        with c_pv:
            gv_val = st.number_input(
                "", min_value=0, key=f"input_r{num_rodada}_v_{idx}", 
                label_visibility="collapsed", value=val_v, placeholder="-",
                disabled=jogo_bloqueado
            )
        with c_iv:
            st.image(obter_escudo(visitante), width=24)
        with c_nv:
            st.markdown(f"<div style='text-align: left; font-weight: bold;'>{visitante}</div>", unsafe_allow_html=True)
        with c_btn:
            if not jogo_bloqueado:
                if st.button("🧮 Calcular", key=f"btn_calc_{idx}"):
                    if gm_val is not None and gv_val is not None:
                        st.session_state.palpites_confirmados[chave_sim] = (gm_val, gv_val)
                        st.rerun()
            else:
                st.caption("🔒 Encerrado")
            
        st.divider()

# ABA 3: AO VIVO
with tab_aovivo:
    @st.fragment(run_every=30)
    def renderizar_painel_ao_vivo():
        c_tit, c_btn = st.columns([2, 1])
        with c_tit:
            st.subheader(f"🔴 Central Ao Vivo - {num_rodada}ª Rodada")
        with c_btn:
            if st.button("🔄 Atualizar Agora"):
                st.cache_data.clear()
                st.rerun()

        placar_tempo_real = buscar_jogos_espn()

        for idx, (mandante, visitante, data_hora_str) in enumerate(confrontos_rodada_atual):
            chave_live = f"{mandante}X{visitante}"
            
            var_m = mapa_variacoes.get(mandante, "➖")
            var_v = mapa_variacoes.get(visitante, "➖")
            
            if chave_live in st.session_state.jogos_encerrados:
                badge = "🔴 FIM DE JOGO"
                p_m, p_v = st.session_state.jogos_encerrados[chave_live]
            elif chave_live in placar_tempo_real:
                st_info = placar_tempo_real[chave_live]
                if st_info['state'] == 'in':
                    badge = f"🟢 AO VIVO ({st_info['detail']})"
                    p_m, p_v = st_info['gm'], st_info['gv']
                elif st_info['state'] == 'post':
                    badge = "🔴 FIM DE JOGO"
                    p_m, p_v = st_info['gm'], st_info['gv']
                else:
                    badge = f"🕒 AGENDADO - {data_hora_str}"
                    p_m, p_v = "-", "-"
            else:
                badge = f"🕒 AGENDADO - {data_hora_str}"
                p_m, p_v = "-", "-"

            st.markdown(f"<div class='status-badge'>{badge}</div>", unsafe_allow_html=True)
            
            c_nm, c_im, c_pm, c_x, c_pv, c_iv, c_nv = st.columns([2, 0.4, 0.8, 0.3, 0.8, 0.4, 2])
            with c_nm:
                st.markdown(f"<div style='text-align: right; font-weight: bold;'>{mandante} <small style='color:#777;'>({var_m})</small></div>", unsafe_allow_html=True)
            with c_im:
                st.image(obter_escudo(mandante), width=24)
            with c_pm:
                st.markdown(f"<h3 style='text-align: center; margin: 0;'>{p_m}</h3>", unsafe_allow_html=True)
            with c_x:
                st.markdown("<div style='text-align: center; font-weight: bold;'>x</div>", unsafe_allow_html=True)
            with c_pv:
                st.markdown(f"<h3 style='text-align: center; margin: 0;'>{p_v}</h3>", unsafe_allow_html=True)
            with c_iv:
                st.image(obter_escudo(visitante), width=24)
            with c_nv:
                st.markdown(f"<div style='text-align: left; font-weight: bold;'>{visitante} <small style='color:#777;'>({var_v})</small></div>", unsafe_allow_html=True)
                
            st.divider()

    renderizar_painel_ao_vivo()
