from datetime import datetime
from pathlib import Path
import json
from app.database.session import SessionLocal
from app.evaluation.evaluator import RetrieverEvaluator
from app.config import JSON_PATH, SAVE_JSON_PATH
from app.retriever.retriever_adapter import RetrieverAdapter
from app.core.container import container
import app.models

db = SessionLocal()

try:
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

    retrievers = {

        "faiss": f_retriever,

        "bm25": b_retriever,

        "hybrid": h_b_retriever,

    }

    evaluation_results = {}

    for name, retriever in retrievers.items():

        result = evaluator.evaluate(
            db,
            retriever
        )

        evaluation_results[name] = result

        print(
            f"{name}: {result}",
            flush=True
        )

    results = {
        "time": datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        ),

        "dataset_size": len(
                evaluator.dataset
        ),

        "results": evaluation_results

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
finally:

    db.close()


