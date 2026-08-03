from jose import jwt
from datetime import datetime, timedelta
from app.config import settings

ALGORITHM = 'HS256'
EXPIRE_MINUTES = 60


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=EXPIRE_MINUTES)
    to_encode.update({'exp': expire})
    return jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=ALGORITHM
    )


def decode_token(token):
    return jwt.decode(
        token,
        settings.SECRET_KEY,
        algorithms=[ALGORITHM]
    )



