from app.config import SEARCH_TOP_K
from app.core.container import container
from agent.prompt import build_search_prompt
from app.llm.qwen import chat_with_qwen
from app.crud.document_crud import get_document_by_key


def knowledge_search(
        db,
        query,
        kb_name,
        owner_id,
        filters=None

):
    result = container.hybrid_retriever.retrieve(
        db,
        query,
        kb_name,
        owner_id=owner_id,
        top_k=SEARCH_TOP_K,
        filters=filters,
    )

    return result


def document_search(
        db,
        query,
        kb_name,
        owner_id
):
    prompt = build_search_prompt(
        query
    )

    key = chat_with_qwen(
        prompt
    )

    docs = get_document_by_key(
        db,
        key,
        kb_name,
        owner_id
    )

    return [
        {
            "filename": doc.filename,
            "document_type": doc.document_type,
        }
        for doc in docs
    ]
