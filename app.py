from flask import Flask, request, jsonify
from pymongo import MongoClient, ASCENDING, TEXT, GEOSPHERE
from bson import ObjectId
from bson.errors import InvalidId
from dotenv import load_dotenv
import os

app = Flask(__name__)

load_dotenv()

mongo_uri = os.getenv("MONGO_URI")

if not mongo_uri:
    raise RuntimeError("MONGO_URI não definida no .env")

client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)

try:
    client.admin.command("ping")
    print("MongoDB Atlas conectado com sucesso")
except Exception as e:
    raise RuntimeError(f"Erro ao conectar no MongoDB: {e}")

db = client["decideflix"]
colecao_titulos = db["titulos"]


# =========================
# INDICES
# =========================


@app.route("/indices/criar", methods=["POST"])
def criar_indices():
    try:
        # 1. Índice Simples (Campo: categoria, Ordem: Crescente)
        colecao_titulos.create_index([("categoria", ASCENDING)])
        
        # 2. Índice de Texto (Campo: nome) - Permite busca por palavras
        colecao_titulos.create_index([("nome", TEXT)])
        
        # 3. Índice Geoespacial (Campo: localizacao) - Permite busca por mapa/distância
        colecao_titulos.create_index([("localizacao", GEOSPHERE)])
        
        return jsonify({"mensagem": "Todos os índices foram criados com sucesso no MongoDB!"}), 201
    except Exception as e:
        return jsonify({"erro": f"Falha ao criar índices: {e}"}), 500

# === 1. TESTANDO O ÍNDICE SIMPLES ===
@app.route("/busca/simples", methods=["GET"])
def testar_indice_simples():
    # Pega a categoria que o usuário digitar na URL
    categoria_buscada = request.args.get("categoria")
    
    if not categoria_buscada:
        return jsonify({"erro": "Envie a categoria. Ex: /busca/simples?categoria=Ação"}), 400

    # O MongoDB percebe sozinho que existe um índice em 'categoria' e usa ele
    filmes = list(colecao_titulos.find({"categoria": categoria_buscada}))
    
    # Formatando a resposta igual você já faz no seu código
    resposta = [{"id": str(f["_id"]), "nome": f["nome"], "categoria": f["categoria"]} for f in filmes]
    
    return jsonify({"quantidade": len(resposta), "resultados": resposta})


# === 2. TESTANDO O ÍNDICE DE TEXTO ===
@app.route("/busca/texto", methods=["GET"])
def testar_indice_texto():
    # Pega a palavra que o usuário quer pesquisar na URL
    termo = request.args.get("q")
    
    if not termo:
        return jsonify({"erro": "Envie o termo. Ex: /busca/texto?q=Matrix"}), 400

    # O operador $text só funciona porque criamos o índice TEXT no campo 'nome'
    filmes = list(colecao_titulos.find(
        {"$text": {"$search": termo}},
        {"score": {"$meta": "textScore"}} # Isso traz uma nota de relevância da pesquisa
    ).sort([("score", {"$meta": "textScore"})])) # Ordena do mais relevante para o menos
    
    resposta = [{"id": str(f["_id"]), "nome": f["nome"], "score_relevancia": f.get("score")} for f in filmes]
    
    return jsonify({"quantidade": len(resposta), "resultados": resposta})


# === 3. TESTANDO O ÍNDICE GEOESPACIAL 2D ===
@app.route("/busca/geo", methods=["GET"])
def testar_indice_geo():
    try:
        # Pega a latitude, longitude e a distância máxima (em metros) da URL
        lat = float(request.args.get("lat"))
        lng = float(request.args.get("lng"))
        distancia = int(request.args.get("dist", 500000)) # Padrão: 500.000 metros (500km)
    except (TypeError, ValueError):
        return jsonify({"erro": "Envie lat e lng. Ex: /busca/geo?lat=-23.55&lng=-46.63"}), 400

    

    # O operador $near traça um raio a partir do ponto e acha o que tem dentro
    query = {
        "localizacao": {
            "$near": {
                "$geometry": {
                    "type": "Point",
                    "coordinates": [lng, lat] # ATENÇÃO: MongoDB usa Longitude primeiro, depois Latitude
                },
                "$maxDistance": distancia
            }
        }
    }

    filmes = list(colecao_titulos.find(query))
    
    resposta = [{
        "id": str(f["_id"]), 
        "nome": f["nome"], 
        "coordenadas": f["localizacao"]["coordinates"]
    } for f in filmes]
    
    return jsonify({"quantidade": len(resposta), "resultados": resposta})

@app.route("/")
def home():
    return "API DecideFlix funcionando"


# =========================
# CRUD
# =========================

@app.route("/titulos", methods=["GET"])
def listar_titulos():
    lista = []
    for titulo in colecao_titulos.find():
        lista.append({
            "id": str(titulo["_id"]),
            "nome": titulo.get("nome"),
            "categoria": titulo.get("categoria"),
            "ano": titulo.get("ano")
        })
    return jsonify(lista)


@app.route("/titulos", methods=["POST"])
def criar_titulo():
    dados = request.json

    novo_titulo = {
        "nome": dados["nome"],
        "categoria": dados["categoria"],
        "ano": dados["ano"]
    }

    resultado = colecao_titulos.insert_one(novo_titulo)

    return jsonify({
        "mensagem": "Título inserido com sucesso!",
        "id": str(resultado.inserted_id)
    }), 201


@app.route("/titulos/lote", methods=["POST"])
def criar_titulos_em_lote():
    dados = request.json

    if not isinstance(dados, list) or len(dados) == 0:
        return jsonify({"erro": "Envie uma lista de títulos"}), 400

    resultado = colecao_titulos.insert_many(dados)

    return jsonify({
        "mensagem": f"{len(resultado.inserted_ids)} títulos inseridos com sucesso"
    }), 201


