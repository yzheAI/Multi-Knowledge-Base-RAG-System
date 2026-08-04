from abc import ABC, abstractmethod


class BaseRetriever(ABC):
    """
    定义统一规范，不进行实际检索
    提前发现错误
    """
    @abstractmethod
    def retrieve(
            self,
            db,
            query: str,
            kb_name: str,
            owner_id: int,
            top_k: int = 5,
            filters: dict | None = None
    ) -> list[dict]:
        pass
