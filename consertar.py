import sqlite3

conn = sqlite3.connect('banco.db')
cursor = conn.cursor()
try:
    # Este comando adiciona a coluna que está faltando
    cursor.execute("ALTER TABLE confirmacoes ADD COLUMN data TEXT")
    conn.commit()
    print("✅ Coluna 'data' adicionada! O erro do convidado sumiu.")
except Exception as e:
    print(f"❌ Erro: {e}")
finally:
    conn.close()