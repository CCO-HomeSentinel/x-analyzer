from services.web_crawler import get_tweets, start_driver, close_driver
from services.text_process import analyze
from connections.MySQLConnection import MySQLConnector
from config.logger import logger
import pandas as pd

def main():
    logger.log("info", "Iniciando web crawler")
    hs_conn = MySQLConnector()
    hs_conn.connect()
    residencias = hs_conn.get_residencias()
    hs_conn.close()

    tweets = []
    start_driver()

    for residencia in residencias:
        id = residencia[0]
        bairro = residencia[1]
        cidade = residencia[2]
        tweets.extend(get_tweets(id, bairro, cidade))

    close_driver()

    logger.log("info", "Iniciando análise dos tweets")
    for tweet in tweets:
        sentiment, is_palavrao, palavra_chave = analyze(tweet.texto)
        tweet.sentiment = sentiment
        tweet.is_palavrao = is_palavrao
        tweet.palavra_chave = palavra_chave


    data = [
    {
        "nome": tweet.nome,
        "texto": tweet.texto,
        "data_post": tweet.data_post,
        "palavra_chave": tweet.palavra_chave,
        "is_palavrao": tweet.is_palavrao,
        "residencia_id": tweet.residencia_id,
        "sentiment": tweet.sentiment,
        "id_ref": tweet.id_ref
    }
    for tweet in tweets
    ]


    df = pd.DataFrame(data)
    df.to_csv("tweets.csv", index=False)

    # x_conn = MySQLConnector(is_x_db=True)
    # x_conn.connect()
    # x_conn.save_tweets(tweets)
    # x_conn.close()
    
    logger.log("info", "Web crawler feito com sucesso")

if __name__ == "__main__":
    main()