class RetrieverAdapter:
    def __init__(self, retriever):
        self.retriever = retriever

    def search(
            self,
            db,
            query,
            kb_name,
            top_k=5,
            filters=None
    ):

        return self.retriever.retrieve(
            db=db,
            query=query,
            kb_name=kb_name,
            top_k=top_k,
            filters=filters
        )
