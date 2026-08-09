from app.document.splitter import split_text, split_sentence, sentences_merge, split_paragraph, clean_chunks


def test_split_paragraph():
    text = """
    第一段内容。
    
    第二段内容。
    """

    paragraphs = split_paragraph(text)

    assert len(paragraphs) == 2
    assert paragraphs[0] == "第一段内容。"
    assert paragraphs[1] == "第二段内容。"


def test_split_sentence():
    text = "人工智能是一门学科。机器学习是其中的重要方向！"

    sentences = split_sentence(text)

    assert len(sentences) == 2
    assert sentences[0] == "人工智能是一门学科。"
    assert sentences[1] == "机器学习是其中的重要方向！"


def test_remove_empty_chunk():
    chunks = [
        "",
        " ",
        "。",
        "人工智能是一门研究机器智能的学科"
    ]

    result = clean_chunks(chunks)

    assert result == [
        "人工智能是一门研究机器智能的学科"
    ]


def test_basic_chunking():
    text = (
        "人工智能是一门研究机器智能的学科。"
        "机器学习是人工智能的重要组成部分。"
        "深度学习推动了人工智能的发展。"
    )

    chunks = split_text(
        text,
        chunk_size=30
    )
    assert len(chunks) >= 1
    for chunk in chunks:
        assert len(chunk) > 10


def test_long_chunking():
    text = "a" * 500

    chunks = split_text(
        text,
        chunk_size=100
    )

    assert len(chunks) > 0

    for chunk in chunks:
        assert len(chunk) > 0
