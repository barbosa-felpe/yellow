import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, request, jsonify, render_template
import json


DATABASE_NAME = "cadastro.db"
app = Flask(__name__)

# 🔹 Função para criar a tabela no banco de dados se não existir
def init_db():
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()

        # Criar tabela de usuários
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                senha TEXT NOT NULL,
                tel TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                cpf TEXT UNIQUE NOT NULL
            )
        """)

        # Criar tabela de linhas
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS linhas (
                codigo TEXT PRIMARY KEY,
                nome TEXT NOT NULL,
                terminal TEXT NOT NULL
            )
        """)

        conn.commit()
        print("✅ Tabelas 'usuarios' e 'linhas' verificadas/criadas com sucesso.")

    except Exception as e:
        print(f"🔥 Erro ao inicializar o banco de dados: {e}")
    finally:
        if conn:
            conn.close()

# 🔹 Função para obter uma conexão com o banco de dados SQLite
def get_connection():
    conn = sqlite3.connect(DATABASE_NAME)
    # Retorna as linhas como dicionários para fácil acesso por nome de coluna
    conn.row_factory = sqlite3.Row
    return conn


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
        cursor = conn.cursor()

        # Verificar duplicatas
        cursor.execute(
            "SELECT * FROM usuarios WHERE cpf = ? OR email = ? OR tel = ?",
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
            VALUES (?, ?, ?, ?, ?)
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

        return jsonify({"mensagem": "Cadastro realizado com sucesso!"}), 200

    except sqlite3.IntegrityError as e:
        print(f"🔥 Erro de integridade no SQLite: {e}")
        return jsonify({"erro": "Dado duplicado. Verifique CPF, email ou telefone."}), 400
    except Exception as e:
        print(f"🔥 Erro no backend (cadastro): {e}")
        return jsonify({"erro": str(e)}), 500
    finally:
        if 'conn' in locals() and conn:
            conn.close()

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
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE cpf = ?", (dados["cpf"],))
        usuario = cursor.fetchone()


        if not usuario:
            return jsonify({"erro": "Usuário não encontrado"}), 404

        if check_password_hash(usuario["senha"], dados["senha"]):
            return jsonify({"mensagem": f"Bem-vindo, {usuario['nome']}!"}), 200
        else:
            return jsonify({"erro": "Senha incorreta"}), 401
    except Exception as e:
        print(f"🔥 Erro no backend (login): {e}")
        return jsonify({"erro": str(e)}), 500
    finally:
        if 'conn' in locals() and conn:
            conn.close()

   
try:
    with open('linhas.json', 'r', encoding='utf-8') as f:
        dados_onibus = json.load(f)
except FileNotFoundError:
    print("ERRO: O arquivo 'linhas.json' não foi encontrado. A API usará dados vazios.")
    dados_onibus = {"terminais": []}
except json.JSONDecodeError:
    print("ERRO: O arquivo 'linhas.json' está mal formatado.")
    dados_onibus = {"terminais": []}

    
@app.route("/linhas")
def linhas():
    return render_template("linhas.html")

@app.route('/api/linhas', methods=['GET'])
def obter_todas_as_linhas():
    # A função agora simplesmente retorna a variável que já está na memória. Super rápido!
    return jsonify(dados_onibus)

# Rota da API para buscar uma linha ESPECÍFICA (não usada pela busca ao vivo, mas é útil ter)
@app.route('/api/linha/<string:codigo>', methods=['GET'])
def obter_linha_por_codigo(codigo):
    
    # O método .get() é uma forma segura de acessar chaves de um dicionário
    for terminal in dados_onibus.get('terminais', []):
        for linha in terminal.get('linhas', []):
            if linha.get('codigo') == codigo:
                return jsonify(linha)
    
    # Se não encontrar, retorna uma mensagem de erro com o código 404 (Não Encontrado)
    return jsonify({"erro": "Linha não encontrada"}), 404



if __name__ == "__main__":
    init_db()  # Garante que o banco e a tabela existam antes de rodar a aplicação
    app.run(debug=True)
