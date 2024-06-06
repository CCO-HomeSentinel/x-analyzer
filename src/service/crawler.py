import os
import sys
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from unidecode import unidecode
from dotenv import load_dotenv
import lexer

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from connection.MySQLConnection import MySQLConnection

load_dotenv()

DRIVER_GUI = os.getenv("DRIVER_GUI") in ("True", "true", "1")

X_USERNAME = os.getenv("X_USERNAME")
X_PASSWORD = os.getenv("X_PASSWORD")
X_KEYWORDS = os.getenv("X_KEYWORDS").split(",")
X_LOGIN_URL = os.getenv("X_LOGIN_URL")
X_SEARCH_URL = os.getenv("X_SEARCH_URL")
X_SCROLL_LIMIT = int(os.getenv("X_SCROLL_LIMIT"))

MYSQL_DATABASE_HS = os.getenv("MYSQL_DATABASE_HS")
MYSQL_DATABASE_X = os.getenv("MYSQL_DATABASE_X")

IDS_IGNORE = os.getenv("IDS_IGNORE").split(",")
for i in range(len(IDS_IGNORE)):
    IDS_IGNORE[i] = int(IDS_IGNORE[i])

global DRIVER

if DRIVER_GUI:
    DRIVER = webdriver.Chrome()
else:
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920x1080")
    chrome_options.add_argument("--start-maximized")

    DRIVER = webdriver.Chrome(options=chrome_options)


def login():
    DRIVER.get(X_LOGIN_URL)
    sleep(8)
    username_html = DRIVER.find_element(By.CLASS_NAME, "r-30o5oe")
    username_html.send_keys(X_USERNAME)
    username_html.send_keys(Keys.RETURN)

    sleep(2.5)
    password_html = DRIVER.find_element(By.NAME, "password")
    password_html.send_keys(X_PASSWORD)
    password_html.send_keys(Keys.RETURN)

    sleep(3)


def track(keyword, bairro, cidade):
    sleep(5)
    DRIVER.get(X_SEARCH_URL + keyword + " " + bairro + " " + cidade)

    sleep(5)
    latest_tab = DRIVER.find_element(By.LINK_TEXT, "Mais recentes")
    latest_tab.click()
    sleep(3)

    tweets = []

    for down in range(X_SCROLL_LIMIT):
        DRIVER.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        sleep(3)
        soup = BeautifulSoup(DRIVER.page_source, "html.parser")
        bloco = soup.find_all("article", {"role": "article"})

        for b in bloco:
            tweets.append(b)

    data = {"tweets": []}

    for tweet in tweets:
        try:
            tweet_text = tweet.find("div", {"lang": True})
            if tweet_text:
                text = unidecode(tweet_text.get_text()).replace("\n", " ").replace("\r", " ").replace("\t", " ").replace('"', " ").strip()
                text = " ".join(text.split())
                text = " ".join([x for x in text.split() if "http" not in x])

                user_element = tweet.find("div", {"dir": "ltr"})
                username = user_element.get_text().replace('@', '')

                date_element = tweet.find("time")
                date = date_element['datetime']
                

                data["tweets"].append({
                    "username": username if username else "N/A",
                    "date": date if date else "N/A",
                    "text": text if text else "N/A",
                })
        except Exception as e:
            print(f"Erro: {e}")

    return data['tweets']


def main():
    login()
    hs_conn = MySQLConnection(MYSQL_DATABASE_HS)
    x_conn = MySQLConnection(MYSQL_DATABASE_X)
    residencias = hs_conn.get_residencias()
    hs_conn.close_connection()

    for residencia in residencias:
        id = residencia[0]
        bairro = residencia[1]
        cidade = residencia[2]

        if id in IDS_IGNORE:
            continue

        for keyword in X_KEYWORDS:
            
            print(f"Buscando por: [{keyword}] [{id}] - [{bairro}], [{cidade}]")
            dados = track(keyword, bairro, cidade)
            
            query = "INSERT INTO x_sentinel.tweet (nome, data_post, texto, is_palavrao, palavra_chave, residencia_id) VALUES"
            for dado in dados:
                dado['username'] = dado['username'].replace("'", "").replace('"', "")
                dado['date'] = dado['date'].replace("'", "").replace('"', "")
                dado['text'] = dado['text'].replace("'", "").replace('"', "")

                contem = 1 if lexer.analisar(dado['text']) else 0
                query += f"""
                    ('{dado['username']}', '{dado['date']}', '{dado['text']}' , {contem}, '{keyword}', {id}),""";
            query = query[:-1] + ";"    
            x_conn.execute_insert(query)

    x_conn.close_connection()
    DRIVER.close()


if __name__ == "__main__":
    main()