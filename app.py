from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file
import os
import pandas as pd # Usaremos apenas para gerar o download agora
from dotenv import load_dotenv
from database import inicializar_banco, salvar_confirmacao, ler_confirmacoes, excluir_confirmacao

# Carrega variáveis de ambiente
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")
SENHA_ADMIN = os.getenv("SENHA_ADMIN")

# Garante que o banco de dados SQL existe ao iniciar
inicializar_banco()

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        return render_template("index.html")
    
    if request.method == "POST":
        nome = request.form.get("nome_completo")
        presenca = request.form.get("presenca")

        if presenca == "Não":
            fralda = "Não se aplica"
            mimo = "Não se aplica"
        else:
            fralda = request.form.get("tamanho_fralda")
            mimo = request.form.get("mimo_extra", "Nenhum")

        salvar_confirmacao(nome, fralda, mimo, presenca)
        
        flash(f"Oba, {nome}! Sua confirmação foi enviada com sucesso. 🎉")
        return redirect(url_for('sucesso'))

@app.route("/sucesso")
def sucesso():
    return render_template("sucesso.html")

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

@app.route("/admin")
def admin():
    if not session.get('logado'):
        return redirect('/login') 
    
    dados = ler_confirmacoes()
    confirmados_sim = 0
    confirmados_nao = 0
    resumo_fraldas = {"P": 0, "M": 0, "G": 0}
    
    for c in dados:
        # No SQLite, acessamos 'presenca' e 'fralda' direto
        presenca = str(c['presenca']).strip().capitalize()
        
        if presenca == "Sim":
            confirmados_sim += 1
            tamanho = str(c['fralda']).strip().upper()
            if tamanho in resumo_fraldas:
                resumo_fraldas[tamanho] += 1
        else:
            confirmados_nao += 1
                
    return render_template("admin.html", 
                           convidados=dados, 
                           sim=confirmados_sim, 
                           nao=confirmados_nao,
                           fraldas=resumo_fraldas)

@app.route("/logout")
def logout():
    session.pop('logado', None)
    flash("Você saiu do painel administrativo.")
    return redirect(url_for('login'))

@app.route("/download")
def download():
    """Lê do Banco de Dados e gera um Excel na hora para o usuário."""
    if not session.get('logado'):
        return redirect('/login')
    
    dados = ler_confirmacoes()
    if not dados:
        return "Nenhum dado para exportar."

    # Criamos um DataFrame com os dados do banco
    df = pd.DataFrame(dados)
    
    # Nome do arquivo temporário
    caminho_excel = "relatorio_convidados.xlsx"
    df.to_excel(caminho_excel, index=False)
    
    return send_file(caminho_excel, as_attachment=True)

@app.route("/excluir/<nome>")
def excluir(nome):
    if not session.get('logado'):
        return redirect('/login')
    
    if excluir_confirmacao(nome):
        flash(f"Convidado {nome} removido com sucesso!")
    else:
        flash("Erro ao tentar remover convidado.")
        
    return redirect(url_for('admin'))

if __name__ == "__main__":
    app.run(debug=True)