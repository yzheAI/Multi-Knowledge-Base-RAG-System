from app.llm.qwen import chat_with_qwen


class AnswerEvaluation:

    def evaluate(
            self,
            question,
            answer,
            contexts,
            model_answer
    ):
        prompt = self.build_prompt(
            question,
            answer,
            contexts,
            model_answer
        )

        result = chat_with_qwen(
            prompt
        )

        return result

    def build_prompt(
            self,
            question,
            answer,
            contexts,
            model_answer
    ):
        prompt = f"""
        你是一个工业知识库问答质量评测器。
        请根据用户问题、参考答案、知识库上下文和模型答案，评价模型答案的质量。
        
        【用户问题】
        {question}
        
        【参考答案】
        {answer}
        
        【知识库上下文】
        {contexts}
        
        【模型答案】
        {model_answer}

        评价以下三个指标：

        1. correctness
        判断模型答案是否与参考答案表达的事实一致。
        如果答案存在事实错误、遗漏关键内容或与参考答案明显冲突，应降低评分。

        2. faithfulness
        判断模型答案中的信息是否能够从知识库上下文中得到支持。
        如果模型加入上下文中没有出现的事实，应降低评分。

        3. relevance
        判断模型答案是否直接回答了用户的问题，
        如果包含大量无关信息、偏离问题或没有解决用户的问题，应降低评分。

        每项评分范围为 1~5：

        1：完全不符合
        2：较差
        3：部分符合
        4：基本符合
        5：完全符合

        请严格输出 JSON：

        {{
            "correctness": 1, 
            "faithfulness": 1, 
            "relevance": 1, 
            "reason": {{ 
                "correctness": "说明正确性评分理由", 
                "faithfulness": "说明忠实性评分理由", 
                "relevance": "说明相关性评分理由" 
            }} 
        }}
         
        要求： 
        1. 三个评分必须是 1~5 的整数。 
        2. 评分必须结合提供的参考答案和知识库上下文。 
        3. 不要因为模型答案写得详细就提高评分。 
        4. 如果模型答案包含知识库上下文无法支持的信息，应降低 faithfulness。 
        5. 除 JSON 外不要输出任何其他内容。
        6. JSON 字符串中的反斜杠必须进行合法 JSON 转义。
        7. 不要在 JSON 字符串中输出无法解析的转义字符。
        """

        return prompt
