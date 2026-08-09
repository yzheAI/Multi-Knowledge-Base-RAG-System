from app.crud.conversation_crud import create_conversation, get_conversation, update_conversation_title
from app.crud.knowledge_base import get_kb_by_name
from app.exceptions.exceptions import KnowledgeBaseEmptyError
from app.llm.qwen import chat_with_qwen_stream
from app.prompts.history_builder import build_history
from app.services.rag_service import retrieve_context, build_sources, build_rag_prompt
import json
from app.crud.message_crud import get_messages_by_conversation_id, create_message
from app.query.rewrite import rewrite_query, need_rewrite


async def chat_service_stream(
        db,
        query: str,
        kb_name: str,
        owner_id: int,
        conversation_id=None,
        filters=None
):

    if conversation_id:
        messages = get_messages_by_conversation_id(
            db,
            conversation_id,
            owner_id
        )

    else:
        kb = get_kb_by_name(
            db,
            kb_name,
            owner_id
        )

        if kb is None:
            raise KnowledgeBaseEmptyError()

        kb_id = kb.id

        conversation = create_conversation(
            db,
            owner_id,
            kb_id,
            title=query[:20]
        )

        conversation_id = conversation.conversation_id

        yield (
            "event: conversation\n"
            f"data: {json.dumps({'conversation_id':conversation_id})}\n\n"
        )

        messages = []

    history = build_history(messages)

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
