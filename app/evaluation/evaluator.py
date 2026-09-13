import json
import re


class RetrieverEvaluator:
    def __init__(
            self,
            dataset_path,
            query_func=None
    ):

        with open(dataset_path, "r", encoding="utf-8") as f:
            self.dataset = json.load(f)

        self.query_func = query_func

    @staticmethod
    def _normalize_text(text):
        """
        对文本进行轻量标准化。

        目的：
        1. 去除换行
        2. 去除多余空白
        3. 避免因为 PDF 文本解析造成的格式差异
        4. 不改变实际语义内容
        """
        if not text:
            return ""

        text = str(text)

        # 去除所有空白字符：
        # 空格、换行、制表符等
        text = re.sub(r"\s+", "", text)

        return text

    @staticmethod
    def _char_ngrams(text, n=3):
        """
        将文本切分成连续的 n 字符片段。
        例如：
        text = "MD10715"
        n=3：
        MD1
        D10
        107
        071
        715
        """
        if len(text) < n:
            return {text}

        return {
            text[i:i + n]
            for i in range(len(text) - n + 1)
        }

    def _evidence_overlap(
            self,
            result_text,
            expected_text
    ):
        """
        计算检索结果与 Ground Truth 的文本证据重叠程度。

        result_coverage：
            检索结果中有多少内容能够在 Ground Truth 中找到。

        expected_coverage：
            Ground Truth 中有多少内容能够在检索结果中找到。
        """

        result_text = self._normalize_text(
            result_text
        )

        expected_text = self._normalize_text(
            expected_text
        )

        if not result_text or not expected_text:
            return 0.0, 0.0

        # 完全包含
        if result_text in expected_text:
            return (
                1.0,
                len(result_text) / len(expected_text)
            )

        if expected_text in result_text:
            return (
                len(expected_text) / len(result_text),
                1.0
            )

        # n-gram 重叠
        result_ngrams = self._char_ngrams(
            result_text,
            n=3
        )

        expected_ngrams = self._char_ngrams(
            expected_text,
            n=3
        )

        if not result_ngrams or not expected_ngrams:
            return 0.0, 0.0

        overlap = (
                result_ngrams
                &
                expected_ngrams
        )

        result_coverage = (
                len(overlap)
                /
                len(result_ngrams)
        )

        expected_coverage = (
                len(overlap)
                /
                len(expected_ngrams)
        )

        return (
            result_coverage,
            expected_coverage
        )

    def _is_relevant_by_id(
            self,
            result,
            expected_chunks
    ):
        result_chunk_id = result.get(
            "chunk_id"
        )

        result_source = result.get(
            "metadata",
            {}
        ).get("source")

        for expected in expected_chunks:

            if (
                    result_chunk_id == expected.get("chunk_id")
                    and result_source == expected.get("source")
            ):
                return True

        return False

    def _is_relevant_by_text(self, result, expected_chunks):
        result_source = result.get(
            "metadata", {}
        ).get("source")

        result_text = self._normalize_text(
            result.get("text", "")
        )

        if not result_source or not result_text:
            return False

        for expected in expected_chunks:
            expected_source = expected.get(
                "source"
            )

            if result_source != expected_source:
                continue

            expected_text = self._normalize_text(
                expected.get("text", "")
            )

            if not expected_text:
                continue

            # 计算文本证据重叠
            result_coverage, expected_coverage = (
                self._evidence_overlap(
                    result_text,
                    expected_text
                )
            )

            if result_coverage >= 0.80:
                return True

            if expected_coverage >= 0.80:
                return True
        return False

    def evaluate(self, db, retriever):
        id_recall_1 = 0
        id_recall_3 = 0
        id_recall_5 = 0
        id_mrr = 0

        text_recall_1 = 0
        text_recall_3 = 0
        text_recall_5 = 0
        text_mrr = 0

        total = len(self.dataset)

        for item in self.dataset:

            query = item["question"]

            if self.query_func:
                query = self.query_func(item)

            results = retriever.search(
                db,
                query,
                kb_name=item["kb_name"],
                owner_id=17,
                top_k=5
            )

            expected_chunks = item.get(
                "relevant_chunks",
                []
            )

            # ID
            if any(
                    self._is_relevant_by_id(
                        r,
                        expected_chunks
                    )
                    for r in results[:1]
            ):
                id_recall_1 += 1

            if any(
                    self._is_relevant_by_id(
                        r,
                        expected_chunks
                    )
                    for r in results[:3]
            ):
                id_recall_3 += 1

            if any(
                    self._is_relevant_by_id(
                        r,
                        expected_chunks
                    )
                    for r in results[:5]
            ):
                id_recall_5 += 1

            for rank, r in enumerate(
                    results,
                    start=1
            ):
                if self._is_relevant_by_id(
                        r,
                        expected_chunks
                ):
                    id_mrr += 1 / rank
                    break

            # TEXT
            if any(
                    self._is_relevant_by_text(
                        r,
                        expected_chunks
                    )
                    for r in results[:1]
            ):
                text_recall_1 += 1

            if any(
                    self._is_relevant_by_text(
                        r,
                        expected_chunks
                    )
                    for r in results[:3]
            ):
                text_recall_3 += 1

            if any(
                    self._is_relevant_by_text(
                        r,
                        expected_chunks
                    )
                    for r in results[:5]
            ):
                text_recall_5 += 1

            for rank, r in enumerate(
                    results,
                    start=1
            ):
                if self._is_relevant_by_text(
                        r,
                        expected_chunks
                ):
                    text_mrr += 1 / rank
                    break

        return {
            "total": total,

            "id": {
                "recall_1": id_recall_1 / total,
                "recall_3": id_recall_3 / total,
                "recall_5": id_recall_5 / total,
                "MRR": id_mrr / total
            },

            "text": {
                "recall_1": text_recall_1 / total,
                "recall_3": text_recall_3 / total,
                "recall_5": text_recall_5 / total,
                "MRR": text_mrr / total
            }
        }
