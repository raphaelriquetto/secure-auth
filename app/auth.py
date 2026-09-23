import os
import jwt
from dotenv import load_dotenv
from argon2 import PasswordHasher
from datetime import datetime, timedelta

load_dotenv()

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")

password_hasher = PasswordHasher()

#recebe a senha original e retorna o hash
def hash_password(password: str) -> str:
    return password_hasher.hash(password)

#recebe a senha que o usuário digitou e o hash que está armazenado no banco
def verify_password(password: str, password_hash: str) -> bool:
    try:
        password_hasher.verify(password_hash, password)
        return True
    except Exception:
        return False

#recebe o id do usuário e retorna um token JWT
def create_access_token(user_id: int) -> str:
    expiration = datetime.utcnow() + timedelta(minutes=30)
    payload = {
        "sub": str(user_id),
        "exp": expiration
    }

    token = jwt.encode(
        payload,
        JWT_SECRET_KEY,
        algorithm="HS256"
    )

    return token

#responsável por pegar o JWT e verificar se é valido
def decode_acess_token(token: str) -> dict:
    payload = jwt.decode(
        token,
        JWT_SECRET_KEY,
        algorithms=["HS256"]
    )
    return payload