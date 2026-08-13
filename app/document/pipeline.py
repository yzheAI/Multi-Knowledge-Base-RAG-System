from pathlib import Path

from app.document.loader import load_document
from app.document.splitter import split_text, clean_chunks
from app.embedding.embedding import get_embeddings
from app.exceptions.exceptions import DocumentEmptyError


def process_document(file_path: str):

    text = load_document(file_path)

    if not text or len(text.strip()) == 0:
        raise DocumentEmptyError("上传文件为空")

    chunks = split_text(text)

    chunk_cleaned = clean_chunks(chunks)

    if len(chunk_cleaned) == 0:
        raise DocumentEmptyError("无有效chunk")

    vectors = get_embeddings(chunk_cleaned)

    ext = Path(file_path).suffix
    metadata = {
        "file_type": ext,
    }

    return {
        "total_length": len(text),
        "chunk_count": len(chunk_cleaned),
        "embedding_dim": len(vectors[0]),
        "chunks": chunk_cleaned,
        "vectors": vectors,
        "metadata": metadata
    }
