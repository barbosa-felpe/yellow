import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

# 🔹 Função para criar conexão com o banco MySQL
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="12345678",
        database="cadastro"
    )

# ================= Rotas =================
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

# ================= Cadastro =================
@app.route("/cadastrar", methods=["POST"])
def cadastrar():
    try:
        novo_usuario = request.get_json()
        print("📥 Recebido no Flask:", novo_usuario)

        if not novo_usuario:
            return jsonify({"erro": "Nenhum dado recebido"}), 400

        # Validação mínima
        required_fields = ["nome", "senha", "tel", "email", "cpf"]
        for field in required_fields:
            if not novo_usuario.get(field):
                return jsonify({"erro": f"Campo '{field}' é obrigatório"}), 400

        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        # Verificar duplicatas
        cursor.execute(
            "SELECT * FROM usuarios WHERE cpf = %s OR email = %s OR tel = %s",
            (novo_usuario["cpf"], novo_usuario["email"], novo_usuario["tel"])
        )
        existente = cursor.fetchone()

        if existente:
            if existente["cpf"] == novo_usuario["cpf"]:
                return jsonify({"erro": "CPF já cadastrado"}), 400
            if existente["email"] == novo_usuario["email"]:
                return jsonify({"erro": "Email já cadastrado"}), 400
            if existente["tel"] == novo_usuario["tel"]:
                return jsonify({"erro": "Telefone já cadastrado"}), 400

        # Gerar hash da senha
        senha_hash = generate_password_hash(novo_usuario["senha"])

        # Inserir usuário no banco
        cursor.execute(
            """
            INSERT INTO usuarios (nome, senha, tel, email, cpf)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                novo_usuario["nome"],
                senha_hash,
                novo_usuario["tel"],
                novo_usuario["email"],
                novo_usuario["cpf"]
            )
        )
        conn.commit()

        cursor.close()
        conn.close()

        return jsonify({"mensagem": "Cadastro realizado com sucesso!"}), 200

    except Exception as e:
        print("🔥 Erro no backend (cadastro):", e)
        return jsonify({"erro": str(e)}), 500

# ================= Login =================
@app.route("/logar", methods=["POST"])
def logar():
    try:
        dados = request.get_json()
        print("📥 Tentativa de login:", dados)

        # Validação por campo
        required_fields = ["cpf", "senha"]
        for field in required_fields:
            if not dados.get(field):
                return jsonify({"erro": f"Campo '{field}' é obrigatório"}), 400

        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM usuarios WHERE cpf = %s", (dados["cpf"],))
        usuario = cursor.fetchone()

        cursor.close()
        conn.close()

        if not usuario:
            return jsonify({"erro": "Usuário não encontrado"}), 404

        if check_password_hash(usuario["senha"], dados["senha"]):
            return jsonify({"mensagem": f"Bem-vindo, {usuario['nome']}!"}), 200
        else:
            return jsonify({"erro": "Senha incorreta"}), 401

    except Exception as e:
        print("🔥 Erro no backend (login):", e)
        return jsonify({"erro": str(e)}), 500
    
if __name__ == "__main__":
    app.run(debug=True)
