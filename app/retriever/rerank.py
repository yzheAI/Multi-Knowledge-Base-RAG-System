import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from app.config import RERANK_MODEL_PATH, DEVICE

# 全局变量，懒加载
rerank_model = None
tokenizer = None


def get_rerank_model():

    global rerank_model, tokenizer

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

    scores = []
    # 禁止梯度计算
    with torch.no_grad():

        for q, text in pairs:

            inputs = tokenizer(
                q,
                text,
                padding=True,
                truncation=True,
                return_tensors="pt"
            )
            # 放到设备
            inputs = {
                k: v.to(DEVICE)
                for k, v in inputs.items()
            }
            # 模型预测
            outputs = model(**inputs)
            # 模型输出取 score
            score = outputs.logits[0].item()

            scores.append(score)
    # 保存分数
    for i, score in enumerate(scores):
        docs[i]["rerank_score"] = float(score)

    docs = sorted(
        docs,
        key=lambda x: x["rerank_score"],
        reverse=True
    )

    return docs[:top_k]
