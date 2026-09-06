from app.config import SAVE_ANSWER_EVALUATION_PATH
import json

with open(SAVE_ANSWER_EVALUATION_PATH, 'r', encoding="utf-8") as f:
    results = json.load(f)

statistic_results = results["results"]

statistics = {
    "correctness": {
        1: 0,
        2: 0,
        3: 0,
        4: 0,
        5: 0,
    },
    "faithfulness": {
        1: 0,
        2: 0,
        3: 0,
        4: 0,
        5: 0,
    },
    "relevance": {
        1: 0,
        2: 0,
        3: 0,
        4: 0,
        5: 0,
    },
}

for result in statistic_results:
    evaluation = result["evaluation"]

    for metric in statistics:
        score = evaluation[metric]
        statistics[metric][score] += 1

for metric, scores in statistics.items():
    total = sum(scores.values())

    average = sum(
        score * count
        for score, count in scores.items()
    ) / total

    print(f"\n{metric}")
    print(f"average: {average:.2f}")

    for score in range(5, 0, -1):
        print(f"{score}: {scores[score]}")
