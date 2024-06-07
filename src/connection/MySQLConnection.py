import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from config.logger import logger

load_dotenv()

MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_PORT = int(os.getenv("MYSQL_PORT"))
MYSQL_USERNAME = os.getenv("MYSQL_USERNAME")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")


class MySQLConnection:
    def __init__(self, database):
        self.database = database
        try:
            self.engine = create_engine(
                f"mysql://{MYSQL_USERNAME}:{MYSQL_PASSWORD}@"
                f"{MYSQL_HOST}:{MYSQL_PORT}/{database}"
            )

        except Exception as e:
            logger.log("info", f"Erro ao conectar com o banco de dados. {e}")


    def execute_insert(self, query):
        try:
            with self.engine.connect() as connection:
                connection.execute(text(query))
                connection.commit()
                logger.log("info", f"Query de insert executada com sucesso.")
        except Exception as e:
            logger.log("error", "Erro ao executar query de insert. {e}")


    def get_connection(self):
        return self.engine.connect()
    

    def close_connection(self):
        self.engine.dispose()
        logger.log("info", f"Conexão com o banco de {self.database} dados encerrada.")


    def return_dict(self, obj):
        return {col.name: getattr(obj, col.name) for col in obj.__table__.columns}


    def execute_select_query(self, query):
        try:
            with self.engine.connect() as connection:
                result = connection.execute(text(query))
                results = result.fetchall()
                return results
        except Exception as e:
            logger.log("error", f"Erro ao executar query de select. {e}")
            return []


    def execute_single_select_query(self, query):
        try:
            with self.engine.connect() as connection:
                result = connection.execute(text(query))
                results = result.fetchone()
                return results
        except Exception as e:
            logger.log("error", f"Erro ao executar query de select. {e}")
            return []


    def get_residencias(self):
        query = """
            SELECT 
	            rs.id,
                en.bairro,
                en.cidade
            FROM
	            home_sentinel.residencia rs
		    JOIN home_sentinel.endereco en ON en.residencia_id = rs.id WHERE rs.id;"""

        return self.execute_select_query(query)