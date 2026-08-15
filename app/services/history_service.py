from app.crud.conversation_crud import create_conversation
from app.crud.knowledge_base import get_kb_by_name
from app.crud.message_crud import get_messages_by_conversation_id
from app.exceptions.exceptions import KnowledgeBaseEmptyError
import json

from app.prompts.history_builder import build_history


def get_or_create_history(
        db,
        conversation_id,
        owner_id,
        kb_name,
        query
):
    is_new = False

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

        messages = []

        is_new = True

    history = build_history(messages)

    return conversation_id, history, is_new
