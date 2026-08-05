from app.memory.conversation_memory import ConversationMemory


class MemoryManager:
    def __init__(self):
        self.memories = {}

    def get_memory(
            self,
            user_id,
            kb_name
    ):
        key = (user_id, kb_name)

        if key not in self.memories:
            self.memories[key] = ConversationMemory()

        return self.memories[key]

    def clear_memory(
            self,
            user_id: int,
            kb_name: str
    ):
        key = (user_id, kb_name)

        if key in self.memories:
            del self.memories[key]
