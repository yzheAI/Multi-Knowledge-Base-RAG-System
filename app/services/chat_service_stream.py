from app.crud.conversation_crud import get_conversation, update_conversation_title
from app.llm.qwen import chat_with_qwen_stream
from app.services.history_service import get_or_create_history
from app.services.rag_service import retrieve_context, build_sources, build_rag_prompt
import json
from app.crud.message_crud import create_message
from app.query.rewrite import rewrite_query, need_rewrite


async def chat_service_stream(
        db,
        query: str,
        kb_name: str,
        owner_id: int,
        conversation_id=None,
        filters=None
):

    conversation_id, history, is_new = get_or_create_history(
        db,
        conversation_id,
        owner_id,
        kb_name,
        query
    )

    if is_new:
        yield (
            "event: conversation\n"
            f"data: {json.dumps({'conversation_id': conversation_id})}\n\n"
        )

    original_query = query

    if need_rewrite(query):
        new_query = rewrite_query(
            original_query,
            history
        )
    else:
        new_query = original_query

    create_message(
        db,
        conversation_id,
        "user",
        query
    )

    contexts = retrieve_context(
        db,
        new_query,
        kb_name,
        owner_id,
        filters
    )

    sources = build_sources(contexts)

    yield (
        "event: source\n"
        f"data: {json.dumps(sources, ensure_ascii=False)}\n\n"
    )

    prompt = build_rag_prompt(
        original_query,
        contexts,
        history
    )

    answer = ""

    for chunk in chat_with_qwen_stream(prompt):
        answer += chunk
        yield (
            "event: message\n"
            f"data: {chunk}\n\n"
        )

    conversation = get_conversation(
        db,
        conversation_id,
        owner_id
    )

    if not conversation.title:
        update_conversation_title(
            db,
            conversation_id,
            query[:20]
        )

    create_message(
        db,
        conversation_id,
        "assistant",
        answer
    )
