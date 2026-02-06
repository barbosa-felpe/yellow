from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
import mysql.connector
import json
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin
import random

# --- REMOVA ou COMENTE estas linhas do SQLAlchemy ---
# from flask_sqlalchemy import SQLAlchemy
# db = SQLAlchemy()
# class Cartao(db.Model)... (Não precisamos disso se usarmos SQL puro)

# --- DEFINA A CLASSE USUARIO ASSIM (Para o Flask-Login) ---
class Usuario(UserMixin):
    def __init__(self, id, nome, cpf):
        self.id = str(id)
        self.nome = nome
        self.cpf = cpf

app = Flask(__name__)
app.secret_key = "sua_chave_secreta"

# Configurações do Banco MySQL
DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = "" 
DB_NAME = "cadastro"
DB_PORT = "3406"

def get_connection():
    try:
        conn = mysql.connector.connect(
            host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_NAME, port=DB_PORT
        )
        return conn
    except mysql.connector.Error as err:
        print(f"Erro ao conectar ao MySQL: {err}")
        return None

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'logar'

# --- LOADER CORRIGIDO PARA MYSQL ---
@login_manager.user_loader
def load_user(user_id):
    conn = get_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM usuarios WHERE id = %s", (user_id,))
        usuario_db = cursor.fetchone()
        cursor.close()
        conn.close()
        if usuario_db:
            return Usuario(usuario_db['id'], usuario_db['nome'], usuario_db['cpf'])
    return None

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
@login_required  # <--- Adicione isso
def recarga():
    return render_template("recarga.html", user=current_user)

# -------------------- AUTENTICAÇÃO --------------------

# Certifique-se de importar login_user lá no topo
@app.route("/cadastrar", methods=["POST"])
def cadastrar():
    data = request.get_json()
    nome = data.get("nome")
    email = data.get("email")
    senha = data.get("senha")
    cpf = data.get("cpf")
    tel = data.get("tel")

    if cpf: cpf = cpf.replace(".", "").replace("-", "")
    if tel: tel = tel.replace("(", "").replace(")", "").replace(" ", "").replace("-", "")

    if not nome or not email or not senha or not cpf:
        return jsonify({"erro": "Preencha todos os campos obrigatórios"}), 400

    conn = get_connection()
    if not conn:
        return jsonify({"erro": "Erro no banco de dados"}), 500

    try:
        cursor = conn.cursor()
        
        # 1. Cria Usuário
        senha_hash = generate_password_hash(senha)
        sql_user = "INSERT INTO usuarios (nome, email, senha, cpf, tel) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(sql_user, (nome, email, senha_hash, cpf, tel))
        novo_id = cursor.lastrowid

        # 2. Cria Conta Bancária (Carteira)
        sql_conta = "INSERT INTO contas (nome, saldo, id_usuario) VALUES (%s, %s, %s)"
        cursor.execute(sql_conta, ('Conta Principal', 0.00, novo_id))

        conn.commit()

        # 3. AUTO-LOGIN (A parte que faltava)
        # Cria o objeto usuário manualmente para logar na sessão
        novo_usuario_obj = Usuario(novo_id, nome, cpf)
        login_user(novo_usuario_obj)

        # Manda direto para o Dashboard
        return jsonify({"mensagem": "Cadastro realizado!", "redirect": "/dashboard"}), 201

    except mysql.connector.Error as err:
        if err.errno == 1062: 
            return jsonify({"erro": "E-mail ou CPF já cadastrados."}), 400
        return jsonify({"erro": f"Erro no banco: {err}"}), 500
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()



