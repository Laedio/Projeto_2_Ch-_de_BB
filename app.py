from flask import Flask, render_template, request, redirect, url_for
import os
# Importamos as funções do seu database.py
from database import inicializar_banco, salvar_confirmacao, ler_confirmacoes

app = Flask(__name__)

# Inicializa o banco (verifica se o Excel existe)
inicializar_banco()

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        return render_template("index.html")
    
    if request.method == "POST":
        nome = request.form.get("nome_completo")
        fralda = request.form.get("tamanho_fralda")
        mimo = request.form.get("mimo_extra", "Nenhum")
        presenca = request.form.get("presenca") 

        # Salva no Excel
        salvar_confirmacao(nome, fralda, mimo, presenca)

        return redirect(url_for('sucesso'))

@app.route("/sucesso")
def sucesso():
    return render_template("sucesso.html")

@app.route("/admin")
def admin():
    # Esta é a versão correta que usa o ler_confirmacoes do seu database.py
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

if __name__ == "__main__":
    app.run(debug=True)