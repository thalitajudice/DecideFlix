from flask import Flask, request, jsonify

from pymongo import MongoClient

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





@app.route("/")

def home():

    return "API DecideFlix funcionando"



@app.route("/titulos", methods=["GET"])

def listar_titulos():

    lista = []



    for titulo in colecao_titulos.find():

        lista.append({

            "id": str(titulo["_id"]),

            "nome": titulo["nome"],

            "categoria": titulo["categoria"],

            "ano": titulo["ano"]

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

    dados = request.json  # espera uma lista de objetos



    if not isinstance(dados, list) or len(dados) == 0:
        return jsonify({"erro": "Envie uma lista de títulos"}), 400

    # 2. Lógica do banco
    resultado = colecao_titulos.insert_many(dados)

    # 3. Resposta de sucesso (Onde costuma faltar o return!)
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

        "nome": titulo["nome"],

        "categoria": titulo["categoria"],

        "ano": titulo["ano"]

    })



@app.route("/titulos/<id>", methods=["PUT"])

def atualizar_titulo(id):

    dados = request.json



    resultado = colecao_titulos.update_one(

        {"_id": ObjectId(id)},

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

    resultado = colecao_titulos.delete_one({"_id": ObjectId(id)})



    if resultado.deleted_count == 0:

        return jsonify({"erro": "Título não encontrado"}), 404



    return jsonify({"mensagem": "Título removido com sucesso"})


@app.route("/titulos/quantidade-por-categoria", methods=["GET"])
def quantidade_por_categoria():
    pipeline = [
        {
            "$group": {
                "_id": "$categoria",
                "quantidade_filmes": {"$sum": 1}
            }
        },
        {
            "$sort": {"quantidade_filmes": -1}
        }
    ]

    resultado = colecao_titulos.aggregate(pipeline)

    resposta = []
    for item in resultado:
        resposta.append({
            "categoria": item["_id"],
            "quantidade_filmes": item["quantidade_filmes"]
        })

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
                "quantidade_filmes": {"$sum": 1}
            }
        },
        {
            "$sort": {"_id": 1}
        }
    ]

    resultado = list(colecao_titulos.aggregate(pipeline))

    # Formatando saída
    resposta = [
        {
            "decada": doc["_id"],
            "quantidade_filmes": doc["quantidade_filmes"]
        }
        for doc in resultado
    ]

    return jsonify(resposta)

@app.route("/titulos/sortear", methods=["GET"])
def sortear_filme():
    pipeline = [
        {"$sample": {"size": 1}}
    ]

    resultado = list(colecao_titulos.aggregate(pipeline))

    if not resultado:
        return jsonify({"erro": "Nenhum filme encontrado"}), 404

    filme = resultado[0]

    return jsonify({
        "titulo": filme.get("titulo"),
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
        "titulo": filme.get("titulo"),
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
        "titulo": filme.get("titulo"),
        "categoria": filme.get("categoria"),
        "ano": filme.get("ano"),
        "decada": decada
    })


if __name__ == "__main__":
    app.run(debug=True)
