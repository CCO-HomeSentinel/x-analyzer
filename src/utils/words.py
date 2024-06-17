from unidecode import unidecode
import re

FILE_PATH = 'src/assets/palavras.txt'

def remove_accents(word):
    return re.sub(r'[^a-zA-Z]', ' ', unidecode(word))

def read_and_process_file():
    with open(FILE_PATH, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    words = [line.strip() for line in lines]
    return [remove_accents(word) for word in words]