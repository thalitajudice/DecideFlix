import streamlit as st
import requests

API_URL = "http://127.0.0.1:5000"

st.title("🎬 DecideFlix")

menu = st.sidebar.selectbox(
    "Menu",
    ["Listar Filmes", "Adicionar Filme", "Buscar (Índices)", "Sortear Filme", "Analytics"]
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
# BUSCAS (ÍNDICES)
# ----------------------------
elif menu == "Buscar (Índices)":
    st.subheader("🔎 Busca Otimizada com Índices")
    
    # Abas (Tabs) para deixar a interface bonita e organizada
    aba_simples, aba_texto, aba_geo = st.tabs(["Simples (Categoria)", "Texto (Nome)", "Geoespacial (Mapa)"])
    
    # --- ABA 1: ÍNDICE SIMPLES ---
    with aba_simples:
        st.info("Utiliza o índice ASCENDING no campo 'categoria'. O banco vai direto na 'letra' certa.")
        categoria = st.text_input("Digite a categoria (ex: Ação, Drama, Animação):")
        
        if st.button("Buscar por Categoria"):
            response = requests.get(f"{API_URL}/busca/simples?categoria={categoria}")
            if response.status_code == 200:
                dados = response.json()
                st.success(f"Encontrados {dados['quantidade']} filmes!")
                for f in dados['resultados']:
                    st.write(f"- **{f['nome']}** ({f['categoria']})")
            else:
                st.error("Erro na busca. Verifique se a API está rodando.")

    # --- ABA 2: ÍNDICE DE TEXTO ---
    with aba_texto:
        st.info("Utiliza o índice TEXT no campo 'nome'. Busca palavras dentro do texto e ordena por relevância.")
        termo = st.text_input("Digite uma palavra do título (ex: Senhor, Volta, Matrix):")
        
        if st.button("Buscar por Texto"):
            response = requests.get(f"{API_URL}/busca/texto?q={termo}")
            if response.status_code == 200:
                dados = response.json()
                st.success(f"Encontrados {dados['quantidade']} filmes!")
                for f in dados['resultados']:
                    st.write(f"- **{f['nome']}** (Relevância: {f['score_relevancia']:.2f})")
            else:
                st.error("Erro na busca.")

    # --- ABA 3: ÍNDICE GEOESPACIAL ---
    with aba_geo:
        st.info("Utiliza o índice GEOSPHERE com operador $near. Encontra filmes gravados em um raio de distância!")
        
        # Coordenadas de Uberlândia como padrão para facilitar o teste
        col1, col2, col3 = st.columns(3)
        with col1:
            lat = st.number_input("Latitude", value=-18.9186, format="%.4f")
        with col2:
            lng = st.number_input("Longitude", value=-48.2772, format="%.4f")
        with col3:
            dist = st.number_input("Distância (Metros)", value=500000, step=50000) # Padrão: 500km
            
        if st.button("Buscar por Proximidade"):
            response = requests.get(f"{API_URL}/busca/geo?lat={lat}&lng={lng}&dist={dist}")
            if response.status_code == 200:
                dados = response.json()
                st.success(f"Encontrados {dados['quantidade']} filmes num raio de {dist/1000}km!")
                for f in dados['resultados']:
                    st.write(f"- **{f['nome']}**")
                    st.caption(f"Coordenadas: {f['coordenadas']}")
            else:
                st.error("Erro na busca.")

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
                lista_categorias = [item['categoria'] for item in dados_cat]
                
                # 2. Mostra a caixa de seleção COM UMA KEY PARA SALVAR O ESTADO
                categoria_escolhida = st.selectbox(
                    "Escolha a categoria:", 
                    lista_categorias, 
                    key="caixa_categoria_sorteio"
                )

                # 3. Botão com NOME FIXO
                if st.button("🎲 Sortear Filme Desta Categoria"):
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
    st.subheader("📊 Analytics do DecideFlix")

    # Criamos duas abas para organizar os dados
    aba_categoria, aba_decada = st.tabs(["Por Categoria", "Por Década"])

    # --- ABA 1: Por Categoria ---
    with aba_categoria:
        response = requests.get(f"{API_URL}/titulos/quantidade-por-categoria")
        if response.status_code == 200:
            dados = response.json()
            for item in dados:
                st.write(f"**{item['categoria']}**: {item['quantidade_filmes']} filme(s)")
                
                # Junta os nomes da lista com vírgulas e exibe em texto menor
                nomes_filmes = ", ".join(item['filmes'])
                st.caption(f"Filmes: {nomes_filmes}")

    # --- ABA 2: Usando a matemática das Décadas ---
    with aba_decada:
        st.info("O banco de dados (MongoDB) calcula a década matematicamente e agrupa os filmes!")
        response_decada = requests.get(f"{API_URL}/titulos/decadas")
        
        if response_decada.status_code == 200:
            dados_decada = response_decada.json()
            for item in dados_decada:
                # O int() é só para garantir que apareça "1990" e não "1990.0"
                st.write(f"📼 **Anos {int(item['decada'])}**: {item['quantidade_filmes']} filme(s)")
                
                # Mostra o nome dos filmes que pertencem a essa década
                nomes = [f"{filme['nome']} ({filme['ano']})" for filme in item['filmes']]
                st.caption(f"Filmes: {', '.join(nomes)}")
