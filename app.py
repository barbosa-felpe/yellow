from flask import Flask, request, jsonify, render_template
import json, os

app = Flask(__name__)
ARQUIVO_JSON = os.path.join(os.path.dirname(__file__), "usuario.json")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/cadastro")
def cadastro():
    return render_template("cadastro.html")

@app.route("/cadastrar", methods=["POST"])
def cadastrar():
    usuario = request.get_json(force=True)
    print("Recebido no Flask:", usuario)

    if not usuario:
        return jsonify({"mensagem": "Erro: nenhum dado recebido"}), 400

    # Cria arquivo se não existir
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
