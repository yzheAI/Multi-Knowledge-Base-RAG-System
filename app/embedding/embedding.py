from sentence_transformers import SentenceTransformer
from app.config import EMBEDDING_MODEL
import threading

embedding_model = None
embedding_lock = threading.Lock()


def get_embedding_model():
    global embedding_model

    if embedding_model is None:

        with embedding_lock:

            if embedding_model is None:

                embedding_model = SentenceTransformer(EMBEDDING_MODEL)

    return embedding_model


def get_embedding(text: str):
    model = get_embedding_model()
    return model.encode(
        text,
        normalize_embeddings=True
    )


def get_embeddings(texts: list[str]):
    model = get_embedding_model()
    return model.encode(
        texts,
        normalize_embeddings=True
    ).tolist()
