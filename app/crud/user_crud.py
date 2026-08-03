from sqlalchemy.orm import Session
from app.models.user import User


def get_user_by_username(db, username: str):
    user = (
        db.query(User)
        .filter(
            User.username == username
        ).first()
    )
    return user


def create_user(db: Session, username: str, password_hash: str):
    user = User(
        username=username,
        password_hash=password_hash
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user



