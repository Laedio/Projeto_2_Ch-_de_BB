-- Script de criação da estrutura do banco
CREATE TABLE IF NOT EXISTS convidados (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    data_confirmacao DATETIME DEFAULT CURRENT_TIMESTAMP,
    nome_completo TEXT NOT NULL,
    presenca TEXT NOT NULL,
    tamanho_fralda TEXT,
    mimo_extra TEXT
);