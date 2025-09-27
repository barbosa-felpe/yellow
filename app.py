from flask import Flask, render_template, request, jsonify, session
import sqlite3
import json
import locale
from werkzeug.security import generate_password_hash, check_password_hash

DATABASE_NAME = "cadastro.db"
app = Flask(__name__)
app.secret_key = "sua_chave_secreta"  # Para sessões
locale.setlocale(locale.LC_ALL, '')  # Para usar locale.currency

# -------------------- INICIALIZAÇÃO DB --------------------
def init_db():
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()

        # Usuários
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

        # Linhas
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS linhas (
                codigo TEXT PRIMARY KEY,
                nome TEXT NOT NULL,
                terminal TEXT NOT NULL
            )
        """)

        # Contas (cada usuário pode ter várias contas)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS contas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_usuario INTEGER NOT NULL,
                nome TEXT NOT NULL,
                saldo REAL DEFAULT 0,
                FOREIGN KEY (id_usuario) REFERENCES usuarios(id)
            )
        """)

        # Linhas favoritas
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS favoritas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_usuario INTEGER NOT NULL,
                codigo_linha TEXT NOT NULL,
                FOREIGN KEY (id_usuario) REFERENCES usuarios(id),
                FOREIGN KEY (codigo_linha) REFERENCES linhas(codigo)
            )
        """)

        # Cartões (adicionado)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cartoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_usuario INTEGER NOT NULL,
                numero TEXT NOT NULL,
                validade TEXT NOT NULL,
                cvv TEXT NOT NULL,
                saldo REAL DEFAULT 0,
                FOREIGN KEY (id_usuario) REFERENCES usuarios(id)
            )
        """)

        conn.commit()
        print("Tabelas criadas/verificadas com sucesso.")
    except Exception as e:
        print(f"Erro ao inicializar a base de dados: {e}")
    finally:
        if conn:
            conn.close()


def get_connection():
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row
    return conn

# -------------------- ROTAS --------------------

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/cadastro")
def cadastro():
    return render_template("cadastro.html")

@app.route("/login")
def login():
    return render_template("login.html")



@app.route("/recarga")
def recarga():
    return render_template("recarga.html")

# -------------------- AUTENTICAÇÃO --------------------

@app.route("/cadastrar", methods=["POST"])
def cadastrar():
    try:
        novo_usuario = request.get_json()
        print("Recebido no Flask:", novo_usuario)
        if not novo_usuario:
            return jsonify({"erro": "Nenhum dado recebido"}), 400

        required_fields = ["nome", "senha", "tel", "email", "cpf"]
        for field in required_fields:
            if not novo_usuario.get(field):
                return jsonify({"erro": f"Campo '{field}' é obrigatório"}), 400

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM usuarios WHERE cpf = ? OR email = ? OR tel = ?",
            (novo_usuario["cpf"], novo_usuario["email"], novo_usuario["tel"])
        )
        existente = cursor.fetchone()
        if existente:
            return jsonify({"erro": "CPF, email ou telefone já cadastrado"}), 400

        senha_hash = generate_password_hash(novo_usuario["senha"])
        cursor.execute(
            "INSERT INTO usuarios (nome, senha, tel, email, cpf) VALUES (?, ?, ?, ?, ?)",
            (novo_usuario["nome"], senha_hash, novo_usuario["tel"], novo_usuario["email"], novo_usuario["cpf"])
        )
        conn.commit()
        return jsonify({"mensagem": "Registro realizado com sucesso!"}), 200
    except Exception as e:
        print(f"Erro no backend (cadastro): {e}")
        return jsonify({"erro": str(e)}), 500
    finally:
        if 'conn' in locals() and conn:
            conn.close()

@app.route("/logar", methods=["POST"])
def logar():
    try:
        dados = request.get_json()
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
            session["user_id"] = usuario["id"]  # <- aqui salvamos na sessão
            return jsonify({"mensagem": f"Bem-vindo, {usuario['nome']}!"}), 200
        else:
            return jsonify({"erro": "Senha incorreta"}), 401
    except Exception as e:
        print(f"Erro no backend (login): {e}")
        return jsonify({"erro": str(e)}), 500
    finally:
        if 'conn' in locals() and conn:
            conn.close()

# -------------------- API DE LINHAS --------------------

try:
    with open('linhas.json', 'r', encoding='utf-8') as f:
        dados_onibus = json.load(f)
except FileNotFoundError:
    print("ERRO: O ficheiro 'linhas.json' não foi encontrado. A API usará dados vazios.")
    dados_onibus = {"terminais": []}
except json.JSONDecodeError:
    print("ERRO: O ficheiro 'linhas.json' está mal formatado.")
    dados_onibus = {"terminais": []}

@app.route("/linhas")
def linhas():
    return render_template("linhas.html")

@app.route('/api/linhas', methods=['GET'])
def obter_todas_as_linhas():
    return jsonify(dados_onibus)

@app.route('/api/rota/<string:codigo>', methods=['GET'])
def obter_rota_por_codigo(codigo):
    try:
        for terminal in dados_onibus.get('terminais', []):
            for linha in terminal.get('linhas', []):
                if linha.get('codigo') == codigo:
                    coordenadas_originais = linha.get('rota')
                    if not coordenadas_originais:
                        return jsonify({"erro": "Rota nao disponivel"}), 404

                    coordenadas_corrigidas = [
                        [p[1], p[0]] for p in coordenadas_originais if isinstance(p, list) and len(p) >= 2
                    ]

                    if not coordenadas_corrigidas:
                        return jsonify({"erro": "Dados da rota invalidos"}), 500

                    return jsonify({
                        "codigo": linha.get('codigo'),
                        "nome": linha.get('nome'),
                        "pontos": coordenadas_corrigidas
                    })
        return jsonify({"erro": "Linha nao encontrada"}), 404
    except Exception as e:
        print(f"ERRO /api/rota: {e}")
        return jsonify({"erro": "Erro interno"}), 500
   

@app.route("/dashboard")
def dashboard():
    user_id = session.get("user_id")
    if not user_id:
        return "Usuário não logado", 401

    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Saldo total das contas
        cursor.execute("SELECT SUM(saldo) as saldo FROM contas WHERE id_usuario = ?", (user_id,))
        resultado = cursor.fetchone()
        saldo = resultado["saldo"] if resultado and resultado["saldo"] is not None else 0.0

        # Todas as contas
        cursor.execute("SELECT * FROM contas WHERE id_usuario=?", (user_id,))
        contas = cursor.fetchall()

        # Cartões do usuário
        cursor.execute("SELECT * FROM cartoes WHERE id_usuario=?", (user_id,))
        cartoes = cursor.fetchall()

        # Linhas favoritas
        cursor.execute("""
            SELECT l.codigo, l.nome, l.terminal
            FROM favoritas f
            JOIN linhas l ON f.codigo_linha = l.codigo
            WHERE f.id_usuario=?
        """, (user_id,))
        favoritas = cursor.fetchall()

        return render_template("dashboard.html",
                               saldo=locale.currency(saldo, grouping=True),
                               contas=contas,
                               cartoes=cartoes,
                               favoritas=favoritas)
    except Exception as e:
        print("Erro ao carregar dashboard:", e)
        return jsonify({"erro": "Não foi possível carregar o dashboard"}), 500
    finally:
        conn.close()


if __name__ == "__main__":
    init_db()
    app.run(debug=True)