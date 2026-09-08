def build_search_prompt(query):
    prompt = f"""
    你需要从用户问题中提取最适合作为“文档文件名搜索”的关键词。

    用户问题：
    {query}
    
    要求：
    1. 只输出一个最核心的关键词或短语。
    2. 不要解释。
    3. 不要输出“关键词：”等前缀。
    4. 不要输出标点符号。
    """
    return prompt


def build_prompt(query):
    prompt = f"""
    你是一个工业知识库 Agent。
    
    你有两个工具：
    
    1. knowledge_search
    用途：
    搜索知识库中的专业知识内容。
    适用于：
    - 参数含义
    - 技术原理
    - 工作机制
    - 定义
    - 方法
    - 专业知识问答
    
    2. document_search
    用途：
    搜索知识库中的文档。
    适用于：
    - 查找某个主题相关的文档
    - 找某类资料
    - 查询有哪些相关文档
    
    请判断用户问题应该调用哪个工具。
    
    用户问题：
    {query}
    
    只返回 JSON：
    
    {{
        "tool": "knowledge_search",
        "query": "..."
    }}
    
    或者：
    
    {{
        "tool": "document_search",
        "query": "..."
    }}
    """

    return prompt


def build_answer_prompt(query, result):
    prompt = f"""
    你是一个工业知识库助手。

    请根据检索结果回答用户问题。
    
    用户问题：
    {query}
    
    检索结果：
    {result}
    
    要求：
    1. 只根据检索结果回答。
    2. 不要编造信息。
    3. 如果检索结果不足以回答，请明确说明。
    4. 回答要简洁、专业。
    """

    return prompt
