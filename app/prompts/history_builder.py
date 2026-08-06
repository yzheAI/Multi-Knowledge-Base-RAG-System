from app.memory.conversation_memory import ConversationMemory


def build_history(messages):

    if not messages:
        return ""

    line = []

    for message in messages:
        if message.role == "user":
            role = "User"
        else:
            role = "Assistant"
        line.append(
            f"{role}: {message.content}"
        )
    return "\n".join(line)
