import sqlite3
import os
import re
from datetime import datetime

# 1. Definimos o nome do arquivo do Banco de Dados
NOME_BANCO = 'dados_ayla.db'

def conectar_banco():
    """Cria uma conexão com o SQLite e permite acessar colunas pelo nome."""
    conn = sqlite3.connect(NOME_BANCO)
    conn.row_factory = sqlite3.Row  # Isso permite usar convidado['nome'] em vez de linha[1]
    return conn

def inicializar_banco():
    """Cria a tabela de convidados se ela ainda não existir."""
    with conectar_banco() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS convidados (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                data TEXT NOT NULL,
                nome TEXT NOT NULL,
                fralda TEXT,
                mimo TEXT,
                presenca TEXT NOT NULL
            )
        """)
    print("Banco de Dados SQL detectado e pronto para uso!")

def salvar_confirmacao(nome, fralda, mimo, presenca):
    # --- MANTEMOS SUA LÓGICA DE LIMPEZA ---
    nome_limpo = nome.strip()
    if not nome_limpo:
        print("Erro: Tentativa de salvar um nome vazio.")
        return 

    nome_sem_numeros = re.sub(r'[0-9]', '', nome_limpo)
    nome_final = nome_sem_numeros.title()

    # --- AGORA SALVAMOS NO SQLITE EM VEZ DE OPENPYXL ---
    data_atual = datetime.now().strftime('%d/%m/%Y %H:%M')
    mimo_final = mimo if mimo else "Nenhum"

    with conectar_banco() as conn:
        conn.execute("""
            INSERT INTO convidados (data, nome, fralda, mimo, presenca)
            VALUES (?, ?, ?, ?, ?)
        """, (data_atual, nome_final, fralda, mimo_final, presenca))
    
    print(f"Sucesso: {nome_final} foi salvo no Banco de Dados SQL.")

def ler_confirmacoes():
    """Lê todos os dados do banco e retorna como uma lista de dicionários."""
    if not os.path.exists(NOME_BANCO):
        return []

    with conectar_banco() as conn:
        cursor = conn.execute("SELECT * FROM convidados ORDER BY id DESC")
        # Transformamos as linhas do SQL em dicionários para o seu admin.html continuar funcionando
        return [dict(row) for row in cursor.fetchall()]

def excluir_confirmacao(id_ou_nome):
    """
    Exclui um convidado. 
    DICA: Agora você pode excluir pelo ID (muito mais seguro) ou pelo nome.
    """
    with conectar_banco() as conn:
        # Tenta excluir pelo nome para manter compatibilidade com o que fizemos antes
        conn.execute("DELETE FROM convidados WHERE nome = ?", (id_ou_nome,))
        return True