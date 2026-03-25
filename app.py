from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file
import os
from database import inicializar_banco, salvar_confirmacao, ler_confirmacoes

# --- NOVO: Importação para ler o arquivo .env ---
from dotenv import load_dotenv

# --- NOVO: Comando que carrega as variáveis do arquivo .env para a memória ---
load_dotenv()

app = Flask(__name__)

# --- ALTERADO: Agora buscamos a chave de segurança no arquivo .env ---
# O os.getenv("NOME") busca o valor que você escreveu lá no arquivo .env
app.secret_key = os.getenv("SECRET_KEY")

# --- ALTERADO: A senha do admin agora também vem do .env ---
# Se o arquivo .env não existir ou estiver errado, ele ficará vazio
SENHA_ADMIN = os.getenv("SENHA_ADMIN")

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
        presenca = request.form.get("presenca") # "Sim" ou "Não"

        if presenca == "Não":
            fralda = "Não se aplica"
            mimo = "Não se aplica"
        else:
            # Se for "Sim", pega os valores que o usuário preencheu
            fralda = request.form.get("tamanho_fralda")
            mimo = request.form.get("mimo_extra", "Nenhum")

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
        # Aqui o Python compara o que o usuário digitou com a variável que veio do .env
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
    
    # Reiniciamos o dicionário para garantir que comece do zero
    resumo_fraldas = {"P": 0, "M": 0, "G": 0}
    
    for c in dados:
        # 1. Padronizamos a resposta de presença (Remove espaços e ignora maiúsculas/minúsculas)
        presenca = str(c.get('presenca', '')).strip().capitalize()
        
        if presenca == "Sim":
            confirmados_sim += 1
            
            # 2. Pegamos o tamanho da fralda e limpamos espaços extras
            tamanho = str(c.get('fralda', '')).strip().upper()
            
            # 3. Só somamos se o tamanho for P, M ou G
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
        return send_file(
            caminho_completo, 
            as_attachment=True, 
            download_name="RELATORIO_PRESENCA_AYLA.xlsx"
        )
    else:
        return "Erro: O relatório ainda não foi gerado. Cadastre um convidado primeiro!"

# ---------------------------------------------------------
# EXECUÇÃO
# ---------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)