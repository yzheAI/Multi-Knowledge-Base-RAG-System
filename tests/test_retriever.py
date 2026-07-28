from sqlalchemy.orm import Session

from app.core.container import container


def test_faiss_retriever(db: Session):
    results = container.faiss_retriever.retrieve(
        db=db,
        query="铜基复合材料是什么？",
        kb_name="copper_based",
        top_k=5
    )

    assert len(results) > 0

    item = results[0]
    assert "chunk_id" in item
    assert "score" in item


def test_bm25_retriever(db: Session):
    results = container.bm25_retriever.retrieve(
        db=db,
        query="铜基复合材料是什么？",
        kb_name="copper_based",
        top_k=5
    )

    assert len(results) > 0

    item = results[0]
    assert "chunk_id" in item
    assert "score" in item


def test_hybrid_retriever(db: Session):
    results = container.hybrid_retriever.retrieve(
        db=db,
        query="铜基复合材料是什么？",
        kb_name="copper_based",
        top_k=5
    )

    assert len(results) > 0

    item = results[0]

    assert "chunk_id" in item
    assert "score" in item
