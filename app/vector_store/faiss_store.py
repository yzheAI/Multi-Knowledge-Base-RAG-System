import faiss
import numpy as np
import pickle
import os
from app.bm25.bm25 import BM25Store


# 封装FAISS，实现 存向量+存原文+搜相似文本
class VectorStore:

    def __init__(self, dim: int):
        # IDMap 包装
        base_index = faiss.IndexFlatIP(dim)
        self.index = faiss.IndexIDMap(base_index)

        self.data = {}
        self.next_id = 0  # 全局唯一ID分配器的状态变量,生成起点
        self.texts = []

        self.bm25 = BM25Store()

    # 添加文本与向量
    def add(
            self,
            embeddings,
            texts,
            chunk_ids,
            doc_id,
            metadata
    ):
        embeddings = np.array(embeddings).astype("float32")  # 转成FAISS需要的格式

        if len(embeddings.shape) == 1:
            embeddings = embeddings.reshape(1, -1)

        self.texts.extend(texts)

        # 索引范围
        ids = np.array(
            chunk_ids
        )

        documents = []

        for i, text in zip(ids, texts):
            documents.append(
                {
                    "chunk_id": int(i),
                    "text": text
                }
            )

        self.bm25.add_documents(
            documents
        )

        self.bm25.rebuild()

        # index 添加向量和显式索引
        self.index.add_with_ids(
            embeddings,
            ids
        ) # 存入 list[list[float]] 和 list[int]，每个向量对应一个序号
        for i, text in zip(ids, texts):
            # 使用字典，data[i]（i唯一）存放信息
            self.data[int(i)] = {
                "text": text,
                "doc_id": doc_id,
                "chunk_id": int(i),
                "metadata": metadata
            }

    def search(self, query_embedding, top_k, filters: dict | None = None):
        query_embedding = np.array([query_embedding]).astype("float32")
        distances, indices = self.index.search(query_embedding, top_k)
        results = []
        for distance, idx in zip(distances[0], indices[0]):
            if idx == -1:
                continue
            item = self.data.get(int(idx))

            if not item:
                continue
            if filters:
                metadata = item["metadata"]
                # 逐个判断，若全为True则返回True
                matched = all(
                    metadata.get(k) == v
                    for k, v in filters.items()
                )
                if not matched:
                    continue

            results.append({
                "chunk_id": int(idx),
                "text": item["text"],
                "doc_id": item["doc_id"],
                "score": float(distance),
                "metadata": item["metadata"],
                "source": "faiss"
            })

        return results

    def save(self, kb_path):
        faiss.write_index(self.index, f"{kb_path}/faiss.index")
        with open(f"{kb_path}/texts.pkl", "wb") as f:
            pickle.dump({
                "data": self.data,
                "next_id": self.next_id
            }, f)
        self.bm25.save(kb_path)

    def load(self, index_path, texts_path, kb_path):
        if os.path.exists(index_path):
            self.index = faiss.read_index(index_path)

        if os.path.exists(texts_path):
            with open(texts_path, "rb") as f:
                obj = pickle.load(f)
                self.data = obj["data"]
                self.next_id = obj["next_id"]
        # 恢复 texts
        self.texts = [item["text"] for item in self.data.values()]

        # 重建 BM25
        bm25_path = f"{kb_path}/bm25.pkl"

        if os.path.exists(bm25_path):
            self.bm25.load(kb_path)

        else:
            if self.data:
                documents = []

                for chunk_id, item in self.data.items():
                    documents.append(
                        {
                            "chunk_id": int(chunk_id),
                            "text": item["text"],
                        }
                    )

                self.bm25.add_documents(
                    documents
                )

                self.bm25.rebuild()

                self.bm25.save(
                    kb_path
                )

    def delete(self, doc_id, kb_path):
        ids = []
        for chunk_id, item in self.data.items():
            if item["doc_id"] == doc_id:
                ids.append(chunk_id)
        if not ids:
            return False
        # 一次性删除FAISS的内容
        ids_array = np.array(ids).astype("int64")
        self.index.remove_ids(ids_array)
        # 循环删除text的内容
        for chunk_id in ids:
            self.data.pop(chunk_id, None)  # None: chunk_id不存在时不报错

        self.texts = [
            item["text"]
            for item in self.data.values()
        ]
        if self.texts:
            self.bm25.corpus = {
                chunk_id: item["text"]
                for chunk_id, item in self.data.items()
            }
            self.bm25.rebuild()
            self.bm25.save(kb_path)

        # 保存索引
        self.save(kb_path)
        return True
