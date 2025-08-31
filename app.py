from flask import Flask, request, jsonify, render_template
import json
import os

app = Flask(__name__)

ARQUIVO_JSON = "usuario.json"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/cadastrar", methods=["POST"])
def cadastrar():
    usuario = request.get_json()

    if os.path.exists(ARQUIVO_JSON):
        with open(ARQUIVO_JSON, "r") as f:
            usuarios = json.load(f)
    else:
        usuarios = []

    usuarios.append(usuario)

    with open(ARQUIVO_JSON, "w") as f:
        json.dump(usuarios, f, indent=2)
    
    return jsonify({"mensagem": "Cadastro realizado com sucesso!"})

if __name__ == "__main__":
    app.run(debug=True)