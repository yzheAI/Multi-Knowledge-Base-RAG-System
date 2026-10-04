import re


def split_paragraph(text: str):
    paragraphs = re.split(
        r"\n\s*\n",
        text
    )
    return [
        p.strip()
        for p in paragraphs
        if p.strip()
    ]


def split_sentence(paragraph: str):
    sentences = re.split(
        r"(?<=[。！；？. ?])",
        paragraph
    )
    return [
        s.strip()
        for s in sentences
        if s.strip()
    ]


def sentences_merge(
        sentences: list[str],
        chunk_size: int = 200,
        overlap_sentence=1
):
    chunks = []

    current = []

    current_len = 0

    for sentence in sentences:

        if current_len + len(sentence) <= chunk_size:
            current.append(sentence)
            current_len += len(sentence)

        else:
            if current:
                chunks.append(
                    "".join(current)
                )
            overlap = current[-overlap_sentence:]

            current = overlap + [sentence]

            current_len = sum(
                len(x)
                for x in current
            )

    if current:
        chunks.append(
            "".join(current)
        )

    return chunks


def clean_chunks(chunks: list[str]):
    cleaned = []
    for c in chunks:
        c = c.strip()

        if not c:
            continue

        if len(c) < 10:
            continue

        if len(c.replace("。", "").strip()) == 0:
            continue

        cleaned.append(c)
    return cleaned


def split_text(
        text: str,
        chunk_size: int = 200
):
    paragraphs = split_paragraph(text)

    all_chunks = []

    for paragraph in paragraphs:

        sentences = split_sentence(paragraph)

        paragraphs_chunks = sentences_merge(
            sentences,
            chunk_size
        )

        all_chunks.extend(paragraphs_chunks)

    return all_chunks
