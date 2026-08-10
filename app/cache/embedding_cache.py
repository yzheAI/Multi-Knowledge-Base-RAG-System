import hashlib
import json
from app.core.redis import redis_client
import numpy as np


class EmbeddingCache:
    PREFIX = "embedding:"  # Redis Key 前缀

    # 根据输入文本，生成 Redis 缓存 key
    def _make_key(self, text):
        # 压缩text为32位字符串
        md5 = hashlib.md5(
            text.encode("utf-8")
        ).hexdigest()

        return self.PREFIX + md5

    # 读出缓存
    def get(self, text):
        key = self._make_key(text)

        value = redis_client.get(key)

        if value:
            return np.array(
                json.loads(value),
                dtype="float32"
            )

        return None

    # 写缓存，过期时间一天
    def set(
            self,
            text,
            embedding,
            expire=86400
    ):

        key = self._make_key(text)

        redis_client.set(
            key,
            json.dumps(
                embedding.tolist()
            ),
            ex=expire,
        )


