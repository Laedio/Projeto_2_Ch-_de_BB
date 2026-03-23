from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file # send_file movido para aqui
import os
from database import inicializar_banco, salvar_confirmacao, ler_confirmacoes

app = Flask(__name__)

# DESCRIÇÃO: Chave de segurança para as sessões e mensagens flash
app.secret_key = 'ayla_secret_2026' 

# DESCRIÇÃO: Senha do painel
SENHA_ADMIN = "ayla123"

# Inicializa o banco de dados
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
        
        flash(f"Oba, {nome}! Sua confirmação foi enviada com sucesso. 🎉")
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
            session['logado'] = True
            return redirect('/admin')
        else:
            return render_template('login.html', erro="Senha incorreta!")
            
    return render_template('login.html')

# ---------------------------------------------------------
# ROTA 4: PAINEL ADMINISTRATIVO (PROTEGIDO)
# ---------------------------------------------------------
@app.route("/admin")
def admin():
    if not session.get('logado'):
        return redirect('/login') 
    
    dados = ler_confirmacoes()
    confirmados_sim = 0
    confirmados_nao = 0
    
    # DESCRIÇÃO: Dicionário ajustado apenas para P, M e G
    resumo_fraldas = {"P": 0, "M": 0, "G": 0}
    
    for c in dados:
        if c.get('presenca') == "Sim":
            confirmados_sim += 1
            tamanho = c.get('fralda')
            if tamanho in resumo_fraldas:
                resumo_fraldas[tamanho] += 1
        else:
            confirmados_nao += 1
                
    return render_template("admin.html", 
                           convidados=dados, 
                           sim=confirmados_sim, 
                           nao=confirmados_nao,
                           fraldas=resumo_fraldas)

# ---------------------------------------------------------
# ROTA 5: DOWNLOAD DA PLANILHA
# ---------------------------------------------------------
@app.route("/download")
def download():
    if not session.get('logado'):
        return redirect('/login')
        
    NOME_PLANILHA = "lista_ayla.xlsx" 
    caminho_completo = os.path.join(os.getcwd(), NOME_PLANILHA)
    
    if os.path.exists(caminho_completo):
        # DESCRIÇÃO: 'download_name' muda o nome do arquivo que o usuário recebe.
        # Isso protege o seu arquivo original 'lista_ayla.xlsx' de ser confundido.
        return send_file(
            caminho_completo, 
            as_attachment=True, 
            download_name="RELATORIO_PRESENCA_AYLA.xlsx"
        )
    else:
        return "Erro: O relatório ainda não foi gerado. Cadastre um convidado primeiro!"

# ---------------------------------------------------------
# EXECUÇÃO (SEMPRE POR ÚLTIMO)
# ---------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)