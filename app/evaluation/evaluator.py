import json


class RetrieverEvaluator:
    def __init__(
            self,
            dataset_path,
            query_func=None
    ):

        with open(dataset_path, "r", encoding="utf-8") as f:
            self.dataset = json.load(f)

        self.query_func = query_func

    def evaluate(self, db, retriever):
        recall_1 = 0
        recall_3 = 0
        recall_5 = 0
        mrr = 0

        total = len(self.dataset)

        for item in self.dataset:

            query = item["question"]

            # Query Rewrite
            if self.query_func:
                query = self.query_func(
                    item
                )

            results = retriever.search(
                db,
                query,
                kb_name=item["kb_name"],
                owner_id=17,
                top_k=5
            )

            if any(
                item["chunk_id"] == r["chunk_id"]
                for r in results[:1]
            ):
                recall_1 += 1

            if any(
                item["chunk_id"] == r["chunk_id"]
                for r in results[:3]
            ):
                recall_3 += 1

            if any(
                item["chunk_id"] == r["chunk_id"]
                for r in results[:5]
            ):
                recall_5 += 1

            for rank, r in enumerate(results, start=1):
                if item["chunk_id"] == r["chunk_id"]:
                    mrr += 1 / rank
                    break

        return {
            "total": total,
            "recall_1": recall_1 / total,
            "recall_3": recall_3 / total,
            "recall_5": recall_5 / total,
            "MRR": mrr / total
        }


