from app.document.loaders.pdf_structured_loader import load_pdf_structured
from app.document.chunking.chunking_v2 import chunk_document


PDF_PATH = r"F:\Desktop\RAG知识库\机床\diagnosis\报警诊断手册.pdf"


pages = load_pdf_structured(PDF_PATH)

chunks = chunk_document(
    pages,
    chunk_size=200
)

print(f"PDF页数: {len(pages)}")
print(f"Chunk数量: {len(chunks)}")

print("\n========== 前50个 Chunk ==========\n")

for i, chunk in enumerate(chunks[1:50]):

    print(f"========== Chunk {i + 1} ==========")
    print(f"Page: {chunk['page']}")
    print(f"Section: {chunk['section']}")
    print(chunk["text"])
    print()
