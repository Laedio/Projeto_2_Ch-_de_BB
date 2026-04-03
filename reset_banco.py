import sqlite3
import os
from database import inicializar_banco

# 1. Deletar o banco antigo para não ter conflito de colunas
if os.path.exists('dados_ayla.db'):
    os.remove('dados_ayla.db')
    print("Arquivo antigo removido!")

# 2. Criar o banco novo com as tabelas de segurança (Log, Convites, etc)
inicializar_banco()

# 3. Inserir o seu convite de teste
conn = sqlite3.connect('dados_ayla.db')
cursor = conn.cursor()
cursor.execute("INSERT INTO convites (codigo_unico, nome_convidado) VALUES (?, ?)", 
               ('festa123', 'Laedio Parceiro'))
conn.commit()
conn.close()

print("\n✅ TUDO PRONTO!")
print("Link de teste: http://127.0.0.1:5000/convite/festa123")