import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from app.config import RERANK_MODEL_PATH, DEVICE
import threading

# 全局变量，懒加载
rerank_model = None
tokenizer = None

rerank_lock = threading.Lock()


def get_rerank_model():

    global rerank_model, tokenizer

    if rerank_model is None:

        with rerank_lock:

            if rerank_model is None:

                tokenizer = AutoTokenizer.from_pretrained(
                    RERANK_MODEL_PATH,
                    use_fast=False
                )

                rerank_model = AutoModelForSequenceClassification.from_pretrained(
                    RERANK_MODEL_PATH
                )

                rerank_model.to(DEVICE)
                # 只预测不训练
                rerank_model.eval()

    return tokenizer, rerank_model


def rerank(query, docs, top_k=5):

    tokenizer, model = get_rerank_model()

    pairs = [
        (query, doc["text"])
        for doc in docs
    ]
    # 批量编码所有文本对
    inputs = tokenizer(
        pairs,
        padding=True,
        truncation=True,
        return_tensors="pt"
    )
    # 张量迁移到指定设备
    inputs = {
        k: v.to(DEVICE)
        for k, v in inputs.items()
    }

    # 禁止梯度计算
    with torch.no_grad():

        # 模型预测
        outputs = model(**inputs)
        # 模型输出取 score
        scores = outputs.logits.squeeze(-1)

    # 保存分数
    for doc, score in zip(
            docs,
            scores
    ):
        doc["rerank_score"] = float(score)

    docs = sorted(
        docs,
        key=lambda x: x["rerank_score"],
        reverse=True
    )

    return docs[:top_k]
