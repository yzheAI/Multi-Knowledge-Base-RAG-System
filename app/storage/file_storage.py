from app.config import KNOWLEDGE_BASE_PATH
from app.crud import knowledge_base
from app.exceptions.exceptions import KnowledgeBaseEmptyError
from app.knowledge_base.manager import KnowledgeManager
import os


async def save_uploaded_file(
        db,
        file,
        kb_name,
        owner_id
):
    kdg = KnowledgeManager(KNOWLEDGE_BASE_PATH)

    kb = knowledge_base.get_kb_by_name(
        db,
        kb_name,
        owner_id
    )

    if not kb:
        raise KnowledgeBaseEmptyError()

    kb_path = kdg.get_path(
        kb_name,
        owner_id
    )

    # 上传整个文档至kb
    upload_dir = os.path.join(
        kb_path,
        "files"
    )

    os.makedirs(
        upload_dir,
        exist_ok=True
    )

    file_path = os.path.join(
        upload_dir,
        file.filename
    )

    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)

    path = {
        "file_path": file_path,
        "kb_path": kb_path,
    }

    return path
