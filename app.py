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


if __name__ == "__main__":
    app.run(debug=True)
