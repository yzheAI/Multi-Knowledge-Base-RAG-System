from rank_bm25 import BM25Okapi
import jieba
import os
import pickle


class BM25Store:
    def __init__(self):
        self.tokenizer = []
        self.bm25 = None
        self.ids = []

    def add_documents(
            self,
            documents: list[dict]
    ):
        self.ids = [
            doc["chunk_id"]
            for doc in documents
        ]

        texts = [
            doc["text"]
            for doc in documents
        ]

        self.tokenizer = [
            list(jieba.cut(text))
            for text in texts
        ]

        self.bm25 = BM25Okapi(
            self.tokenizer,
        )

    def search(
            self,
            query: str,
            top_k: int = 5
    ):
        if not self.bm25:
            return []

        # 对查询语句分词
        query_tokens = list(
            jieba.cut(query)
        )

        # 计算query和所有语料的BM25相似度分数
        scores = self.bm25.get_scores(
            query_tokens
        )

        ranked = sorted(
            enumerate(scores),  # 下标+分数配对
            key=lambda x: x[1],
            reverse=True
        )

        return [
            {
                "chunk_id": self.ids[idx],
                "score": float(score),
                "source": "bm25",
            }
            for idx, score in ranked[:top_k]
        ]

    def save(
            self,
            kb_path: str
    ):

        data = {
            "tokenizer": self.tokenizer,
            "ids": self.ids,
            "bm25": self.bm25
        }

        path = os.path.join(
            kb_path,
            "bm25.pkl"
        )

        with open(path, 'wb') as f:
            pickle.dump(data, f)

    def load(self, kb_path: str):

        path = os.path.join(
            kb_path,
            "bm25.pkl"
        )

        if os.path.exists(path):
            with open(path, 'rb') as f:
                obj = pickle.load(f)

                self.tokenizer = obj['tokenizer']
                self.bm25 = obj['bm25']
                self.ids = obj['ids']

        return True
