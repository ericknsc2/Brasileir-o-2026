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
    "Mirassol": "data:image/png;base64,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",
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
