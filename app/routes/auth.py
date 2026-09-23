from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..auth import create_access_token, hash_password, verify_password
from ..database import get_db
from ..models import User
from ..schemas import RegisterRequest, UserResponse, LoginRequest
from ..dependencies import get_current_user_id

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post("/register", response_model=UserResponse)
def register(
    user_data: RegisterRequest,
    db: Session = Depends(get_db)
):
    password_hash = hash_password(user_data.password)

    user = User(
        name=user_data.name,
        email=user_data.email,
        password_hash=password_hash
    )

    db.add(user)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=409,
            detail="E-mail já cadastrado!"
        )
    
    db.refresh(user)

    return user

@router.post("/login")
def login(
    user_data: LoginRequest,
    db: Session = Depends(get_db)
):
    result = db.execute(
        select(User).where(User.email == user_data.email)
    )

    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="E-mail ou senha inválidos"
        )

    password_is_valid = verify_password(
        user_data.password,
        user.password_hash
    )

    if not password_is_valid:
        raise HTTPException(
            status_code=401,
            detail="E-mail ou senha inválidos"
        )

    access_token = create_access_token(user.id)

    return{
        "message": "Login realizado com sucesso!",
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.get("/me")
def get_me(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    user = db.get(User, user_id)

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="Usuário não encontrado"
        )

    return{
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "created_at": user.created_at
    }