import fitz


def load_pdf_structured(file_path: str):
    # 返回结构化PDF页面数据
    doc = fitz.open(file_path)  # 打开PDF文档

    pages = []  # 存放所有页面解析结果

    # 解析PDF每一页
    for page_num, page in enumerate(doc):
        # dict:字典格式提取全部内容，block:页面拆分成多个块
        blocks = page.get_text("dict")["blocks"]

        page_data = {
            "page": page_num + 1,
            "blocks": []
        }

        for block in blocks:
            if "lines" not in block:
                continue

            block_lines = []
            for line in block["lines"]:
                spans = []

                for span in line["spans"]:
                    spans.append({
                        "text": span["text"],
                        "font_size": span["size"],  # 字体大小
                        "flags": span["flags"],  # 粗体、斜体
                        "bbox": span["bbox"]  # 坐标框，页面上的位置
                    })
                block_lines.append(spans)
            page_data["blocks"].append(block_lines)
        pages.append(page_data)

    doc.close()
    return pages
