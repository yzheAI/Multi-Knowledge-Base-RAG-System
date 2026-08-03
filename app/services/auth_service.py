from app.crud.user_crud import get_user_by_username, create_user
from app.auth.password import hash_password, verify_password
from app.auth.jwt import create_access_token
from app.exceptions.exceptions import UserConflictError, UserNotFoundError


async def create_user_service(db, username, password):
    user = get_user_by_username(db, username)
    if user:
        raise UserConflictError()

    hashed_password = hash_password(password)

    user = create_user(
        db,
        username,
        hashed_password
    )

    return user.username


async def login_user_service(db, username, password):
    user = get_user_by_username(db, username)
    if not user:
        raise UserNotFoundError()

    if not verify_password(password, user.hashed_password):
        raise UserNotFoundError()

    token = create_access_token(
        {
            "user_id": user.id,
        }
    )

    return {
        "access_token": token,
        "token_type": "bearer",
    }
