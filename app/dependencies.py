from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from .auth import decode_acess_token
from .database import get_db
from .models import RevokedToken

security = HTTPBearer()

def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)) -> dict:

    token = credentials.credentials

    try:
        payload = decode_acess_token(token)
    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Token inválido ou expirado"
        )

    user_id = payload.get("sub")
    jti = payload.get("jti")
    expires_at = payload.get("exp")

    if user_id is None or jti is None or expires_at is None:
        raise HTTPException(
            status_code=401,
            detail="Token inválido"
        )

    revoked_token = db.execute(
        select(RevokedToken).where(RevokedToken.jti == jti)
    ).scalar_one_or_none()

    if revoked_token is not None:
        raise HTTPException(
            status_code=401,
            detail="Token revogado"
        )
    
    return{
        "user_id": int(user_id),
        "jti": jti,
        "expires_at": payload.get("exp")
    }