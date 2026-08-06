from app.config import SEARCH_TOP_K
from app.prompts.rag_prompt import build_prompt
from app.core.container import container


def retrieve_context(
        db,
        query: str,
        kb_name: str,
        owner_id: int,
        filters=None
):
    if filters:
        filters = filters.model_dump(
            exclude_none=True
        )

    contexts = container.hybrid_retriever.retrieve(
        db,
        query,
        kb_name,
        owner_id=owner_id,
        top_k=SEARCH_TOP_K,
        filters=filters,
    )
    return contexts


def build_sources(contexts):
    sources = [
        {
            "chunk_id": ctx["chunk_id"],
            "source": ctx["metadata"].get("source"),
            "score": ctx["score"],
            "content": ctx["text"]
        }
        for ctx in contexts
    ]
    return sources


def build_rag_prompt(
        query,
        contexts,
        history=None,
):
    content_text = "\n".join(
        [ctx["text"] for ctx in contexts]
    )

    prompt = build_prompt(
        query,
        content_text,
        history
    )

    return prompt
