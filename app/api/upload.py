from fastapi import APIRouter, UploadFile, File, Query, Form, Depends
from sqlalchemy.orm import Session
from app.auth.dependencies import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.schemas.response_schema import ResponseModel
from app.services.upload_service import upload, search_files, get_all_files, file_delete
from utils.response import success


upload_router = APIRouter(prefix="/files", tags=["文件上传"])


@upload_router.post('/', response_model=ResponseModel)
async def upload_file(
        db: Session = Depends(get_db),
        file: UploadFile = File(...),
        kb_name: str = Form(...),
        current_user: User = Depends(get_current_user)
):
    result = await upload(
        db,
        file,
        kb_name,
        current_user.id
    )

    return success(result)


@upload_router.post('/search', response_model=ResponseModel)
async def read_file(
        db: Session = Depends(get_db),
        query: str = Query(...),
        kb_name: str = Query(),
        current_user: User = Depends(get_current_user)
):
    result = await search_files(
        db,
        query,
        kb_name,
        current_user.id
    )
    return success(data=result)


@upload_router.get('/files_message', response_model=ResponseModel)
async def get_files(
        kb_name,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    result = await get_all_files(
        db,
        kb_name,
        current_user.id
    )
    return success(
        data=result,
        msg="查询成功"
    )


@upload_router.delete("/{doc_id}", response_model=ResponseModel)
async def delete_file(
        doc_id: int,
        kb_name: str,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    await file_delete(
        db,
        doc_id,
        kb_name,
        current_user.id
    )

    return success(msg="删除成功")
