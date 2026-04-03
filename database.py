import sqlite3
import os
import re
import uuid
from datetime import datetime

# Nome do banco de dados
NOME_BANCO = 'dados_ayla.db'

def conectar_banco():
    """Cria uma conexão com o SQLite."""
    conn = sqlite3.connect(NOME_BANCO)
    conn.row_factory = sqlite3.Row
    return conn

def inicializar_banco():
    """Cria a infraestrutura de tabelas necessária."""
    with conectar_banco() as conn:
        # TABELA 1: Confirmacoes - AJUSTADA PARA COLUNA 'data'
        conn.execute('''
            CREATE TABLE IF NOT EXISTS confirmacoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                fralda TEXT,
                mimo TEXT,
                presenca TEXT,
                ip_address TEXT,
                user_agent TEXT,
                data TEXT  -- Nome exato que o app.py procura
            )
        ''')

        # TABELA 2: Convites únicos
        conn.execute('''
            CREATE TABLE IF NOT EXISTS convites (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                codigo_unico TEXT UNIQUE NOT NULL,
                nome_convidado TEXT NOT NULL,
                status TEXT DEFAULT 'pendente',
                expira_em TIMESTAMP
            )
        ''')

        # TABELA 3: Segurança (ADICIONADA COLUNA USUARIO)
        conn.execute('''
            CREATE TABLE IF NOT EXISTS logs_seguranca (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ip TEXT,
                user_agent TEXT,
                endpoint TEXT,
                usuario TEXT DEFAULT 'Visitante', -- <--- NOVA COLUNA
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
    print("🚀 Banco de dados atualizado!")

def salvar_confirmacao(nome, fralda, mimo, presenca, ip="N/A", ua="N/A"):
    """Salva a confirmação (Usada internamente ou via formulário)."""
    nome_final = re.sub(r'[0-9]', '', nome.strip()).title()
    mimo_final = mimo if mimo else "N/A"
    data_agora = datetime.now().strftime("%d/%m/%Y %H:%M")
    
    with conectar_banco() as conn:
        conn.execute("""
            INSERT INTO confirmacoes (nome, fralda, mimo, presenca, ip_address, user_agent, data)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (nome_final, fralda, mimo_final, presenca, ip, ua, data_agora))
        conn.commit()

def ler_confirmacoes():
    if not os.path.exists(NOME_BANCO):
        return []
    with conectar_banco() as conn:
        cursor = conn.execute("SELECT * FROM confirmacoes ORDER BY id DESC")
        return [dict(row) for row in cursor.fetchall()]

def excluir_confirmacao(nome):
    with conectar_banco() as conn:
        conn.execute("DELETE FROM confirmacoes WHERE nome = ?", (nome,))
        conn.commit()
        return True

def registrar_log(ip, ua, endpoint, usuario="Visitante"):
    """Agora aceita o nome do usuário para o log."""
    try:
        with conectar_banco() as conn:
            conn.execute("INSERT INTO logs_seguranca (ip, user_agent, endpoint, usuario) VALUES (?, ?, ?, ?)", 
                         (ip, ua, endpoint, usuario))
            conn.commit()
    except Exception as e:
        print(f"⚠️ Erro ao registrar log: {e}")

def gerar_novo_convite(nome_convidado):
    token_curto = str(uuid.uuid4())[:4]
    slug = re.sub(r'[^a-zA-Z0-9]', '-', nome_convidado.lower())
    codigo = f"{slug}-{token_curto}"
    
    with conectar_banco() as conn:
        conn.execute("INSERT INTO convites (codigo_unico, nome_convidado) VALUES (?, ?)", 
                      (codigo, nome_convidado))
        conn.commit()
    return codigo