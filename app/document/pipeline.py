from pathlib import Path

from app.document.loaders.document_loader import load_document
from app.document.chunking.chunking_v1 import split_text, clean_chunks
from app.embedding.embedding import get_embeddings
from app.exceptions.exceptions import DocumentEmptyError
from app.document.loaders.pdf_structured_loader import load_pdf_structured
from app.document.chunking.chunking_v2 import chunk_document


def process_document(file_path: str):

    # text = load_document(file_path)
    pages = load_pdf_structured(file_path)

    if not pages:
        raise DocumentEmptyError("PDF解析结果为空")

    # chunks = split_text(text)
    chunks = chunk_document(pages)

    # chunk_cleaned = clean_chunks(chunks)

    # if len(chunk_cleaned) == 0:
    if not chunks:
        raise DocumentEmptyError("无有效chunk")

    chunk_texts = [
        chunk["text"].strip()
        for chunk in chunks
        if chunk["text"].strip()
    ]

    if not chunk_texts:
        raise DocumentEmptyError("无有效chunk")

    vectors = get_embeddings(chunk_texts)

    ext = Path(file_path).suffix
    metadata = {
        "file_type": ext,
    }

    # return {
    #     "total_length": len(text),
    #     "chunk_count": len(chunk_cleaned),
    #     "embedding_dim": len(vectors[0]),
    #     "chunks": chunk_cleaned,
    #     "vectors": vectors,
    #     "metadata": metadata
    # }
    return {
        "total_length": len(pages),
        "chunk_count": len(chunks),
        "embedding_dim": len(vectors[0]),
        "chunks": chunk_texts,
        "vectors": vectors,
        "metadata": metadata
    }
