import streamlit as st
import requests

API_URL = "http://127.0.0.1:5000"

st.title("🎬 DecideFlix")

menu = st.sidebar.selectbox(
    "Menu",
    ["Listar Filmes", "Adicionar Filme", "Sortear Filme", "Analytics"]
)

# ----------------------------
# LISTAR
# ----------------------------
if menu == "Listar Filmes":
    st.subheader("Lista de Filmes")

    response = requests.get(f"{API_URL}/titulos")

    if response.status_code == 200:
        filmes = response.json()
        for filme in filmes:
            st.write(f"{filme['nome']} ({filme['ano']}) - {filme['categoria']}")
    else:
        st.error("Erro ao buscar filmes")

# ----------------------------
# ADICIONAR
# ----------------------------
elif menu == "Adicionar Filme":
    st.subheader("Adicionar Novo Filme")

    titulo = st.text_input("Título")
    categoria = st.text_input("Categoria")
    ano = st.number_input("Ano", min_value=1900, max_value=2100)

    if st.button("Adicionar"):
        data = {
            "titulo": titulo,
            "categoria": categoria,
            "ano": ano
        }

        response = requests.post("http://127.0.0.1:5000/titulos", json=data)

        if response.status_code == 201:
            st.success("Filme adicionado com sucesso")
        else:
            st.error("Erro ao adicionar filme")

# ----------------------------
# SORTEAR
# ----------------------------
elif menu == "Sortear Filme":
    st.subheader("🎲 Sorteio")

    if st.button("Sortear agora"):
        response = requests.get(f"{API_URL}/titulos/sortear")

        if response.status_code == 200:
            filme = response.json()
            st.success(f"{filme['nome']} ({filme['ano']})")
            st.write(f"Categoria: {filme['categoria']}")
        else:
            st.error("Nenhum filme encontrado")

# ----------------------------
# ANALYTICS
# ----------------------------
elif menu == "Analytics":
    st.subheader("Quantidade por Categoria")

    response = requests.get(f"{API_URL}/titulos/quantidade-por-categoria")

    if response.status_code == 200:
        dados = response.json()
        for item in dados:
            st.write(f"{item['categoria']}: {item['quantidade_filmes']}")
