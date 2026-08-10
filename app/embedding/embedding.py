from sentence_transformers import SentenceTransformer
from app.config import EMBEDDING_MODEL
from app.cache.embedding_cache import EmbeddingCache
import threading

embedding_model = None
embedding_lock = threading.Lock()
embedding_cache = EmbeddingCache()


def get_embedding_model():
    global embedding_model

    if embedding_model is None:

        with embedding_lock:

            if embedding_model is None:

                embedding_model = SentenceTransformer(EMBEDDING_MODEL)

    return embedding_model


def get_embedding(text: str):
    cached = embedding_cache.get(text)

    if cached is not None:
        print("embedding cache hit")
        return cached

    model = get_embedding_model()
    embedding = model.encode(
        text,
        normalize_embeddings=True
    )

    embedding_cache.set(
        text,
        embedding
    )

    return embedding


def get_embeddings(texts: list[str]):
    model = get_embedding_model()
    return model.encode(
        texts,
        normalize_embeddings=True
    ).tolist()
