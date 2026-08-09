from app.query.rewrite import rewrite_query
from app.prompts.history_builder import build_history


def rewrite_adapter(item):

    history = item["history"]

    query = item["question"]

    new_query = rewrite_query(
            query,
            history
    )

    return new_query

