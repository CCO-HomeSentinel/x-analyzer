import mysql.connector
from dotenv import load_dotenv
import os
from config.logger import logger

load_dotenv(override=True)

HOST = os.environ.get('MYSQL_HOST')
USERNAME = os.environ.get('MYSQL_USER')
PASSWORD = os.environ.get('MYSQL_PASSWORD')
DATABASE_HS = os.environ.get('MYSQL_DATABASE_HS')
DATABASE_X = os.environ.get('MYSQL_DATABASE_X')

print(HOST)

class MySQLConnector:
    def __init__(self, is_x_db = False):
        logger.log("info", f"Conexão com MySQL setada com o bannco de dados: {DATABASE_X if is_x_db else DATABASE_HS}")
        self.host = HOST
        self.username = USERNAME
        self.password = PASSWORD
        self.database = DATABASE_X if is_x_db else DATABASE_HS
        self.connection = None
        self.cursor = None

    def connect(self):
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.username,
                password=self.password,
                database=self.database
            )

            if self.connection.is_connected():
                self.cursor = self.connection.cursor()
                logger.log("info", "Conexão feita com sucesso")
        except mysql.connector.Error as error:
            logger.log("error", f"Ocorreu um erro ao se conectar com o banco de dados: {error}")

    def save_tweets(self, tweets):
        if self.database == DATABASE_X:
            tweet_data = [(tweet.nome, tweet.texto, tweet.data_post, tweet.palavra_chave, tweet.is_palavrao, tweet.residencia_id, tweet.sentiment) for tweet in tweets]
            insert_query = "INSERT INTO tweet (nome, texto, data_post, palavra_chave, is_palavrao, residencia_id, sentiment) VALUES (%s, %s, %s, %s, %s, %s, %s)"
            self.cursor.executemany(insert_query, tweet_data)
            self.connection.commit()
            logger.log("info", "Tweets salvados com sucesso")

    def get_residencias(self):
        if self.database == DATABASE_HS:
            get_query = """
                SELECT 
                    rs.id,
                    en.bairro,
                    ci.nome
                FROM
                    home_sentinel.residencia rs
                JOIN 
                    home_sentinel.endereco en ON en.id = rs.id 
                JOIN 
                    home_sentinel.cidade ci ON ci.id = en.id;"""
            
            self.cursor.execute(get_query)
            logger.log("info", "Residências buscadas com sucesso")
            return self.cursor.fetchall()
        
        return None


    def close(self):
        try:
            if self.connection.is_connected():
                self.cursor.close()
                self.connection.close()
                logger.log("info", "Conexão com o banco de dados fechada")
        except mysql.connector.Error as error:
            logger.log("error", f"Ocorreu um erro ao fechar a conexão com o banco de dados")
        
        