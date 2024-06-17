from selenium.webdriver.common.by import By
from lib.Selenium import WebDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from datetime import datetime
import os
from dotenv import load_dotenv
from domain.Tweet import Tweet
from config.logger import logger

load_dotenv()

USER = os.environ.get("USER")
PASSWORD = os.environ.get("PASSWORD")
SEARCH_URL = os.environ.get("X_SEARCH_URL")
SEARCH_FILTER = os.environ.get("X_SEARCH_FILTER")
KEYWORDS = os.environ.get("KEYWORDS", '').split(",")
LIMIT_SCROLL = int(os.environ.get("LIMIT_SCROLL"))

driver = None
logged_in = False

def start_driver():
    global driver
    driver = WebDriverManager()
    logger.log("info", "Driver iniciado com sucesso")

def get_tweets(residencia_id, bairro, cidade):
    keyword_list = " OR ".join(KEYWORDS)
    query = f"{bairro} {cidade} ({keyword_list})"
    logger.log("info", f"Iniciando buscas - query: {query}")
    url_search = f'{SEARCH_URL}{query}{SEARCH_FILTER}'
    driver.open_url(url_search)

    if not logged_in:
        _login()

    last_height = 0
    tweets = []
    tweets_ids = []
    count = 1
    cont_erros = 0

    while count <= LIMIT_SCROLL:

        # Encontrando todos os elementos que correspondem a artigos de tweets
        new_tweets = driver.find_elements(By.XPATH, "//article[@role='article']")

        for new_tweet in new_tweets:
            if new_tweet.id not in tweets_ids:
                try:
                    nome = new_tweet.find_element(By.XPATH, ".//div[@data-testid='User-Name']/div[2]/div/div/a/div/span").text
                    texto = new_tweet.find_element(By.XPATH, ".//div[@data-testid='tweetText']").text
                    data_post = new_tweet.find_element(By.XPATH, ".//time").get_attribute("datetime")
                    data_post = datetime.fromisoformat(data_post.replace('T', ' ')[:-1])
                    id = new_tweet.id
                    tweets_ids.append(id)

                    tweet = Tweet(nome, texto, data_post, residencia_id, id)
                    tweets.append(tweet)
                except Exception as ex:
                    cont_erros += 1
                    logger.log("error", f"Ocorreu um erro ao mapear um tweet: {ex}")

        new_height = _scroll_and_load_tweets(driver, last_height)

        if new_height == last_height:
            break

        count += 1
        last_height = new_height

    logger.log("info", f"Tweets encontrados: {len(tweets)}")
    return tweets

def close_driver():
    driver.close()

def _login():
    global logged_in

    driver.send_keys(By.NAME, 'text', USER)
    driver.click_element(By.XPATH, '//*[@id="layers"]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div/div/div/button[2]')
    driver.send_keys(By.NAME, 'password', PASSWORD)
    driver.click_element(By.XPATH, '//*[@data-testid="LoginForm_Login_Button"]')

    logged_in = True
    logger.log("info", "Login feito com sucesso")

def _scroll_and_load_tweets(driver, last_height):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    
    try:
        WebDriverWait(driver, 10).until(
            lambda driver: driver.execute_script("return document.body.scrollHeight") != last_height
        )
    except Exception as ex:
        return last_height
    
    # Obtenha a nova altura da página
    new_height = driver.execute_script("return document.body.scrollHeight")
    return new_height