from app.cache.retrieval_cache import RetrievalCache


def test_retrieval_cache_set_and_get(retrieval_cache):
    cache = RetrievalCache()

    owner_id = 1
    kb_id = 10
    query = "人工智能是什么"
    filters = None

    result = [
        {
            "chunk_id": 1,
            "text": "人工智能是研究智能系统的技术",
            "score": 0.95
        }
    ]

    cache.set(
        owner_id,
        kb_id,
        query,
        filters,
        result
    )

    cached_result = cache.get(
        owner_id,
        kb_id,
        query,
        filters
    )

    assert cached_result == result


def test_delete_retrieval_cache_by_kb(retrieval_cache):
    cache = RetrievalCache()

    owner_id = 1
    kb_id = 10

    result = [
        {
            "chunk_id": 1,
            "text": "人工智能",
            "score": 0.95,
        }
    ]

    cache.set(
        owner_id,
        kb_id,
        "什么是人工智能",
        None,
        result
    )

    cache.set(
        owner_id,
        kb_id,
        "人工智能有哪些应用",
        None,
        result
    )

    cache.set(
        owner_id,
        20,
        "什么是人工智能",
        None,
        result
    )

    deleted_count = cache.delete_by_kb(
        owner_id,
        kb_id
    )

    assert deleted_count == 2

    assert cache.get(
        owner_id,
        kb_id,
        "人工智能有哪些应用",
        None,
    ) is None

    assert cache.get(
        owner_id,
        20,
        "什么是人工智能",
        None
    ) == result


def test_delete_retrieval_cache_by_only_for_owner(retrieval_cache):
    cache = RetrievalCache()
    result = [
        {
            "chunk_id": 1,
            "text": "人工智能",
            "score": 0.95,
        }
    ]

    cache.set(
        1,
        10,
        "什么是人工智能",
        None,
        result
    )
    cache.set(
        2,
        10,
        "什么是人工智能",
        None,
        result
    )

    deleted_count = cache.delete_by_kb(
        1,
        10
    )
    assert deleted_count == 1

    assert cache.get(
        1,
        10,
        "什么是人工智能",
        None
    ) is None

    assert cache.get(
        2,
        10,
        "什么是人工智能",
        None
    ) == result


def test_retrieval_cache_filters_are_different(retrieval_cache):
    cache = RetrievalCache()

    owner_id = 1
    kb_id = 10
    query = "人工智能"

    result1 = [
        {
            "chunk_id": 1,
            "text": "人工智能",
            "score": 0.9,
        }
    ]

    result2 = [
        {
            "chunk_id": 2,
            "text": "人工智能",
            "score": 0.8,
        }
    ]

    filters1 = {
        "source": "doc1.pdf"
    }
    filters2 = {
        "source": "doc2.pdf"
    }

    cache.set(
        owner_id,
        kb_id,
        query,
        filters1,
        result1
    )
    cache.set(
        owner_id,
        kb_id,
        query,
        filters2,
        result2
    )

    assert cache.get(
        owner_id,
        kb_id,
        query,
        filters1,
    ) == result1

    assert cache.get(
        owner_id,
        kb_id,
        query,
        filters2
    ) == result2

