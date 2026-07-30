import faiss
import numpy as np
import os
from app.bm25.bm25 import BM25Store
from app.crud import chunk_crud


# 封装FAISS，实现 存向量+存原文+搜相似文本
class VectorStore:

    def __init__(self, dim: int):
        # IDMap 包装，只管理 index 和 bm25
        base_index = faiss.IndexFlatIP(dim)
        self.index = faiss.IndexIDMap(base_index)

        self.bm25 = BM25Store()

    # 添加文本与向量
    def add(
            self,
            embeddings,
            texts,
            chunk_ids,
    ):
        embeddings = np.array(
            embeddings
        ).astype("float32")  # 转成FAISS需要的格式

        if len(embeddings.shape) == 1:
            embeddings = embeddings.reshape(1, -1)

        # 索引范围
        ids = np.array(
            chunk_ids
        ).astype("int64")

        # index 添加向量和显式索引
        self.index.add_with_ids(
            embeddings,
            ids
        )  # 存入 list[list[float]] 和 list[int]，每个向量对应一个序号

        # 存入documents，方便传入bm25
        documents = [
            {
                "chunk_id": int(i),
                "text": text
            }
            for i, text in zip(ids, texts)
        ]

        self.bm25.add_documents(documents)

    def search(
            self,
            query_embedding,
            top_k,
    ):
        query_embedding = np.array(
            [query_embedding]
        ).astype("float32")

        distances, indices = self.index.search(
            query_embedding,
            top_k
        )

        results = []

        for distance, idx in zip(
                distances[0],
                indices[0]
        ):
            if idx == -1:
                continue

            results.append({
                "chunk_id": int(idx),
                "score": float(distance),
                "source": "faiss"
            })

        return results

    def save(
            self,
            kb_path
    ):
        faiss.write_index(
            self.index,
            f"{kb_path}/faiss.index"
        )

        self.bm25.save(kb_path)

    def load(
            self,
            index_path,
            kb_id,
            db
    ):
        self.bm25 = BM25Store()  # 初始化bm25，防止多次load
        if os.path.exists(index_path):

            self.index = faiss.read_index(
                index_path
            )

        documents = []
        # 从数据库获取 chunks
        chunks = chunk_crud.get_all_chunks_by_kb(
            db,
            kb_id
        )

        for chunk in chunks:
            documents.append({
                "chunk_id": chunk.id,
                "text": chunk.content
            })

        if documents:
            self.bm25.add_documents(documents)

    def delete(
            self,
            chunk_ids,
            kb_path,
    ):

        ids_array = np.array(
            chunk_ids
        ).astype("int64")

        self.index.remove_ids(ids_array)

        self.bm25.delete_documents(
            chunk_ids
        )
        # 保存索引
        self.save(kb_path)
        return True
