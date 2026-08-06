from app.crud.conversation_crud import get_user_conversations, create_conversation
from app.crud.knowledge_base import get_kb_by_name
from app.crud.message_crud import get_messages_by_conversation_id


def get_conversations_by_kb_service(db, user_id, kb_name):
    kb = get_kb_by_name(
        db,
        kb_name,
        user_id
    )

    conversations = get_user_conversations(
        db,
        user_id,
        kb.id,
    )

    results = [
        {
            "conversation_id": conversation.conversation_id,
            "title": conversation.title,
            "created_at": conversation.created_at,
        }
        for conversation in conversations
    ]

    return results


def create_conversation_service(db, kb_name, user_id):
    kb = get_kb_by_name(
        db,
        kb_name,
        user_id
    )

    conversation = create_conversation(
        db,
        user_id,
        kb.id,
        None
    )

    return {
        "conversation_id": conversation.conversation_id,
    }


def get_messages_service(
        db,
        conversation_id,
        user_id
):

    messages = get_messages_by_conversation_id(
        db,
        conversation_id,
        user_id
    )

    return [
        {
            "role": message.role,
            "content": message.content,
            "created_at": message.created_at,
        }
        for message in messages
    ]
