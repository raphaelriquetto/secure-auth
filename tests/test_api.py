from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app) #cria um cliente que permite testar a aplicação FastAPI sem precisar rodar o servidor

def test_home(client):
    response = client.get("/") #faz uma requisição GET para a rota raiz da aplicação

    assert response.status_code == 200 #verifica se o status code da resposta é 200 (OK)
    assert response.json() == {"message": "SecureAuth API está funcionando!"} #verifica se o conteúdo da resposta é igual ao esperado

def test_register_user(client):
    response = client.post(
        "/auth/register",
        json={
            "name": "Usuario Teste",
            "email": "teste@example.com",
            "password": "senha123"
        }
    )

    assert response.status_code == 200
    data = response.json()

    assert data["name"] == "Usuario Teste"
    assert data["email"] == "teste@example.com"
    assert "password_hash" not in data  # Verifica se a senha não está presente na resposta
    assert "password" not in data  # Verifica se a senha não está presente na resposta

def test_register_duplicate_email(client):
    user_data = {
        "name": "Usuario Teste",
        "email": "duplicado@example.com",
        "password": "senha123"
    }

    first_response = client.post("/auth/register", json=user_data)
    second_response = client.post("/auth/register", json=user_data)

    assert first_response.status_code == 200
    assert second_response.status_code == 409
    assert second_response.json()["detail"] == "E-mail já cadastrado!"

def test_login_sucess(client):
    user_data = {
        "name": "Usuario Teste",
        "email": "login@example.com",
        "password": "senha123"
    }

    register_response = client.post("/auth/register", json=user_data)
    assert register_response.status_code == 200

    login_response = client.post(
        "/auth/login",
        json={
            "email": user_data["email"],
            "password": user_data["password"]
        }
    )
    assert login_response.status_code == 200

    data = login_response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_wrong_password(client):
    user_data = {
        "name": "Usuario Teste",
        "email": "senhaerrada@example.com",
        "password": "senha123"
    }

    client.post("/auth/register", json=user_data)

    login_response = client.post(
        "/auth/login",
        json={
            "email": user_data["email"],
            "password": "senhaerrada"
        }
    )
    assert login_response.status_code == 401
    assert login_response.json()["detail"] == "E-mail ou senha inválidos"

def test_me_without_token(client):
    response = client.get("/auth/me")
    assert response.status_code == 401

def test_me_with_valid_token(client):
    user_data = {
        "name": "Usuario Teste",
        "email": "protegido@example.com",
        "password": "senha123"
    }

    client.post("/auth/register", json=user_data)

    login_response = client.post(
        "/auth/login",
        json={
            "email": user_data["email"],
            "password": user_data["password"]
        }
    )

    token = login_response.json()["access_token"]

    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    assert response.json()["email"] == user_data["email"]

def test_me_with_invalid_token(client):
    response = client.get(
        "/auth/me",
        headers={"Authorization": "Bearer invalidtoken"}
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Token inválido"

def test_logout_revokes_token(client):
    user_data = {
        "name": "Usuario Logout",
        "email": "logout@example.com",
        "password": "senha123"
    }

    register_response = client.post("/auth/register", json=user_data)
    assert register_response.status_code == 200

    login_response = client.post(
        "/auth/login",
        json={
            "email": user_data["email"],
            "password": user_data["password"]
        }
    )
    assert login_response.status_code == 200

    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    me_response = client.get("/auth/me", headers=headers)
    assert me_response.status_code == 200

    logout_response = client.post("/auth/logout", headers=headers)
    assert logout_response.status_code == 200
    assert logout_response.json()["message"] == "Logout realizado com sucesso!"

    me_after_logout = client.get("/auth/me", headers=headers)
    assert me_after_logout.status_code == 401
    assert me_after_logout.json()["detail"] == "Token revogado"