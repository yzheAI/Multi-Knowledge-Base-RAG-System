from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.services.knowledge_base_service import create, get_kb_service, get_all_kb_service, delete_kb_service
from app.database.session import get_db
from app.schemas.response_schema import ResponseModel
from utils.response import success
from app.schemas.knowledge_base_schema import KnowledgeBaseCreate
from app.auth.dependencies import get_current_user
from app.models.user import User

kb_router = APIRouter(prefix='/knowledge_bases', tags=['知识库管理'])


@kb_router.post('/', response_model=ResponseModel)
async def create_kb(
        request: KnowledgeBaseCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    kb = await create(
        db,
        request.name,
        current_user.id
    )
    return success(
        data=kb,
        msg="创建成功"
    )


@kb_router.get('/all', response_model=ResponseModel)
async def get_all_kb(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    kbs = await get_all_kb_service(
        db,
        current_user.id
    )
    return success(
        data=kbs,
        msg="查询成功"
    )


@kb_router.get('/{kb_name}', response_model=ResponseModel)
async def get_kb(
        kb_name: str,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    kb = await get_kb_service(
        db=db,
        kb_name=kb_name,
        owner_id=current_user.id
    )
    return success(
        data=kb,
        msg="查询成功"
    )


@kb_router.delete('/{kb_name}', response_model=ResponseModel)
async def delete_kb(
        kb_name: str,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    await delete_kb_service(
        db=db,
        kb_name=kb_name,
        owner_id=current_user.id
    )
    return success(
        data={
            "kb_name": kb_name
        },
        msg="删除成功"
    )
