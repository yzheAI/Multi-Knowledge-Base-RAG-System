from app.core.container import container


def test_faiss_retriever(
        db,
        auth_user,
        retrieval_kb
):

    user_id = auth_user["user_id"]

    results = container.faiss_retriever.retrieve(
        db=db,
        query="铜基复合材料是什么？",
        owner_id=user_id,
        kb_name=retrieval_kb,
        top_k=5
    )

    assert len(results) > 0

    item = results[0]
    assert "chunk_id" in item
    assert "score" in item


def test_bm25_retriever(
        db,
        auth_user,
        retrieval_kb
):
    results = container.bm25_retriever.retrieve(
        db=db,
        query="铜基复合材料是什么？",
        owner_id=auth_user["user_id"],
        kb_name=retrieval_kb,
        top_k=5
    )

    assert len(results) > 0

    item = results[0]
    assert "chunk_id" in item
    assert "score" in item


def test_hybrid_retriever(db, auth_user, retrieval_kb):
    results = container.hybrid_retriever.retrieve(
        db=db,
        query="铜基复合材料是什么？",
        owner_id=auth_user["user_id"],
        kb_name=retrieval_kb,
        top_k=5
    )

    assert len(results) > 0

    item = results[0]

    assert "chunk_id" in item
    assert "score" in item
