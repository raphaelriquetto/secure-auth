from .database import Base, engine
from .models import User, RevokedToken

Base.metadata.create_all(bind=engine)

print("Tabelas verificada/criadas com sucesso!")