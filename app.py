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

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

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

@app.route("/logar", methods=["POST"])
def logar():
    verificacaoSenha = False
    verificacaoCPF = False

    usuarioLogin = request.get_json()

    with open("usuario.json", "r", encoding="utf-8") as f:
        usuarios = json.load(f)


    for usuario in usuarios:
        if usuario["cpf"] == usuarioLogin["cpf"]:
            verificacaoCPF = True
        else:
            verificacaoCPF = False

        if usuario["senha"] == usuarioLogin["senha"]:
            verificacaoSenha = True
        else:
            verificacaoSenha = False

    if verificacaoSenha and verificacaoCPF:
        return jsonify({"mensagem": "Login bem-sucedido!"})
    else:
        return jsonify({"erro": "Senha ou CPF incorreto"}), 400



if __name__ == "__main__":
    app.run(debug=True)
