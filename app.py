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

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/cadastrar", methods=["POST"])
def cadastrar():
    novo_usuario = request.get_json()  # renomeei p/ evitar conflito
    print("Recebido no Flask:", novo_usuario)

    if not novo_usuario:
        return jsonify({"mensagem": "Erro: nenhum dado recebido"}), 400

    # Carregar os usuários já existentes
    if os.path.exists(ARQUIVO_JSON):
        with open(ARQUIVO_JSON, "r") as f:
            usuarios = json.load(f)
    else:
        usuarios = []

    # Verificar se já existe CPF cadastrado
    for usuario in usuarios:
        if usuario["cpf"] == novo_usuario["cpf"]:
            return jsonify({"erro": "CPF já cadastrado"}), 400

    for usuario in usuarios:
        if usuario["email"] == novo_usuario["email"]:
            return jsonify({"erro": "Email já cadastrado"}), 400
        
    for usuario in usuarios:
        if usuario["tel"] == novo_usuario["tel"]:
            return jsonify({"erro": "Email já cadastrado"}), 400

    # Se não existir, adiciona
    usuarios.append(novo_usuario)

    # Salva no arquivo JSON
    with open(ARQUIVO_JSON, "w") as f:
        json.dump(usuarios, f, indent=2)

    return jsonify({"mensagem": "Cadastro realizado com sucesso!"})


if __name__ == "__main__":
    app.run(debug=True)
