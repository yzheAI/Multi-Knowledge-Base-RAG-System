from app.crud import chunk_crud


def build_retriever_results(
        db,
        hits,
        source,
        filters=None
) -> list[dict]:
    """
    将向量检索或关键词检索得到的chunk_id结果，
    转换为统一的检索结果格式。
    """

    results = []

    # 提取出 chunk_id，根据chunk_id查询chunk内容
    chunk_ids = [
        h["chunk_id"]
        for h in hits
    ]

    chunks = chunk_crud.get_chunks_by_ids(
        db,
        chunk_ids,
    )

    # 构建映射，提高chunk查询效率
    chunk_map = {
        chunk.id: chunk
        for chunk in chunks
    }

    for hit in hits:
        chunk = chunk_map.get(
            hit["chunk_id"]
        )

        if chunk is None:
            continue
        # 根据metadata过滤条件筛选chunk
        if filters is not None:
            matched = all(
                chunk.metadata_info.get(k) == v
                for k, v in filters.items()
            )

            if not matched:
                continue

        results.append({
            "text": chunk.content,
            "chunk_id": chunk.id,
            "score": hit["score"],
            "source": source,
            "metadata": chunk.metadata_info
        })

        return results
