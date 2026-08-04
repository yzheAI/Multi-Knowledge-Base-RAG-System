from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.schemas.auth_schema import UserLogin, UserCreate
from app.services.auth_service import create_user_service, login_user_service


user_router = APIRouter(prefix='/auth', tags=['认证'])


@user_router.post('/register')
async def create_user(request: UserCreate, db: Session = Depends(get_db)):
    user = await create_user_service(
        db=db,
        username=request.username,
        password=request.password
    )

    return user


@user_router.post('/login')
async def login(request: UserLogin, db: Session = Depends(get_db)):
    result = await login_user_service(
        db=db,
        username=request.username,
        password=request.password
    )
    return result

