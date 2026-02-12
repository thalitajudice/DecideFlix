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
    st.subheader("🎲 Sorteio de Filmes")

    # Opção para escolher o tipo de sorteio
    tipo_sorteio = st.radio(
        "Como você quer sortear?",
        ("Sortear qualquer um", "Sortear por Categoria")
    )

    if tipo_sorteio == "Sortear qualquer um":
        if st.button("Sortear Agora"):
            try:
                response = requests.get(f"{API_URL}/titulos/sortear")
                if response.status_code == 200:
                    filme = response.json()
                    st.success(f"🍿 O vencedor é: **{filme['nome']}** ({filme['ano']})")
                    st.info(f"Categoria: {filme['categoria']}")
                else:
                    st.error("Nenhum filme encontrado no banco de dados.")
            except:
                st.error("Erro de conexão com a API.")

    elif tipo_sorteio == "Sortear por Categoria":
        # 1. Busca as categorias existentes para preencher a caixinha
        try:
            resp_cat = requests.get(f"{API_URL}/titulos/quantidade-por-categoria")
            if resp_cat.status_code == 200:
                dados_cat = resp_cat.json()
                # Cria uma lista só com os nomes das categorias
                lista_categorias = [item['categoria'] for item in dados_cat]
                
                # 2. Mostra a caixa de seleção
                categoria_escolhida = st.selectbox("Escolha a categoria:", lista_categorias)

                # 3. Botão de sortear específico
                if st.button(f"Sortear filme de {categoria_escolhida}"):
                    response = requests.get(f"{API_URL}/titulos/sortear/categoria/{categoria_escolhida}")
                    
                    if response.status_code == 200:
                        filme = response.json()
                        st.success(f"🍿 O vencedor de {categoria_escolhida} é: **{filme['nome']}** ({filme['ano']})")
                    else:
                        st.warning(f"Não consegui sortear. Talvez não tenha filmes de {categoria_escolhida}?")
            else:
                st.error("Erro ao carregar categorias.")
        except:
            st.error("Erro de conexão ao buscar categorias.")

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
