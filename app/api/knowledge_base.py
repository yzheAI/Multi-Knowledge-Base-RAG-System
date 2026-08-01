from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.services.knowledge_base_service import create, get_kb_service, get_all_kb_service, delete_kb_service
from app.database.session import get_db
from app.schemas.response_schema import ResponseModel
from utils.response import success
from app.schemas.knowledge_base_schema import KnowledgeBaseCreate

kb_router = APIRouter(prefix='/knowledge_bases', tags=['知识库管理'])


@kb_router.post('/', response_model=ResponseModel)
async def create_kb(request: KnowledgeBaseCreate, db: Session = Depends(get_db)):
    kb = await create(db, request.name)
    return success(
        data=kb,
        msg="创建成功"
    )


@kb_router.get('/all', response_model=ResponseModel)
async def get_all_kb(db: Session = Depends(get_db)):
    kbs = await get_all_kb_service(
        db=db,
    )
    return success(
        data=kbs,
        msg="查询成功"
    )


@kb_router.get('/{kb_name}', response_model=ResponseModel)
async def get_kb(kb_name: str, db: Session = Depends(get_db)):
    kb = await get_kb_service(
        db=db,
        kb_name=kb_name
    )
    return success(
        data=kb,
        msg="查询成功"
    )


@kb_router.delete('/{kb_name}', response_model=ResponseModel)
async def delete_kb(kb_name: str, db: Session = Depends(get_db)):
    await delete_kb_service(
        db=db,
        kb_name=kb_name
    )
    return success(
        data={
            "kb_name": kb_name
        },
        msg="删除成功"
    )
