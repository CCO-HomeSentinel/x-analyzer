import re
import nltk
from dotenv import load_dotenv
import os
# from utils.levenshtein import find_closest_word
from unidecode import unidecode
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

load_dotenv()

nltk.download('stopwords')
nltk.download('wordnet')

lematizer = WordNetLemmatizer()
stop_words = set(stopwords.words('portuguese'))

# Vocabulário padrão
positive_words = [
    'bom', 'otimo', 'excelente', 'maravilhoso', 'fantastico', 'positivo',
    'feliz', 'alegria', 'amor', 'gostar', 'melhor', 'incrivel', 'brilhante'
]

negative_words = [
    'ruim', 'pessimo', 'horrivel', 'negativo', 'triste', 'raiva', 'odio',
    'pior', 'pobre', 'nojento', 'medonho', 'aterrador', 'abominavel'
]

# Vocabulário da regra de negócio
NEGATIVE_WORDS_ENV = os.getenv('NEGATIVE_WORDS', '').split(',')
POSITIVE_WORDS_ENV = os.getenv('POSITIVE_WORDS', '').split(',')
BAD_WORDS_ENV = os.getenv('BAD_WORDS', '').split(',')
KEYWORDS = os.getenv('KEYWORDS', '').split(',')

positive_words.extend(POSITIVE_WORDS_ENV)
negative_words.extend(NEGATIVE_WORDS_ENV)
negative_words.extend(BAD_WORDS_ENV)

all_words = positive_words + negative_words + NEGATIVE_WORDS_ENV + POSITIVE_WORDS_ENV + BAD_WORDS_ENV

# TO DO: Implementar Levenshtein com um bom desempenho
def preprocess_text(text):
    text = re.sub(r'[^a-zA-Z]', ' ', unidecode(text))
    text = text.lower()
    words = text.split()
    words = [lematizer.lemmatize(word) for word in words if word not in stop_words]
    text = ' '.join(words)
    return text

def tokenize(text):
    tokens = []
    text = preprocess_text(text)
    words = text.split()
    
    for word in words:
        token = {
            'text': word,
            'types': []
        }
        
        if word in positive_words:
            token['types'].append('positive')
        if word in negative_words:
            token['types'].append('negative')
        if word in KEYWORDS:
            token['types'].append('keyword')
        if word in BAD_WORDS_ENV:
            token['types'].append('bad_word')
        
        if not token['types']:
            token['types'].append('other')
        
        tokens.append(token)
    
    return tokens

def analyze(text):
    tokens = tokenize(text)
    
    positive_count = sum(1 for token in tokens if 'positive' in token['types'])
    negative_count = sum(1 for token in tokens if 'negative' in token['types'])
    has_bad_word = any('bad_word' in token['types'] for token in tokens)
    keyword = next((token['text'] for token in tokens if 'keyword' in token['types']), None)
    
    if positive_count > negative_count:
        return 'positive', has_bad_word, keyword
    elif negative_count > positive_count:
        return 'negative', has_bad_word, keyword
    else:
        return 'neutral', has_bad_word, keyword