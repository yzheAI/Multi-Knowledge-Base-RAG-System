from datetime import datetime
from pathlib import Path
import json

from app.database.session import SessionLocal
from app.evaluation.evaluator import RetrieverEvaluator
from app.config import JSON_PATH, SAVE_JSON_PATH
from app.retriever.retriever_adapter import RetrieverAdapter
from app.core.container import container

db = SessionLocal()


evaluator = RetrieverEvaluator(
    JSON_PATH
)

f_retriever = RetrieverAdapter(
    container.faiss_retriever,
)

b_retriever = RetrieverAdapter(
    container.bm25_retriever,
)

h_b_retriever = RetrieverAdapter(
    container.hybrid_retriever,
)

result_faiss = evaluator.evaluate(
    db,
    f_retriever,
)

result_bm25 = evaluator.evaluate(
    db,
    b_retriever,
)

result_hybrid = evaluator.evaluate(
    db,
    h_b_retriever,
)

results = {
    "model": "bge-reranker-base",
    "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "results": {
        "faiss": result_faiss,
        "bm25": result_bm25,
        "hybrid": result_hybrid,
    }
}

save_path = Path(
    SAVE_JSON_PATH
)

with open(save_path, "w", encoding="utf-8") as f:
    json.dump(
        results,
        f,
        ensure_ascii=False,
        indent=4,
    )
print(
    f"Evaluation result saved to {save_path}"
)
print(f"Faiss: {result_faiss}")
print(f"Bm25: {result_bm25}")
print(f"Hybrid: {result_hybrid}")

