from flask import Flask, request, jsonify
from pymongo import MongoClient

app = Flask(__name__)

client = MongoClient(
    "mongodb+srv://thalitajudice_db_user:ezxbUarJQGdhlRtM@cluster0.3q7fnip.mongodb.net/decideflix",
    serverSelectionTimeoutMS=5000
)

db = client["decideflix"]
colecao_titulos = db["titulos"]

@app.route("/")
def home():
    return "API DecideFlix funcionando 🚀"

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

if __name__ == "__main__":
    app.run(debug=True)
