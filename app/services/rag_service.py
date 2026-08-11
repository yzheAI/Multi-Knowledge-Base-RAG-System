from app.config import SEARCH_TOP_K
from app.crud.knowledge_base import get_kb_by_name
from app.prompts.rag_prompt import build_prompt
from app.core.container import container
from app.cache.retrieval_cache import RetrievalCache

retrieve_cache = RetrievalCache()


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

    kb = get_kb_by_name(
        db,
        kb_name,
        owner_id
    )
    cache = retrieve_cache.get(
        owner_id,
        kb.id,
        query,
        filters
    )
    if cache is not None:
        print("retrieval cache hit")
        return cache

    contexts = container.hybrid_retriever.retrieve(
        db,
        query,
        kb_name,
        owner_id=owner_id,
        top_k=SEARCH_TOP_K,
        filters=filters,
    )
    retrieve_cache.set(
        owner_id,
        kb.id,
        query,
        filters,
        contexts,
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
