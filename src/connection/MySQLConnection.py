import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

load_dotenv()

MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_PORT = int(os.getenv("MYSQL_PORT"))
MYSQL_USERNAME = os.getenv("MYSQL_USERNAME")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")


class MySQLConnection:
    def __init__(self, database):
        try:
            self.engine = create_engine(
                f"mysql://{MYSQL_USERNAME}:{MYSQL_PASSWORD}@"
                f"{MYSQL_HOST}:{MYSQL_PORT}/{database}"
            )
            Session = sessionmaker(bind=self.engine)
            self.session = Session()

        except Exception as e:
            print(f"Erro ao conectar com o banco de dados. {e}")

    def get_session(self):
        return self.session

    def close_connection(self):
        self.session.close()

    def execute_insert(self, query):
        try:
            with self.engine.connect() as connection:
                connection.execute(text(query))
                connection.commit()
                print("Query de insert executada com sucesso.")
        except Exception as e:
            print(f"Erro ao executar query de insert. {e}")

    def get_connection(self):
        return self.engine.connect()

    def return_dict(self, obj):
        return {col.name: getattr(obj, col.name) for col in obj.__table__.columns}

    def execute_select_query(self, query):
        try:
            with self.engine.connect() as connection:
                result = connection.execute(text(query))
                results = result.fetchall()
                return results
        except Exception as e:
            print("Erro ao executar query de select. {e}")
            return []

    def execute_single_select_query(self, query):
        try:
            with self.engine.connect() as connection:
                result = connection.execute(text(query))
                results = result.fetchone()
                return results
        except Exception as e:
            print(f"Erro ao executar query de select. {e}")
            return []

    def get_residencias(self):
        query = """
            SELECT 
	            rs.id,
                en.bairro,
                en.cidade
            FROM
	            home_sentinel.residencia rs
		    JOIN home_sentinel.endereco en ON en.residencia_id = rs.id WHERE rs.id IN (1, 2);"""

        return self.execute_select_query(query)