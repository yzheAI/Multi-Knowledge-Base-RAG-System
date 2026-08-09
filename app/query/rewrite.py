from app.llm.qwen import chat_with_qwen


def need_rewrite(query):

    keywords = [
        "它",
        "这个",
        "那个",
        "上述",
        "前面",
        "该"
    ]

    return any(
        k in query
        for k in keywords
    )


def rewrite_query(
        query,
        history
):
    if not history:
        return query

    prompt = f"""
    你是一个查询优化助手。
    
    根据历史对话，将用户问题改写成适合知识库检索的完整问题。
    
    要求：
    1. 保留原意
    2. 补充省略的信息
    3. 不回答问题
    
    历史对话：
    {history}
    
    用户问题：
    {query}
    
    改写后的问题：
    """
    result = chat_with_qwen(prompt)
    return result.strip()
