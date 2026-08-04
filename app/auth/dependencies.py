from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.auth.jwt import decode_token
from app.database.session import get_db
from app.models.user import User
from app.exceptions.exceptions import TokenInvalidError, InvalidCredentialsError

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login",
)


def get_current_user(
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db)
):
    try:
        payload = decode_token(token)

        user_id = payload.get(
            "user_id"
        )

        if not user_id:
            raise TokenInvalidError()

    except Exception:
        raise TokenInvalidError()

    user = (
        db.query(User)
        .filter(
            User.id == user_id
        ).first()
    )

    if not user:
        raise InvalidCredentialsError()

    return user

