from app.core.redis import redis_client
import hashlib
import json


class RetrievalCache:
    PREFIX = "retrieval:"

    def _make_key(
            self,
            owner_id,
            kb_id,
            query,
            filters
    ):
        payload = {
            "query": query,
            "filters": filters,
        }

        query_hash = hashlib.md5(
            json.dumps(
                payload,
                sort_keys=True,
                ensure_ascii=False,
            ).encode("utf-8")
        ).hexdigest()

        return (
            f"{self.PREFIX}"
            f"{owner_id}:"
            f"{kb_id}:"
            f"{query_hash}"
        )

    def get(
            self,
            owner_id,
            kb_id,
            query,
            filters
    ):
        key = self._make_key(
            owner_id,
            kb_id,
            query,
            filters
        )

        value = redis_client.get(key)

        if value:
            return json.loads(value)

        return None

    def set(
            self,
            owner_id,
            kb_id,
            query,
            filters,
            result,
            expire=3600
    ):
        key = self._make_key(
            owner_id,
            kb_id,
            query,
            filters
        )

        redis_client.set(
            key,
            json.dumps(result),
            ex=expire,
        )

    def delete_by_kb(
            self,
            owner_id,
            kb_id,
    ):
        pattern = (
            f"{self.PREFIX}"
            f"{owner_id}:"
            f"{kb_id}:*"
        )
        keys = []

        # 迭代器遍历分片遍历
        for key in redis_client.scan_iter(
                match=pattern
        ):
            keys.append(key)

        if keys:
            redis_client.delete(*keys)  # 批量删除多个key

        return len(keys)

