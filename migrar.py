import pandas as pd
import os
from database import inicializar_banco, salvar_confirmacao

def migrar_dados_antigos():
    arquivo_excel = "lista_ayla.xlsx"
    
    if not os.path.exists(arquivo_excel):
        print(f"❌ Arquivo {arquivo_excel} não encontrado.")
        return

    # Garante que o Banco de Dados SQL (tabelas) existe
    inicializar_banco()

    # Lê o Excel
    df = pd.read_excel(arquivo_excel)
    
    print(f"--- Colunas detectadas no seu Excel: {list(df.columns)} ---")
    
    for index, linha in df.iterrows():
        # MAPEAMENTO EXATO BASEADO NO QUE VOCÊ ME PASSOU:
        nome = linha.get('Nome')
        fralda = linha.get('Fralda')
        presenca = linha.get('Presença')
        
        # BUSCA NA COLUNA 'Mimo' (Coluna D do seu Excel)
        # Se estiver vazio ou for NaN, vira "Nenhum"
        mimo_bruto = linha.get('Mimo')
        mimo = str(mimo_bruto) if pd.notna(mimo_bruto) else "Nenhum"

        if nome:
            salvar_confirmacao(str(nome), str(fralda), mimo, str(presenca))
            print(f"✅ {nome} migrado com o mimo: {mimo}")

    print("--- Migração Concluída com Sucesso! ---")

if __name__ == "__main__":
    migrar_dados_antigos()