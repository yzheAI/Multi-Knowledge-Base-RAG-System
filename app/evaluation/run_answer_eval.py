from datetime import datetime

from app.database.session import SessionLocal
from app.evaluation.answer_evaluation import AnswerEvaluation
from app.config import JSON_PATH, SAVE_ANSWER_EVALUATION_PATH
import json

from app.llm.qwen import chat_with_qwen
from app.prompts.rag_prompt import build_prompt
from app.services.rag_service import retrieve_context

evaluator = AnswerEvaluation()

db = SessionLocal()

try:
    with open(JSON_PATH, "r", encoding='utf-8') as f:
        dataset = json.load(f)

    answer_results = {
        "time": datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        ),

        "dataset_size": len(
            dataset
        ),
    }

    results = []

    for item in dataset:

        question = item["question"]
        reference_answer = item["answer"]

        contexts = retrieve_context(
            db,
            question,
            kb_name=item["kb_name"],
            owner_id=17
        )

        prompt = build_prompt(
            query=question,
            content_text=contexts
        )

        model_answer = chat_with_qwen(
            prompt
        )

        result = evaluator.evaluate(
            contexts=contexts,
            question=question,
            model_answer=model_answer,
            answer=reference_answer
        )

        # JSON字符串 → Python字典
        try:
            result = json.loads(result)
        except json.JSONDecodeError:
            print("评测结果 JSON 解析失败：")
            print(result)
            continue

        results.append({
            "question": question,
            "model_answer": model_answer,
            "evaluation": result
        })

        print(result)

    answer_results["results"] = results

    with open(SAVE_ANSWER_EVALUATION_PATH, "w", encoding='utf-8') as f:
        json.dump(answer_results, f, ensure_ascii=False, indent=4)

finally:
    db.close()
