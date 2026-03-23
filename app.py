from flask import Flask, render_template, request, redirect, url_for, session
import os
# DESCRIÇÃO: Importamos as funções que gerenciam o Excel
from database import inicializar_banco, salvar_confirmacao, ler_confirmacoes

app = Flask(__name__)

# DESCRIÇÃO: Chave para criptografar as sessões. Fundamental para o login funcionar.
app.secret_key = 'ayla_secret_2026' 

# DESCRIÇÃO: Senha definida para o acesso administrativo.
SENHA_ADMIN = "ayla123"

# DESCRIÇÃO: Garante que o arquivo Excel exista antes do site abrir.
inicializar_banco()

# ---------------------------------------------------------
# ROTA 1: PÁGINA INICIAL (CONVITE)
# ---------------------------------------------------------
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        return render_template("index.html")
    
    if request.method == "POST":
        nome = request.form.get("nome_completo")
        fralda = request.form.get("tamanho_fralda")
        mimo = request.form.get("mimo_extra", "Nenhum")
        presenca = request.form.get("presenca") 

        salvar_confirmacao(nome, fralda, mimo, presenca)
        return redirect(url_for('sucesso'))

# ---------------------------------------------------------
# ROTA 2: PÁGINA DE SUCESSO
# ---------------------------------------------------------
@app.route("/sucesso")
def sucesso():
    return render_template("sucesso.html")

# ---------------------------------------------------------
# ROTA 3: LOGIN DO ADMIN
# ---------------------------------------------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        senha_digitada = request.form.get('senha')
        
        if senha_digitada == SENHA_ADMIN:
            session['logado'] = True # DESCRIÇÃO: Dá permissão de acesso
            return redirect('/admin')
        else:
            return render_template('login.html', erro="Senha incorreta!")
            
    return render_template('login.html')

# ---------------------------------------------------------
# ROTA 4: PAINEL ADMINISTRATIVO (PROTEGIDO)
# ---------------------------------------------------------
@app.route("/admin")
def admin():
    # DESCRIÇÃO: Verifica se o usuário passou pelo login
    if not session.get('logado'):
        return redirect('/login') 
    
    dados = ler_confirmacoes()
    confirmados_sim = 0
    confirmados_nao = 0
    
    for c in dados:
        if c.get('presenca') == "Sim":
            confirmados_sim += 1
        else:
            confirmados_nao += 1
                
    return render_template("admin.html", 
                           convidados=dados, 
                           sim=confirmados_sim, 
                           nao=confirmados_nao)

# ---------------------------------------------------------
# EXECUÇÃO DO APP (ESTA DEVE SER SEMPRE A ÚLTIMA LINHA)
# ---------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)