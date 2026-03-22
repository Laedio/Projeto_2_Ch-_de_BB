import openpyxl
import os
from datetime import datetime

# 1. Definimos o nome EXATO do arquivo que você criou na pasta
NOME_EXCEL = 'lista_ayla.xlsx'

def inicializar_banco():
    # Apenas verifica se você criou o arquivo como combinamos
    if not os.path.exists(NOME_EXCEL):
        print(f"ERRO: O arquivo {NOME_EXCEL} não foi encontrado na pasta!")
    else:
        print("Planilha do Excel detectada e pronta para uso!")

import re # Certifique-se de que o 're' está importado no topo do arquivo!

def salvar_confirmacao(nome, fralda, mimo, presenca):
    # 1. REMOVE ESPAÇOS: O .strip() tira espaços invisíveis do início e do fim
    nome_limpo = nome.strip()

    # 2. TRAVA DE SEGURANÇA: Se após o strip o nome estiver vazio, para tudo!
    if not nome_limpo:
        print("Erro: Tentativa de salvar um nome vazio ou apenas com espaços.")
        return  # Sai da função sem salvar nada no Excel

    # 3. REMOVE NÚMEROS: O regex re.sub garante que 'João123' vire 'João'
    nome_sem_numeros = re.sub(r'[0-9]', '', nome_limpo)

    # 4. FORMATAÇÃO: Deixa a primeira letra de cada nome maiúscula (Ex: laedio -> Laedio)
    nome_final = nome_sem_numeros.title()

    # --- AGORA SEGUE O CÓDIGO NORMAL DE SALVAR NO EXCEL ---
    book = openpyxl.load_workbook(NOME_EXCEL)
    folha = book.active
    
    # Encontra a linha vazia
    linha_vazia = 2 
    while folha.cell(row=linha_vazia, column=2).value is not None:
        linha_vazia += 1

    # Salva os dados (Usando o 'nome_final' que limpamos acima)
    folha.cell(row=linha_vazia, column=1).value = datetime.now().strftime('%d/%m/%Y %H:%M')
    folha.cell(row=linha_vazia, column=2).value = nome_final # Nome limpo aqui!
    folha.cell(row=linha_vazia, column=3).value = fralda
    folha.cell(row=linha_vazia, column=4).value = mimo if mimo else "Nenhum"
    folha.cell(row=linha_vazia, column=5).value = presenca
    
    book.save(NOME_EXCEL)
    print(f"Sucesso: {nome_final} foi salvo na planilha.")

def ler_confirmacoes():
    if not os.path.exists(NOME_EXCEL):
        return []

    book = openpyxl.load_workbook(NOME_EXCEL)
    folha = book.active
    
    lista_convidados = []
    
    # min_row=2 pula o cabeçalho colorido
    for linha in folha.iter_rows(min_row=2, values_only=True):
        # linha[0]=Data, [1]=Nome, [2]=Fralda, [3]=Mimo, [4]=Presença
        if linha[1]: 
            convidado = {
                'data': linha[0],
                'nome': linha[1],
                'fralda': linha[2],
                'mimo': linha[3],
                'presenca': linha[4]
            }
            lista_convidados.append(convidado)
            
    return lista_convidados