from pathlib import Path
from PyPDF2 import PdfReader
from app.exceptions.exceptions import UnsupportedDocumentType


def load_txt(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8") as f:  # 读入txt内容
        return f.read()


def load_pdf(file_path: str) -> str:
    reader = PdfReader(file_path)  # 打开PDF
    text = ""
    for page in reader.pages:  # 遍历每一页
        text += page.extract_text() or ""  # 提取文字
    return text


def load_document(file_path: str) -> str:
    ext = Path(file_path).suffix.lower()  # 获取后缀

    if ext == ".txt":
        return load_txt(file_path)
    elif ext == ".pdf":
        return load_pdf(file_path)
    else:
        raise UnsupportedDocumentType(f"Unsupported file type: {ext}")

