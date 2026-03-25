import pandas as pd
import os

NOME_PLANILHA = "lista_ayla.xlsx"

if os.path.exists(NOME_PLANILHA):
    df = pd.read_excel(NOME_PLANILHA)
    
    # 1. Mostra no terminal as colunas que ele ENCONTROU (ajuda no debug)
    print(f"Colunas encontradas: {list(df.columns)}")

    # 2. Vamos tentar encontrar a coluna de presença, mesmo que tenha acento ou espaço
    # Procuramos algo que contenha 'presen' (cobre presenca e presença)
    col_presenca = [c for c in df.columns if 'presen' in c.lower()]
    col_fralda = [c for c in df.columns if 'fralda' in c.lower()]
    col_mimo = [c for c in df.columns if 'mimo' in c.lower()]

    if col_presenca and col_fralda and col_mimo:
        p = col_presenca[0]
        f = col_fralda[0]
        m = col_mimo[0]

        # 3. Faz a limpeza usando os nomes REAIS das colunas
        df.loc[df[p].astype(str).str.contains('Não', na=False), [f, m]] = "Não se aplica"
        
        df.to_excel(NOME_PLANILHA, index=False)
        print(f"✅ Sucesso! Coluna '{p}' usada para filtrar.")
    else:
        print("❌ Não encontrei as colunas necessárias. Verifique o cabeçalho do Excel.")
else:
    print("❌ Planilha não encontrada.")