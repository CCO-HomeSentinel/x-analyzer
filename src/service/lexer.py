import os
import re
import unicodedata
from dotenv import load_dotenv

load_dotenv()


def remover_acentuacoes(texto):
    return ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')


BAD_WORDS = os.getenv("BAD_WORDS").split(",")
BAD_WORDS = [remover_acentuacoes(p).lower() for p in BAD_WORDS]

# Definindo os padrões para os tokens
especificacoes_tokens = [
    ('NUMERO',   r'\d+(\.\d*)?'),   # Números inteiros ou decimais
    ('UNIDADE',  r'[°C|%|Pa]'),     # Unidades de medida
    ('ID',       r'[a-zA-Z_]\w*'),  # Identificadores (nomes de sensores)
    ('DOISPONTOS', r':'),           # Dois pontos
    ('IGNORAR',  r'[ \t]+'),        # Espaços e tabulações
    ('NOVA_LINHA', r'\n'),          # Quebras de linha
    ('ERRO',     r'.'),             # Qualquer outro caractere
]

padrao_tokens = re.compile('|'.join(f'(?P<{nome}>{padrao})' for nome, padrao in especificacoes_tokens))


def analisar(texto):
    texto = remover_acentuacoes(texto)
    
    tokens = []
    for correspondencia in padrao_tokens.finditer(texto):
        tipo = correspondencia.lastgroup
        valor = correspondencia.group(tipo)
        if tipo == 'NUMERO':
            valor = float(valor) if '.' in valor else int(valor)
        elif tipo == 'NOVA_LINHA':
            pass
        elif tipo == 'IGNORAR':
            continue
        elif tipo == 'ERRO':
            print(f'Caractere inesperado: {valor}')
        tokens.append((tipo, valor))
    
    for _, valor in tokens:
        if isinstance(valor, str) and valor.lower() in BAD_WORDS:
            return True
    
    return False


def logar_tokens(tokens):
    for token in tokens:
        print(token)


def contem_palavrao(texto):
    texto = remover_acentuacoes(texto).lower()
    palavras = texto.split()
    for palavra in palavras:
        if palavra in BAD_WORDS:
            return True
    return False