@app.route("/titulos/<id>", methods=["GET"])
def buscar_titulo(id):
    try:
        oid = ObjectId(id)
    except InvalidId:
        return jsonify({"erro": "ID inválido"}), 400

    titulo = colecao_titulos.find_one({"_id": oid})

    if not titulo:
        return jsonify({"erro": "Título não encontrado"}), 404

    return jsonify({
        "id": str(titulo["_id"]),
        "nome": titulo.get("nome"),
        "categoria": titulo.get("categoria"),
        "ano": titulo.get("ano")
    })


@app.route("/titulos/<id>", methods=["PUT"])
def atualizar_titulo(id):
    try:
        oid = ObjectId(id)
    except InvalidId:
        return jsonify({"erro": "ID inválido"}), 400

    dados = request.json

    resultado = colecao_titulos.update_one(
        {"_id": oid},
        {"$set": {
            "nome": dados["nome"],
            "categoria": dados["categoria"],
            "ano": dados["ano"]
        }}
    )

    if resultado.matched_count == 0:
        return jsonify({"erro": "Título não encontrado"}), 404

    return jsonify({"mensagem": "Título atualizado com sucesso"})


@app.route("/titulos/<id>", methods=["DELETE"])
def deletar_titulo(id):
    try:
        oid = ObjectId(id)
    except InvalidId:
        return jsonify({"erro": "ID inválido"}), 400

    resultado = colecao_titulos.delete_one({"_id": oid})

    if resultado.deleted_count == 0:
        return jsonify({"erro": "Título não encontrado"}), 404

    return jsonify({"mensagem": "Título removido com sucesso"})

@app.route("/titulos/limpar", methods=["DELETE"])
def limpar_banco():
    """Rota temporária para apagar todos os documentos e resetar o banco"""
    resultado = colecao_titulos.delete_many({}) # O {} vazio significa "apagar tudo"
    
    return jsonify({
        "mensagem": f"Faxina concluída! {resultado.deleted_count} filmes foram apagados."
    }), 200


# =========================
# ANALYTICS
# =========================

@app.route("/titulos/quantidade-por-categoria", methods=["GET"])
def quantidade_por_categoria():
    pipeline = [
        {
            "$group": {
                "_id": "$categoria",
                "quantidade_filmes": {"$sum": 1},
                "filmes": {"$push": "$nome"}
            }
        },
        {"$sort": {"quantidade_filmes": -1}}
    ]

    resultado = list(colecao_titulos.aggregate(pipeline))



    resposta = [
    {
        "categoria": item["_id"],
        "quantidade_filmes": item["quantidade_filmes"],
        "filmes": item["filmes"]
    }
    for item in resultado
]


    return jsonify(resposta)


@app.route("/titulos/decadas", methods=["GET"])
def filmes_por_decada():
    pipeline = [
        {
            "$addFields": {
                "decada": {
                    "$multiply": [
                        {"$floor": {"$divide": ["$ano", 10]}},
                        10
                    ]
                }
            }
        },
        {
            "$group": {
                "_id": "$decada",
                "quantidade_filmes": {"$sum": 1},
                "filmes": {"$push": {"nome": "$nome", "ano": "$ano"}}

            }
        },
        {"$sort": {"_id": 1}}
    ]

    resultado = list(colecao_titulos.aggregate(pipeline))

    resposta = [
        {
            "decada": doc["_id"],
            "quantidade_filmes": doc["quantidade_filmes"],
            "filmes": doc["filmes"]

        }
        for doc in resultado
    ]

    return jsonify(resposta)


# =========================
# SORTEIOS
# =========================

@app.route("/titulos/sortear", methods=["GET"])
def sortear_filme():
    pipeline = [{"$sample": {"size": 1}}]

    resultado = list(colecao_titulos.aggregate(pipeline))

    if not resultado:
        return jsonify({"erro": "Nenhum filme encontrado"}), 404

    filme = resultado[0]

    return jsonify({
        "nome": filme.get("nome"),
        "categoria": filme.get("categoria"),
        "ano": filme.get("ano")
    })


@app.route("/titulos/sortear/categoria/<categoria>", methods=["GET"])
def sortear_por_categoria(categoria):
    pipeline = [
        {"$match": {"categoria": categoria}},
        {"$sample": {"size": 1}}
    ]

    resultado = list(colecao_titulos.aggregate(pipeline))

    if not resultado:
        return jsonify({"erro": "Nenhum filme encontrado para essa categoria"}), 404

    filme = resultado[0]

    return jsonify({
        "nome": filme.get("nome"),
        "categoria": filme.get("categoria"),
        "ano": filme.get("ano")
    })


@app.route("/titulos/sortear/decada/<int:decada>", methods=["GET"])
def sortear_por_decada(decada):
    pipeline = [
        {
            "$addFields": {
                "decada": {
                    "$multiply": [
                        {"$floor": {"$divide": ["$ano", 10]}},
                        10
                    ]
                }
            }
        },
        {"$match": {"decada": decada}},
        {"$sample": {"size": 1}}
    ]

    resultado = list(colecao_titulos.aggregate(pipeline))

    if not resultado:
        return jsonify({"erro": "Nenhum filme encontrado para essa década"}), 404

    filme = resultado[0]

    return jsonify({
        "nome": filme.get("nome"),
        "categoria": filme.get("categoria"),
        "ano": filme.get("ano"),
        "decada": decada
    })


if __name__ == "__main__":
    app.run(debug=True)
