import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

load_dotenv()

database_url = os.getenv("database_url")

#é responsável por criar a conexão que o SQLAlchemy utilizará para conversar com o PostgreSQL.
engine = create_engine(database_url)

#cria uma "fábrica" de sessões.
SessionLocal = sessionmaker(
    bind = engine,
    autoflush = False,
    autocommit = False
)

#será a classe-base dos nossos modelos.
class Base(DeclarativeBase):
    pass

#Essa função será responsável por fornecer uma conexão/sessão com o banco para cada requisição.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()