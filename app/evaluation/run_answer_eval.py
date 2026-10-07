from datetime import datetime
from app.core.container import container
from app.crud import document_crud, knowledge_base
from app.database.session import SessionLocal
from app.evaluation.answer_evaluation import AnswerEvaluation
from app.config import JSON_PATH, SAVE_ANSWER_EVALUATION_PATH
import json
from app.llm.qwen import chat_with_qwen
from app.prompts.rag_prompt import build_prompt

evaluator = AnswerEvaluation()

db = SessionLocal()


def get_document_id(
        db,
        kb_id,
        source,
):

    documents = document_crud.get_documents_by_kb(
        db,
        kb_id
    )

    target_source = source.replace(
        ".pdf",
        "plus.pdf"
    )

    candidates = [
        doc
        for doc in documents
        if doc.filename == target_source
    ]

    if not candidates:
        raise ValueError(
            f"找不到对应 V2 document: "
            f"kb={kb_id}, "
            f"source={source}, "
            f"target={target_source}"
        )

    if len(candidates) > 1:
        raise ValueError(
            f"找到多个匹配 V2 document: "
            f"kb={kb_id}, "
            f"source={source}, "
            f"documents={[doc.id for doc in candidates]}"
        )

    return candidates[0].id


try:
    with open(JSON_PATH, "r", encoding='utf-8') as f:
        dataset = json.load(f)

    results = []

    correctness_sum = 0
    faithfulness_sum = 0
    relevance_sum = 0
    valid_count = 0

    # V2 Answer Evaluation
    for item in dataset:

        question = item["question"]
        reference_answer = item["answer"]

        expected_chunks = item.get(
            "relevant_chunks",
            []
        )

        if not expected_chunks:
            continue

        kb = knowledge_base.get_kb_by_name(
            db,
            item["kb_name"],
            17
        )

        if not kb:
            raise ValueError(
                f"找不到知识库: "
                f"{item['kb_name']}"
            )

        # 找到 V2 document
        source = expected_chunks[0].get(
            "source"
        )

        document_id = get_document_id(
            db=db,
            kb_id=kb.id,
            source=source
        )

        # V2 Retrieval
        contexts = container.hybrid_retriever.retrieve(
            db,
            question,
            item["kb_name"],
            owner_id=17,
            top_k=10,
            document_id=document_id
        )

        # Generation
        prompt = build_prompt(
            query=question,
            content_text=contexts
        )

        model_answer = chat_with_qwen(
            prompt
        )

        # Answer Evaluation
        result = evaluator.evaluate(
            question=question,
            answer=reference_answer,
            contexts=contexts,
            model_answer=model_answer
        )

        # JSON Parse
        try:
            result = json.loads(result)

        except json.JSONDecodeError:
            print(
                "V2 评测结果 JSON 解析失败："
            )
            print(result)
            continue

        # Statistics
        correctness_sum += result[
            "correctness"
        ]

        faithfulness_sum += result[
            "faithfulness"
        ]

        relevance_sum += result[
            "relevance"
        ]

        valid_count += 1

        # Save Result
        results.append({
            "question": question,
            "reference_answer": reference_answer,
            "model_answer": model_answer,
            "evaluation": result
        })

        print(result)

    # Summary
    summary = {
        "valid_count": valid_count,

        "correctness": (
            correctness_sum / valid_count
            if valid_count > 0
            else 0
        ),

        "faithfulness": (
            faithfulness_sum / valid_count
            if valid_count > 0
            else 0
        ),

        "relevance": (
            relevance_sum / valid_count
            if valid_count > 0
            else 0
        )
    }

    # Save
    answer_results = {
        "time": datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        ),

        "version": "v2",

        "dataset_size": len(dataset),

        "summary": summary,

        "results": results
    }

    with open(
            SAVE_ANSWER_EVALUATION_PATH,
            "w",
            encoding="utf-8"
    ) as f:

        json.dump(
            answer_results,
            f,
            ensure_ascii=False,
            indent=4
        )

    print("\n==========================")
    print("V2 Answer Evaluation")
    print("==========================")
    print(
        f"Valid: {valid_count}/{len(dataset)}"
    )
    print(
        f"Correctness: "
        f"{summary['correctness']:.2f}"
    )
    print(
        f"Faithfulness: "
        f"{summary['faithfulness']:.2f}"
    )
    print(
        f"Relevance: "
        f"{summary['relevance']:.2f}"
    )

finally:
    db.close()
