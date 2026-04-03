import sqlite3
conn = sqlite3.connect('banco.db')
cursor = conn.cursor()
try:
    cursor.execute("ALTER TABLE confirmacoes ADD COLUMN data TEXT")
    conn.commit()
    print("✅ Agora o banco aceita a data! O convidado já pode confirmar.")
except:
    print("⚠️ A coluna já existia ou houve outro erro.")
conn.close()