@app.route("/logar", methods=["GET", "POST"])
def logar():
    if request.method == "GET":
        return render_template("login.html")

    cpf = request.form.get("cpf")
    senha = request.form.get("senha")

    # --- DEBUG NO TERMINAL ---
    print(f"--- TENTATIVA DE LOGIN ---")
    print(f"CPF Original digitado: '{cpf}'")

    if not cpf or not senha:
        flash("Preencha CPF e Senha", "error")
        return render_template("login.html")

    # Limpeza
    cpf_limpo = cpf.replace(".", "").replace("-", "")
    print(f"CPF Limpo (como vai ser buscado): '{cpf_limpo}'")

    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        
        # Busca
        cursor.execute("SELECT * FROM usuarios WHERE cpf = %s", (cpf_limpo,))
        usuario_db = cursor.fetchone()

        print(f"O que o banco encontrou? {usuario_db}") 

        if not usuario_db:
            # SE ENTRAR AQUI, É O SEU PROBLEMA ATUAL
            print("ERRO: Usuário não encontrado no banco com esse CPF limpo.")
            
            # Tenta buscar SEM limpar para ver se o erro é formatação
            cursor.execute("SELECT * FROM usuarios WHERE cpf = %s", (cpf,))
            teste_formato = cursor.fetchone()
            if teste_formato:
                print(f"ACHEI! Mas o CPF no banco está COM pontos: {teste_formato['cpf']}")
                print("DICA: Sua limpeza de CPF está atrapalhando ou o cadastro foi feito errado.")
            
            flash("Usuário não encontrado.", "error")
            conn.close()
            return render_template("login.html")

        # Verifica senha
        if check_password_hash(usuario_db["senha"], senha):
            print("Senha confere! Logando...")
            user_obj = Usuario(usuario_db['id'], usuario_db['nome'], usuario_db['cpf'])
            login_user(user_obj)
            return redirect(url_for("dashboard"))
        else:
            print("ERRO: Senha incorreta.")
            flash("Senha incorreta.", "error")
            return render_template("login.html")

    except Exception as e:
        print(f"ERRO CRÍTICO: {e}")
        return render_template("login.html")
    finally:
        if conn and conn.is_connected():
            cursor.close()
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
@login_required  # <--- Isso bloqueia quem não logou automaticamente
def dashboard():
    # Não precisamos mais verificar session.get("user_id") manualmente
    
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        # Usamos current_user.id (do Flask-Login)
        user_id = current_user.id 

        # 1. Busca as CONTAS
        cursor.execute("SELECT id, nome, saldo FROM contas WHERE id_usuario = %s", (user_id,))
        contas = cursor.fetchall()

        # 2. Busca os CARTÕES
        cursor.execute("SELECT id, numero, nome_titular, id_conta FROM cartoes WHERE id_usuario = %s", (user_id,))
        cartoes = cursor.fetchall()

        # 3. Calcula o saldo TOTAL
        saldo_total = sum(c['saldo'] for c in contas)
        
        # Formatação segura
        saldo_formatado = f"{saldo_total:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

        cursor.execute("SELECT codigo_linha FROM favoritas WHERE id_usuario=%s", (user_id,))
        rows_favoritos = cursor.fetchall()
        
        # Transforma o resultado do banco em uma lista simples de códigos. Ex: ['040', '303']
        lista_codigos_favoritos = [row['codigo_linha'] for row in rows_favoritos]

        # 2. Agora cruzamos com o JSON (dados_onibus) para pegar o Nome e Terminal
        favoritas_para_exibir = []

        # Certifique-se que dados_onibus foi carregado lá no topo do app.py
        if dados_onibus and 'terminais' in dados_onibus:
            for terminal in dados_onibus['terminais']:
                nome_terminal = terminal.get('nome')
                
                for linha in terminal.get('linhas', []):
                    codigo_atual = linha.get('codigo')
                    
                    # Se o código desta linha do JSON estiver na lista do banco:
                    if codigo_atual in lista_codigos_favoritos:
                        favoritas_para_exibir.append({
                            'codigo': codigo_atual,
                            'nome': linha.get('nome'),
                            'terminal': nome_terminal
                        })

        # --- FIM DA CORREÇÃO ---

        return render_template("dashboard.html",
                               saldo=saldo_formatado,
                               contas=contas,
                               cartoes=cartoes,
                               favoritas=favoritas_para_exibir, # <--- Passamos a lista processada no Python
                               user=current_user)
    except Exception as e:
        print("Erro dashboard:", e)
        return f"Erro ao carregar dashboard: {e}", 500
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

