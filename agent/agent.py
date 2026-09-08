from agent.prompt import build_prompt, build_answer_prompt
from app.llm.qwen import chat_with_qwen
from agent.tools import knowledge_search, document_search
import json


def run_agent(
        db,
        query,
        owner_id,
        kb_name,
        filters=None
):
    prompt = build_prompt(
        query
    )

    decision = chat_with_qwen(
        prompt
    )

    decision = json.loads(decision)

    tool = decision["tool"]

    agent_query = decision["query"]

    if tool == "knowledge_search":

        result = knowledge_search(
            db,
            agent_query,
            kb_name,
            owner_id,
            filters
        )

    elif tool == "document_search":
        result = document_search(
            db,
            agent_query,
            kb_name,
            owner_id
        )

    else:
        raise ValueError("Unknown tool")

    answer_prompt = build_answer_prompt(
        query,
        result
    )

    answer = chat_with_qwen(
        answer_prompt
    )

    return answer
