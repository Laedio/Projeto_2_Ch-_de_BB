from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file
import os
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
from database import inicializar_banco, ler_confirmacoes, excluir_confirmacao, conectar_banco, registrar_log, gerar_novo_convite

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")
SENHA_ADMIN = os.getenv("SENHA_ADMIN")

# Inicializa o banco de dados
inicializar_banco()

@app.route("/")
def index():
    return "<h1>Acesso Restrito</h1><p>Use o link individual enviado pelo WhatsApp.</p>", 403

# --- ROTA DO CONVITE (ABRIR O FORMULÁRIO) ---
@app.route("/convite/<token>")
def convite_personalizado(token):
    with conectar_banco() as conn:
        convite = conn.execute("SELECT * FROM convites WHERE codigo_unico = ?", (token,)).fetchone()

    if not convite:
        registrar_log(request.remote_addr, request.user_agent.string, "Tentativa: Token Inválido", "Desconhecido")
        return "<h1>Convite Inválido</h1>", 404

    # REGISTRO DE ACESSO: Agora acontece ANTES de qualquer verificação de status
    registrar_log(request.remote_addr, request.user_agent.string, "Acessou o Link", convite['nome_convidado'])

    # Se já confirmou, leva para o sucesso (mas o log de acesso acima já foi gravado!)
    if convite['status'] == 'confirmado':
        return render_template("sucesso.html", nome=convite['nome_convidado'], ja_confirmado=True)

    return render_template("index.html", nome=convite['nome_convidado'], token=token)

# --- ROTA DE CONFIRMAÇÃO (SALVAR DADOS) ---
@app.route("/confirmar/<token>", methods=["POST"])
def confirmar(token):
    nome_real = request.form.get("nome_invisivel")
    presenca = request.form.get("presenca")
    
    with conectar_banco() as conn:
        # 1. TRANCA DE SEGURANÇA: Verifica se este TOKEN já foi usado
        check_token = conn.execute("SELECT status FROM convites WHERE codigo_unico = ?", (token,)).fetchone()
        
        # 2. TRANCA DE SEGURANÇA: Verifica se este NOME já confirmou (prevenção extra)
        check_nome = conn.execute("SELECT id FROM confirmacoes WHERE nome = ?", (nome_real,)).fetchone()

        if (check_token and check_token['status'] == 'confirmado') or check_nome:
            registrar_log(request.remote_addr, request.user_agent.string, "Tentativa de Re-confirmação", nome_real)
            flash(f"Ops! {nome_real}, sua confirmação já foi registrada anteriormente. 😉")
            return redirect(url_for('sucesso'))

        # Se passou pelas trancas, processa a confirmação normal
        registrar_log(request.remote_addr, request.user_agent.string, f"Respondeu: {presenca}", nome_real)

        if presenca == "Sim":
            fralda = request.form.get("tamanho_fralda")
            mimo = request.form.get("mimo_extra")
            if not mimo or mimo.strip() == "": mimo = "Nenhum"
        else:
            fralda = "N/A"
            mimo = "N/A"
        
        data_confirmacao = datetime.now().strftime("%d/%m/%Y %H:%M")

        # Salva o resultado
        conn.execute("""
            INSERT INTO confirmacoes (nome, fralda, mimo, presenca, ip_address, user_agent, data)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (nome_real, fralda, mimo, presenca, request.remote_addr, request.user_agent.string, data_confirmacao))
        
        # Atualiza o convite para 'confirmado' para invalidar o token
        conn.execute("UPDATE convites SET status = 'confirmado' WHERE codigo_unico = ?", (token,))
        conn.commit()

    flash(f"Obrigado, {nome_real}! Sua resposta foi salva.")
    return redirect(url_for('sucesso'))
@app.route("/sucesso")
def sucesso():
    return render_template("sucesso.html")

# --- ADMINISTRAÇÃO ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form.get('senha') == SENHA_ADMIN:
            session['logado'] = True
            return redirect('/admin')
        return render_template('login.html', erro="Senha incorreta!")
    return render_template('login.html')

@app.route("/admin")
def admin():
    if not session.get('logado'): return redirect('/login') 
    
    dados = ler_confirmacoes()
    
    with conectar_banco() as conn:
        cursor = conn.execute("SELECT * FROM logs_seguranca ORDER BY timestamp DESC LIMIT 20")
        logs = [dict(row) for row in cursor.fetchall()]

    confirmados_sim = sum(1 for c in dados if str(c['presenca']).capitalize() == "Sim")
    confirmados_nao = len(dados) - confirmados_sim
    resumo_fraldas = {"P": 0, "M": 0, "G": 0}
    for c in dados:
        if str(c['presenca']).capitalize() == "Sim":
            t = str(c['fralda']).upper()
            if t in resumo_fraldas: resumo_fraldas[t] += 1
                
    return render_template("admin.html", convidados=dados, sim=confirmados_sim, nao=confirmados_nao, fraldas=resumo_fraldas, logs=logs)

@app.route("/admin/gerar_link", methods=["POST"])
def admin_gerar_link():
    if not session.get('logado'): return redirect('/login')
    nome = request.form.get("nome_novo_convidado")
    if nome:
        token = gerar_novo_convite(nome)
        flash(f"Link gerado para {nome}: /convite/{token}")
    return redirect(url_for('admin'))

@app.route("/logout")
def logout():
    session.pop('logado', None)
    return redirect(url_for('login'))

@app.route("/download")
def download():
    if not session.get('logado'): return redirect('/login')
    dados = ler_confirmacoes()
    df = pd.DataFrame(dados)
    df.to_excel("confirmacoes.xlsx", index=False)
    return send_file("confirmacoes.xlsx", as_attachment=True)

@app.route("/excluir/<nome>")
def excluir(nome):
    if not session.get('logado'): return redirect('/login')
    excluir_confirmacao(nome)
    return redirect(url_for('admin'))

if __name__ == "__main__":
    app.run(debug=True)