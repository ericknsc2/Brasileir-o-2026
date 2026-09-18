import pandas as pd
import streamlit as st

# Configuração da página
st.set_page_config(
    page_title="Simulador Brasileirão 2026", page_icon="⚽", layout="wide"
)

# Título principal
st.title("⚽ Simulador e Painel do Brasileirão 2026")
st.markdown(
    "Acompanhe e simule os resultados dos jogos do Campeonato Brasileiro de 2026!"
)

# Dados iniciais simulados para os 20 clubes do Brasileirão 2026
@st.cache_data
def carregar_dados():
  clubes = [
      "Flamengo",
      "Fluminense",
      "Botafogo",
      "Vasco da Gama",
      "Palmeiras",
      "São Paulo",
      "Corinthians",
      "Santos",
      "Atlético-MG",
      "Cruzeiro",
      "Grêmio",
      "Internacional",
      "Bahia",
      "Vitória",
      "Fortaleza",
      "Ceará",
      "Athletico-PR",
      "Coritiba",
      "Sport",
      "Juventude",
  ]

  # Criando um DataFrame base para a tabela de classificação
  tabela = pd.DataFrame({
      "Clube": clubes,
      "P": [0] * 20,  # Pontos
      "J": [0] * 20,  # Jogos
      "V": [0] * 20,  # Vitórias
      "E": [0] * 20,  # Empates
      "D": [0] * 20,  # Derrotas
      "GP": [0] * 20,  # Gols Pró
      "GC": [0] * 20,  # Gols Contra
      "SG": [0] * 20,  # Saldo de Gols
  })
  return tabela


if "tabela_classificacao" not in st.session_state:
  st.session_state.tabela_classificacao = carregar_dados()

# Barra lateral para navegação
st.sidebar.header("Navegação")
opcao = st.sidebar.selectbox(
    "Escolha a seção", ["Tabela de Classificação", "Simulador de Partidas"]
)

# Ordenação da tabela (Pontos, Vitórias, Saldo de Gols, Gols Pró)
def atualizar_tabela(df):
  df["SG"] = df["GP"] - df["GC"]
  df = df.sort_values(
      by=["P", "V", "SG", "GP"], ascending=[False, False, False, False]
  ).reset_index(drop=True)
  return df


if opcao == "Tabela de Classificação":
  st.subheader("📊 Tabela de Classificação Atualizada")
  tabela_atual = atualizar_tabela(st.session_state.tabela_classificacao)

  # Adicionando formatação visual para zonas de classificação (Libertadores, Sul-Americana, Rebaixamento)
  def colorir_tabela(val):
    # Apenas para estilizar o index ou posições se necessário
    return ""

  st.dataframe(tabela_atual, use_container_width=True)

  st.markdown("### Legenda:")
  st.markdown("🟢 **Pré-Libertadores / Grupos:** 1º ao 6º colocado")
  st.markdown("🔵 **Sul-Americana:** 7º ao 12º colocado")
  st.markdown("🔴 **Rebaixamento (Série B):** 17º ao 20º colocado")

elif opcao == "Simulador de Partidas":
  st.subheader("⚡ Simulador de Resultados")
  st.markdown("Insira os gols da partida para atualizar a tabela instantaneamente.")

  col1, col2, col3 = st.columns([3, 1, 3])

  clubes_lista = list(st.session_state.tabela_classificacao["Clube"])

  with col1:
    mandante = st.selectbox("Mandante", clubes_lista, index=0)
    gols_mandante = st.number_input(
        "Gols Mandante", min_value=0, max_value=20, value=0, step=1
    )

  with col2:
    st.markdown("### X")

  with col3:
    # Selecionar um visitante diferente do mandante por padrão se possível
    visitante_index = 1 if len(clubes_lista) > 1 else 0
    visitante = st.selectbox("Visitante", clubes_lista, index=visitante_index)
    gols_visitante = st.number_input(
        "Gols Visitante", min_value=0, max_value=20, value=0, step=1
    )

  if st.button("Registrar Partida e Atualizar Tabela", type="primary"):
    if mandante == visitante:
      st.error("O time mandante e o visitante não podem ser os mesmos!")
    else:
      df = st.session_state.tabela_classificacao

      # Atualiza estatísticas do Mandante
      idx_m = df.index[df["Clube"] == mandante][0]
      df.loc[idx_m, "J"] += 1
      df.loc[idx_m, "GP"] += gols_mandante
      df.loc[idx_m, "GC"] += gols_visitante

      # Atualiza estatísticas do Visitante
      idx_v = df.index[df["Clube"] == visitante][0]
      df.loc[idx_v, "J"] += 1
      df.loc[idx_v, "GP"] += gols_visitante
      df.loc[idx_v, "GC"] += gols_mandante

      # Atribuição de pontos, vitórias, empates e derrotas
      if gols_mandante > gols_visitante:
        df.loc[idx_m, "P"] += 3
        df.loc[idx_m, "V"] += 1
        df.loc[idx_v, "D"] += 1
      elif gols_mandante < gols_visitante:
        df.loc[idx_v, "P"] += 3
        df.loc[idx_v, "V"] += 1
        df.loc[idx_m, "D"] += 1
      else:
        df.loc[idx_m, "P"] += 1
        df.loc[idx_m, "E"] += 1
        df.loc[idx_v, "P"] += 1
        df.loc[idx_v, "E"] += 1

      st.session_state.tabela_classificacao = df
      st.success(
          f"Partida registrada com sucesso! {mandante} {gols_mandante} x"
          f" {gols_visitante} {visitante}"
      )

      # Mostra a tabela prévia atualizada logo abaixo
      st.dataframe(atualizar_tabela(df), use_container_width=True)
