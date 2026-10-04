import re


def normalize_text(text: str):
    # 将所有空格换行转换为一个空格
    return re.sub(r"\s+", " ", text).strip()


def split_sentence(text: str):
    sentences = re.split(
        r"(?<=[。！；？.!?])",
        text
    )
    return [
        s.strip()
        for s in sentences
        if s.strip()
    ]


def get_block_text(block):
    # 取出block的text
    texts = []

    for line in block:
        for span in line:
            texts.append(span["text"])

    return normalize_text("".join(texts))


def get_block_font_size(block):
    sizes = []

    for line in block:
        for span in line:
            sizes.append(span["font_size"])

    return max(sizes) if sizes else 0


def is_toc_page(page):
    # 判断是否为目录页
    texts = []

    for block in page["blocks"]:
        text = get_block_text(block)
        if text:
            texts.append(text)

    page_text = "".join(texts)

    # 明确出现“目录”
    if "目录" in page_text:
        return True

    # 大量“章节标题 + 页码”的目录结构
    toc_like = 0

    for text in texts:
        if re.search(r"\.{3,}\s*\d+$", text):
            toc_like += 1

        elif re.search(r"\s+\d{1,4}$", text):
            toc_like += 1

    return toc_like >= 5


def is_page_number(text: str):
    # 判断是否为独立页码
    return bool(
        re.fullmatch(
            r"[—\-–]\s*\d+\s*[—\-–]",
            text
        )
    )


def is_main_heading(
        text: str,
        font_size: float
):
    """
    一级章节标题。
    例如：
    1.1 一般安全说明
    3.2 调试工具和服务工具
    """
    text = normalize_text(text)

    if not text:
        return False

    # 大标题
    if font_size >= 20:
        return True

    # Siemens 正文章节标题主要为 14pt
    if 13.5 <= font_size <= 14.5:
        return True

    # 中文章节标题
    if re.match(
        r"^[一二三四五六七八九十]+、\S+",
        text
    ):
        return True

    # 数字章节标题
    if re.match(
        r"^\d+(?:\.\d+)+\s*\S+",
        text
    ):
        return True

    return False


def is_subheading(text: str, font_size: float):
    """
    二级/小标题。

    当前 Siemens 文档中：
    11pt 通常对应 Toolbox、PLC 编程工具、
    Access MyMachine /P2P 等小标题。
    """

    text = normalize_text(text)

    if not text:
        return False

    # 当前文档实际观察到的小标题约为 11pt
    if not (10.8 <= font_size <= 11.2):
        return False

    # 太长更可能是正文
    if len(text) > 40:
        return False

    return True


def sentences_merge(
    sentences: list[str],
    chunk_size: int = 200,
    overlap_sentence: int = 1
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
                chunks.append("".join(current))

            overlap = current[-overlap_sentence:]

            current = overlap + [sentence]
            current_len = sum(len(x) for x in current)

    if current:
        chunks.append("".join(current))

    return chunks


def flush_text(
    chunks,
    current_text,
    page_num,
    section
):
    """
    把当前积累的正文转换成 chunks。
    """

    if not current_text:
        return

    text = "".join(current_text)

    sentences = split_sentence(text)

    for chunk in sentences_merge(
        sentences,
        chunk_size=200
    ):
        chunks.append({
            "text": chunk,
            "page": page_num,
            "section": section.copy()
        })


def chunk_document(
    pages,
    chunk_size: int = 200
):
    chunks = []

    current_heading = []
    current_text = []

    for page in pages:

        # 过滤目录页
        if is_toc_page(page):
            continue

        for block in page["blocks"]:

            text = get_block_text(block)

            if not text:
                continue

            # 过滤页码
            if is_page_number(text):
                continue

            font_size = get_block_font_size(block)

            # 一级标题
            if is_main_heading(text, font_size):

                # 先保存之前正文
                if current_text:
                    text_content = "".join(current_text)

                    sentences = split_sentence(text_content)

                    for chunk in sentences_merge(
                        sentences,
                        chunk_size
                    ):
                        chunks.append({
                            "text": chunk,
                            "page": page["page"],
                            "section": current_heading.copy()
                        })

                    current_text = []

                # 大标题
                if font_size >= 20:
                    current_heading.append(text)

                # 普通章节标题
                else:
                    current_heading = [text]

            # 二级标题
            elif is_subheading(text, font_size):

                # 保存之前正文
                if current_text:
                    text_content = "".join(current_text)

                    sentences = split_sentence(text_content)

                    for chunk in sentences_merge(
                        sentences,
                        chunk_size
                    ):
                        chunks.append({
                            "text": chunk,
                            "page": page["page"],
                            "section": current_heading.copy()
                        })

                    current_text = []

                # 二级标题加入 section
                current_heading = (
                    current_heading[:1] + [text]
                )

            # 正文
            else:
                current_text.append(text)

    # 最后一批正文
    if current_text:
        text_content = "".join(current_text)

        sentences = split_sentence(text_content)

        for chunk in sentences_merge(
            sentences,
            chunk_size
        ):
            chunks.append({
                "text": chunk,
                "page": pages[-1]["page"],
                "section": current_heading.copy()
            })

    return chunks
