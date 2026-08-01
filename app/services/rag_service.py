from app.config import SEARCH_TOP_K
from app.llm.qwen import chat_with_qwen_stream
from app.memory.conversation_memory import ConversationMemory
from app.prompts.history_builder import build_history
from app.prompts.rag_prompt import build_prompt
from app.core.container import container
import json
memory = ConversationMemory()


async def chat_service_stream(db, query: str, kb_name, filters=None):

    history = build_history(memory)

    if filters:
        filters = filters.model_dump(
            exclude_none=True
        )

    contexts = container.hybrid_retriever.retrieve(
        db,
        query,
        kb_name,
        top_k=SEARCH_TOP_K,
        filters=filters,
    )

    sources = [
        {
            "chunk_id": ctx["chunk_id"],
            "source": ctx["metadata"].get("source"),
            "score": ctx["score"],
            "content": ctx["text"]
        }
        for ctx in contexts
    ]

    yield (
        "event: source\n"
        f"data: {json.dumps(sources, ensure_ascii=False)}\n\n"
    )

    content_text = "\n".join(
        [ctx["text"] for ctx in contexts]
    )

    prompt = build_prompt(
        query,
        content_text,
        history
    )

    answer = ""

    for chunk in chat_with_qwen_stream(prompt):
        answer += chunk
        yield (
            "event: message\n"
            f"data: {chunk}\n\n"
        )

    memory.add_user_message(query)
    memory.add_assistant_message(answer)