@app.route("/api/realizar_recarga", methods=["POST"])
@login_required 
def realizar_recarga():
    data = request.get_json()
    valor = data.get("valor")

    # Só validamos o valor agora
    if not valor:
        return jsonify({"erro": "Informe um valor"}), 400

    try:
        valor_float = float(valor)
        if valor_float <= 0:
            return jsonify({"erro": "O valor deve ser positivo"}), 400
    except ValueError:
        return jsonify({"erro": "Valor inválido"}), 400

    conn = get_connection()
    if not conn:
        return jsonify({"erro": "Erro no banco de dados"}), 500

    try:
        cursor = conn.cursor()
        
        # --- LÓGICA CORRETA ---
        # Atualiza a conta que pertence a esse usuário.
        # O "LIMIT 1" garante que pega a primeira conta (caso tenha mais de uma)
        sql = """
        UPDATE contas 
        SET saldo = saldo + %s 
        WHERE id_usuario = %s 
        LIMIT 1
        """
        
        cursor.execute(sql, (valor_float, current_user.id))
        
        if cursor.rowcount == 0:
            # Se não atualizou nada, é porque o usuário não tem conta criada no banco ainda
            return jsonify({"erro": "Nenhuma conta bancária encontrada para este usuário."}), 404

        conn.commit()
        return jsonify({"mensagem": "Recarga realizada com sucesso!", "redirect": "/dashboard"}), 200

    except Exception as e:
        print(f"Erro na recarga: {e}")
        return jsonify({"erro": "Erro ao processar recarga"}), 500
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

@app.route('/adicionar_cartao', methods=['GET', 'POST'])
@login_required
def adicionar_cartao():
    if request.method == 'POST':
        nome_cartao = request.form.get('nome') # Ex: "Meu Bilhete Único"
        senha_digitada = request.form.get('senha')

        if not nome_cartao or not senha_digitada:
            flash('Preencha o nome do cartão e sua senha.', 'error')
            return redirect(url_for('adicionar_cartao'))

        conn = get_connection()
        if not conn:
            flash("Erro de conexão.", "error")
            return redirect(url_for('dashboard'))

        try:
            cursor = conn.cursor(dictionary=True)

            # 1. VERIFICAR A SENHA DO USUÁRIO (Segurança)
            cursor.execute("SELECT senha FROM usuarios WHERE id = %s", (current_user.id,))
            user_db = cursor.fetchone()

            if not user_db or not check_password_hash(user_db['senha'], senha_digitada):
                flash('Senha incorreta. Não foi possível criar o cartão.', 'error')
                return redirect(url_for('adicionar_cartao'))

            # 2. PEGAR ID DA CONTA
            cursor.execute("SELECT id FROM contas WHERE id_usuario = %s LIMIT 1", (current_user.id,))
            conta = cursor.fetchone()
            if not conta:
                flash('Erro: Usuário sem conta bancária.', 'error')
                return redirect(url_for('dashboard'))
            
            id_conta_usuario = conta['id']

            # 3. GERAR O NÚMERO DO CARTÃO AUTOMATICAMENTE
            # Gera uma sequência de 16 números aleatórios
            numero_gerado = ''.join([str(random.randint(0, 9)) for _ in range(16)])
            
            # Validade e CVV agora são inúteis para ônibus, vamos colocar valores padrão
            validade_fake = "00/00" 
            cvv_fake = "000"

            # 4. SALVAR NO BANCO
            sql = """
            INSERT INTO cartoes (nome_titular, numero, validade, cvv, id_usuario, id_conta)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (nome_cartao, numero_gerado, validade_fake, cvv_fake, current_user.id, id_conta_usuario))
            conn.commit()
            
            flash(f'Cartão "{nome_cartao}" criado com sucesso!', 'success')
            return redirect(url_for('dashboard'))

        except Exception as e:
            print(f"Erro ao criar cartão: {e}")
            flash('Erro ao processar solicitação.', 'error')
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()

    return render_template('adicionar_cartao.html')

if __name__ == "__main__":
    app.run(debug=True)